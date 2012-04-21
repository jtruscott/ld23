import pytality

import event
import world
import random
import logging

log = logging.getLogger(__name__)

class Tower(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.fire_delay = 5
        self.range = 2
        self.effect = 'tower'
        self.fg = pytality.colors.DARKGREY

    def tick(self):
        if self.fire_delay > 0:
            self.fire_delay -= 1
            self.fg = pytality.colors.DARKGREY
            return
        else:
            self.fg = pytality.colors.LIGHTGREY

        cell = world.get_at(self.x, self.y)
        for neighbor in cell.in_range(self.range):
            if neighbor.baddies:
                target = list(neighbor.baddies)[0]
                log.debug("%r firing at %r", self, target)
                self.fg = pytality.colors.LIGHTGREEN
                target.take_damage(1)
                self.fire_delay = 4
                break

all_towers = set()

@event.on('game.input')
def on_input(key):
    if key == 'T':

        t = Tower(x=random.randint(0, world.map_width), y=random.randint(0, world.map_height))
        start = world.get_at(t.x, t.y)
        start.tower = t
        all_towers.add(t)

        
@event.on('game.tick')
def on_tick():
    #can't mutate during iteration
    for tower in list(all_towers):
        tower.tick()
