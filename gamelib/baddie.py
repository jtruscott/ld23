import heapq
import event
import world
import pytality
import random
import logging

log = logging.getLogger(__name__)


#http://stackoverflow.com/questions/4159331/python-speed-up-an-a-star-pathfinding-algorithm
def aStar(current, end):

    openSet = set()
    openHeap = []
    closedSet = set()

    #super arbitrary
    terrainCosts = {
        world.Plain: 0,
        world.Hill: 3,
        world.Mountain: 8
    }

    #cutoff the path ends
    current.parent = None
    end.parent = None

    #yay toruses!
    def xdistance(a,b):
        small = min(a,b)
        large = max(a,b)
        d1 = abs(a-b)
        d2 = small + (world.map_width-b)
        return min(d1, d2)
    def ydistance(a,b):
        small = min(a,b)
        large = max(a,b)
        d1 = abs(a-b)
        d2 = small + (world.map_height-b)
        return min(d1, d2)

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
                    cc = cc.parent
                tile.H += terrainCost

                if tile not in openSet:
                    openSet.add(tile)
                    heapq.heappush(openHeap, (tile.H,tile))
    return []


all_baddies = set()

class Baddie(object):
    speed = 2
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 3
        self.move_delay = 2
        self.dead = False

    def set_path(self, path):
        self.full_path = path
        self.path = path[:]
        for tile in path:
            tile.in_path_of.add(self)

    def move(self):
        if self.dead:
            return

        self.move_delay -= 1
        if self.move_delay > 0: 
            return

        self.move_delay = self.speed

        leaving = self.path.pop(0)
        leaving.in_path_of.discard(self)
        leaving.baddies.discard(self)

        if len(self.path) <= 1:
            log.debug("got there!")
            all_baddies.discard(self)
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
        

@event.on('game.input')
def on_input(key):
    if key == 'B':
        b = Baddie(x=random.randint(0, world.map_width), y=random.randint(0, world.map_height))
        
        start = world.get_at(b.x, b.y)
        start.baddies.add(b)
        paths = []
        for target, highlight in ((world.north_pole, 'pathing_north'), (world.south_pole, 'pathing_south')):
            path = aStar(start, target)
            paths.append((len(path), path))
            for tile in path:
                tile.highlights.add(highlight)

        #head down the shorter path
        b.set_path(sorted(paths)[0][1])
        
        all_baddies.add(b)
        
@event.on('game.tick')
def on_tick():
    #can't mutate during iteration
    for baddie in list(all_baddies):
        baddie.move()
