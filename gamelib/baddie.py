import heapq
import event
import world
import pytality
import random
import game
import logging
import math

log = logging.getLogger(__name__)

PodBeacon = '\x04'
Pod1 = '\x99'
Pod2 = '\x94'
Pod3 = '\x0F'

#yay toruses!
def xdistance(a,b):
    small = min(a,b)
    large = max(a,b)
    d1 = abs(a-b)
    d2 = small + (world.map_width-large)
    return min(d1, d2)

def ydistance(a,b):
    small = min(a,b)
    large = max(a,b)
    d1 = abs(a-b)
    d2 = small + (world.map_height-large)
    return min(d1, d2)

def distance_in(x, y, target, maximum):
    dy = ydistance(y, target.y)
    dx = xdistance(x, target.x)
    return math.sqrt(dy**2 + dx**2) <= maximum+0.5


#http://stackoverflow.com/questions/4159331/python-speed-up-an-a-star-pathfinding-algorithm
def aStar(current, end, mover):

    openSet = set()
    openHeap = []
    closedSet = set()

    #super arbitrary
    terrainCosts = {
        world.Plain: 0,
        world.Hill: 6,
        world.Mountain: 12
    }

    #cutoff the path ends
    current.parent = None
    end.parent = None


    def retracePath(c):
        path = [c]
        while c.parent is not None:
            c = c.parent
            path.append(c)
        path.reverse()
        return path

    openSet.add(current)
    openHeap.append((0,current))
    while openSet:
        current = heapq.heappop(openHeap)[1]
        if current == end:
            return retracePath(current)
        openSet.remove(current)
        closedSet.add(current)
        for tile in current.neighbors():
            if tile not in closedSet:
                tile.parent = current
                tile.H = (xdistance(end.x, tile.x)+ydistance(end.y, tile.y))*10 
                terrainCost = 0
                cc = tile
                while cc.parent is not None:
                    if cc.character in terrainCosts:
                        terrainCost += terrainCosts[cc.character]
                    if 'tower' in cc.effects:
                        terrainCost += mover.tower_avoidance
                    if cc.tower:
                        #don't go over towers, but don't call them full on walls
                        terrainCost += 1000
                    cc = cc.parent

                tile.H += terrainCost

                if tile not in openSet:
                    openSet.add(tile)
                    heapq.heappush(openHeap, (tile.H,tile))
    return []


all_baddies = set()
all_landers = set()

min_distance = 20

class Lander(object):
    def __init__(self, x, y, hp, children=None):
        self.x = x
        self.y = y
        self.hp = hp
        self.children = children
        if children:
            self.delay = 20
            self.character = PodBeacon
            self.child_delays = [random.randint(0, 10) for i in range(children)]
        else:
            self.delay = 11
            self.character = None

    def tick(self):
        self.delay -= 1
        if self.delay == 10:
            self.character = Pod1
        elif self.delay == 6:
            self.character = Pod2
        elif self.delay == 2:
            self.character = Pod3
        elif self.delay <= 0:
            #landed!
            spawn_at(self.x, self.y, self.hp)
            all_landers.discard(self)
        
        if self.children:
            root_cell = world.get_at(self.x, self.y)

            possible_spots = [cell for cell in root_cell.in_range(5) if (
                    cell is not root_cell
                    and not cell.tower
                    and not distance_in(cell.x, cell.y, world.north_pole, min_distance)
                    and not distance_in(cell.x, cell.y, world.south_pole, min_distance)
                )
            ]

            for child_delay in self.child_delays:
                if child_delay == self.delay:
                    #spawn a child on a random neighbor
                    i = random.randint(0, len(possible_spots)-1)
                    spot = possible_spots.pop(i)
                    log.debug("landing child at x=%r, y=%r", spot.x, spot.y)

                    lander = Lander(spot.x, spot.y, self.hp)
                    all_landers.add(lander)
                


