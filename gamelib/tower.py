import pytality

import game
import event
import world
import random
import logging

log = logging.getLogger(__name__)

class Tower(object):
    name = "?"
    build_name = "?"
    base_damage = 1
    base_range = 1
    base_cooldown = 90

    range_increment = 1
    range_cost = [100]
    damage_increment = 1
    damage_cost = [100]
    cooldown_reduction = 1
    cooldown_cost = [100]

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
        self.value = self.cost * 0.8
        self.kills = 0

        #don't want to update the class here
        self.range_cost = self.range_cost[:]
        self.damage_cost = self.damage_cost[:]
        self.cooldown_cost = self.cooldown_cost[:]

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
    def upgrade_cost(self, upgrade_type):
        r = dict(damage=self.damage_cost, range=self.range_cost, speed=self.cooldown_cost)[upgrade_type]
        if r:
            return r[0]
        else:
            return None

    def upgrade(self, upgrade_type):
        cost = None
        if upgrade_type == 'damage' and self.damage_cost:
            cost = self.damage_cost.pop(0)
            self.damage += self.damage_increment


        if upgrade_type == 'range' and self.range_cost:
            cost = self.range_cost.pop(0)
            self.range += self.range_increment

        if upgrade_type == 'speed' and self.cooldown_cost:
            cost = self.cooldown_cost.pop(0)
            self.cooldown -= self.cooldown_reduction

        if not cost:
            return
        game.resources -= cost
        self.value += cost * 0.8


class BasicTower(Tower):
    name = "Basic Tower"
    build_name = "<WHITE>[B]</>asic Tower"
    character = "B"
    base_cooldown = 5
    base_range = 4
    base_damage = 2
    base_cost = 50

    damage_cost = range_cost = [40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90]
    cooldown_cost = [50, 100]

class LongRangeTower(Tower):
    name = "Long Range Tower"
    build_name = "<WHITE>[L]</>ong Range Tower"
    character = "L"
    base_cooldown = 5
    base_range = 8
    base_damage = 1
    base_cost = 75

    damage_cost = [75, 80, 85, 90, 95, 100, 105, 110, 115, 120]
    range_cost = [50, 55, 60, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120]
    cooldown_cost = [75, 100, 125]

class RapidFireTower(Tower):
    name = "Rapid Fire Tower"
    build_name = "<WHITE>[R]</>apid Fire Tower"
    character = "R"
    base_cooldown = 3
    base_range = 3
    base_damage = 2
    base_cost = 75
    damage_cost = [100, 105, 110, 115, 120, 125, 130, 135, 140, 150]
    range_cost = [100, 110, 120, 130, 140]
    cooldown_cost = [150]

class SniperTower(Tower):
    name = "Sniper Tower"
    build_name = "<WHITE>[S]</>niper Tower"
    character = "S"
    base_cooldown = 20
    base_range = 10
    base_damage = 13
    base_cost = 200

    damage_increment = 2
    cooldown_reduction = 2
    damage_cost = cooldown_cost = range_cost = [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]

tower_types = (BasicTower, LongRangeTower, RapidFireTower, SniperTower)

all_towers = set()

@event.on('game.input')
def on_input(key):
    x,y = world.cursor_pos()
    current_cell = world.get_at(x, y)
    if current_cell.tower:
        tower = current_cell.tower
        if key == '$':
            current_cell.tower = None
            all_towers.discard(tower)

            game.resources += tower.value
            event.fire("message", "Tower sold!")
            return

        if key in "drs":
            if key == "d":
                cost = tower.upgrade_cost("damage")
            elif key == "r":
                cost = tower.upgrade_cost("range")
            elif key == "s":
                cost = tower.upgrade_cost("speed")
            else:
                return
            
            if cost > game.resources:
                event.fire("error", "Cannot upgrade tower:\nInsufficient resources")
                return
            if key == "d":
                tower.upgrade("damage")
                event.fire("message", "Tower Damage upgraded!")
            elif key == "r":
                tower.upgrade("range")
                event.fire("message", "Tower Range upgraded!")
            elif key == "s":
                tower.upgrade("speed")
                event.fire("message", "Tower Speed upgraded!")

    elif current_cell.buildable:
        if key in "blrs":

            if key == 'b':
                tower_type = BasicTower
            elif key == "l":
                tower_type = LongRangeTower
            elif key == "r":
                tower_type = RapidFireTower
            elif key == "s":
                tower_type = SniperTower

            if game.resources < tower_type.base_cost:
                event.fire("error", "Cannot construct tower:\nInsufficient resources")
                return

            game.resources -= tower_type.base_cost

            tower = tower_type(x=x, y=y)
            current_cell.tower = tower
            all_towers.add(tower)

    else:
        if key in "blrs":
            event.fire("error", "Cannot construct tower:\nCell is not buildable")
            return

        
@event.on('game.tick')
def on_tick():
    #can't mutate during iteration
    for tower in list(all_towers):
        tower.tick()
