import pytality

import game
import event
import world
import random
import logging

log = logging.getLogger(__name__)

class Tower(object):
    name = "?"
    base_cooldown = 90
    base_range = 1

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.effect = 'tower'
        self.fg = pytality.colors.DARKGREY

        self.cooldown = self.base_cooldown
        self.range = self.base_range
        self.damage = self.base_damage

        self.fire_delay = self.cooldown
        self.cost = self.base_cost
        self.kills = 0

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
                log.debug("%r firing at %r on tick %r", self, target, game.ticks)
                self.fg = pytality.colors.LIGHTGREEN
                killed = target.take_damage(self.damage)
                if killed:
                    self.kills += 1

                self.fire_delay = self.cooldown
                break

class BasicTower(Tower):
    name = "Basic Tower"
    base_cooldown = 5
    base_range = 2
    base_damage = 2
    base_cost = 50


class LongRangeTower(Tower):
    name = "Long Range Tower"
    base_cooldown = 5
    base_range = 6
    base_damage = 1
    base_cost = 75

all_towers = set()

@event.on('game.input')
def on_input(key):
    if key in ('T', 'Y'):
        x,y = world.cursor_pos()
        start = world.get_at(x, y)
        if start.tower:
            event.fire("error", "Cannot construct tower: Cell already has a tower")
            return

        if key == 'T':
            tower_type = BasicTower
        else:
            tower_type = LongRangeTower

        if game.money < tower_type.base_cost:
            event.fire("error", "Cannot construct tower: Insufficient resources")
            return
        if not start.buildable:
            event.fire("error", "Cannot construct tower: Cell is not buildable")
            return

        game.money -= tower_type.base_cost

        tower = tower_type(x=x, y=y)
        start.tower = tower
        all_towers.add(tower)

        
@event.on('game.tick')
def on_tick():
    if game.ticks % 10 == 0:
        game.money += 1

    #can't mutate during iteration
    for tower in list(all_towers):
        tower.tick()
