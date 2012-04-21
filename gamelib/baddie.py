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


class Baddie(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

@event.on('game.input')
def on_input(key):
    if key == 'B':
        b = Baddie(x=random.randint(0, world.map_width), y=random.randint(0, world.map_height))
        start = world.get_at(b.x, b.y)
        start.baddies = [b]
        for tile in aStar(start, world.north_pole):
            tile.highlights.add('pathing_north')
            tile.calculate_image()
        
        for tile in aStar(start, world.south_pole):
            tile.highlights.add('pathing_south')
            tile.calculate_image()

        world.update_map()
        world.update_map_buffer()