class Baddie(object):
    speed = 5-1
    def __init__(self, x, y, hp):
        self.x = x
        self.y = y
        self.health = hp
        self.move_delay = 2

        self.tower_avoidance = random.randint(0,4)
        
        self.dead = False

    def set_path(self, path):
        self.full_path = path
        self.path = path[:]
        for tile in path:
            tile.in_path_of.add(self)
            tile.highlights.add('pathfinding')

    def move(self):
        if self.dead:
            return

        self.move_delay -= 1
        if self.move_delay > 0: 
            return


        leaving = self.path.pop(0)
        leaving.in_path_of.discard(self)
        leaving.baddies.discard(self)
        
        self.move_delay = self.speed
        if leaving.character == world.Hill:
            self.move_delay += 3
        if leaving.character == world.Mountain:
            self.move_delay += 6


        if len(self.path) <= 1:
            log.debug("got to the target with %r hp", self.health)
            all_baddies.discard(self)
            life_cost = 1 + (game.wave/6)
            game.lives -= life_cost
            event.fire('error', "%i Li%s Lost!" % (life_cost, "fe" if life_cost == 1 else "ves"))
            return

        current = self.path[0]
        current.baddies.add(self)

    def take_damage(self, amount):
        if self.dead:
            return

        self.health -= amount
        if self.health <= 0:
            log.debug("%r was killed by %r damage", self, amount)
            #dead!
            self.dead = True

            #cleanup our pathing
            self.path[0].baddies.discard(self)
            for tile in self.path:
                tile.in_path_of.discard(self)

            self.full_path = self.path = None
            all_baddies.discard(self)
            game.resources += 5
            return True
        

def spawn_at(x, y, hp):
    b = Baddie(x=x, y=y, hp=hp)
    
    start = world.get_at(b.x, b.y)
    start.baddies.add(b)
    paths = []
    for target in (world.north_pole, world.south_pole):
        path = aStar(start, target, b)
        paths.append((len(path), path))

    #head down the shorter path
    b.set_path(sorted(paths)[0][1])
    
    all_baddies.add(b)


@event.on('game.input')
def on_input(key):
    if key == '\x1b' and game.wave_delay:
        event.fire("message", "Skipping wave timer.")
        game.wave_delay = 1

@event.on('game.tick')
def on_tick():
    if game.growings:
        game.growings -= 1
        world.grow_map()
        world.cursor_slop_x += 1
        world.cursor_slop_y += 1
        if not game.growings:
            world.cursor_slop_x = 0
            world.cursor_slop_y = 0
            game.wave_delay =  game.fps * 60
        return
    if game.wave_delay:
        game.wave_delay -= 1
        if not game.wave_delay:
            event.fire('game.nextwave')
        return

    if not all_landers and not all_baddies:
        reward = 10*(game.wave+9)
        game.resources += reward
        event.fire('message', "Wave Complete! <YELLOW>+$%i</>" % reward)
        if game.wave < 5:
            event.fire('message', "The world begins to grow.")
        if game.wave % 6 == 0:
            event.fire('message', "The world is growing faster.")
        game.growings = 1 + (game.wave/6)
        return

    for lander in list(all_landers):
        lander.tick()

    #can't mutate during iteration
    for baddie in list(all_baddies):
        baddie.move()



@event.on('game.predraw')
def on_predraw():
    for lander in all_landers:
        cell = world.get_at(lander.x, lander.y)
        if lander.character:
            cell.cell[2] = lander.character
            if game.wave_type == 'Swarm':
                cell.cell[0] = pytality.colors.LIGHTMAGENTA
            elif game.wave_type == 'Cluster':
                cell.cell[0] = pytality.colors.YELLOW
            else:
                cell.cell[0] = pytality.colors.LIGHTCYAN

@event.on('game.nextwave')
def on_nextwave():
    game.calc_next_wave()

    wave = game.wave
    landers = game.wave_landers
    units = game.wave_units
    hp = game.wave_hp

    existing_clusters = []
    for cluster in range(landers):
        for _ in range(30):
            x = random.randint(0, world.map_width)
            y = random.randint(0, world.map_height)
            if distance_in(x, y, world.north_pole, min_distance) or distance_in(x, y, world.south_pole, min_distance):
                continue
            for existing in existing_clusters:
                if distance_in(x, y, existing, min_distance/2):
                    continue

            current = world.get_at(x, y)
            if current.tower:
                #there's a tower there? shift over one. might put us slightly too close. whatever.
                chosen = random.choice(current.neighbors)
                x,y = chosen.x, chosen.y
            break

        #if it didn't find anything we still have an x/y, it's just kinda cheating, but failing 30 tries is absurd
        log.debug("landing at x=%r, y=%r after %r tries", x, y, _)

        lander = Lander(x, y, hp=hp, children=units-1)
        all_landers.add(lander)
    
    
