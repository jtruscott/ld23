import event
import logging
import pytality
import game
import random
import math

colors = pytality.colors

Plain = ' '
Hill = '\xb0'
Mountain = '\xb1'

log = logging.getLogger(__name__)

map_width = 60
map_height = 60

view_width = map_width
view_height = map_height
view_x = 0
view_y = 0

def clamp_width(value):
    while value < 0:
        value += map_width
    while value >= map_width:
        value -= map_width
    return value

def clamp_height(value):
    while value < 0:
        value += map_height
    while value >= map_height:
        value -= map_height
    return value

def get_at(x, y):
    if y < 0 or y >= map_height:
        y = clamp_height(y)
    if x < 0 or x >= map_width:
        x = clamp_width(x)
    return map[y][x]


class Cell(object):
    def __init__(self, x, y, character=' ', fg=colors.LIGHTGREY, bg=colors.BLACK):
        self.x = x
        self.y = y

        self.character = character
        self.fg = fg
        self.bg = bg

        #mutable on purpose
        self.cell = [fg, bg, character]
        self.effects = set()

    def reset_effects(self):
        self.effects = set()

    def add_effects(self):
        pass

    def calculate_image(self, viewmode=None):
        self.cell[0] = self.fg

        if 'northpole' in self.effects:
            self.cell[1] = colors.RED
        elif 'southpole' in self.effects:
            self.cell[1] = colors.BLUE
        else:
            self.cell[1] = self.bg

        self.cell[2] = self.character

    def in_range(self, radius):
        for y in range(-radius, radius+1):
            for x in range(-radius, radius+1):
                if math.sqrt(y**2 + x**2) > radius+0.5:
                    continue
                abs_y = clamp_height(y + self.y)
                abs_x = clamp_width(x + self.x)
                #log.debug('radius: %r, %r', abs_x, abs_y)
                yield map[abs_y][abs_x]

class Pole(Cell):
    def __init__(self, ns, **kwargs):
        self.ns = ns
        if ns == 'northpole':
            kwargs['bg'] = colors.LIGHTRED
        else:
            kwargs['bg'] = colors.LIGHTBLUE

        Cell.__init__(self, **kwargs)

    def add_effects(self):
        for neighbor in self.in_range(2):
            neighbor.effects.add(self.ns)

def prettify_map(iterations):
    #make the map a little prettier
    #by taking out some jaggy bits
    #and smoothing the terrain a bit

    #after two iterations, this appears to be idempotent - which is good, as it means we can run it after expanding the world
    for iteration in range(iterations):
        for y in range(map_height):
            for x in range(map_width):
                cell = map[y][x]
                n = get_at(x, y-1)
                e = get_at(x+1, y)
                w = get_at(x-1, y)
                s =  get_at(x, y+1)
                if(n.character == e.character == w.character == s.character) and n.character != cell.character:
                    #log.debug("prettify, iteration %i, changing cell to %r", iteration, n.character)
                    cell.character = n.character

                if cell.character == Mountain:
                    for c in (n,e,w,s):
                        if c.character == Plain:
                            #log.debug("prettify, iteration %i, changing cell to Hill", iteration)
                            c.character = Hill

def update_map():
    #three passes!
    #this is kinda silly but i'd rather not have bugs from being smart
    for col in map:
        for cell in col:
            cell.reset_effects()

    for col in map:
        for cell in col:
            cell.add_effects()

    for col in map:
        for cell in col:
            cell.calculate_image()

def update_map_buffer():
    log.debug("update_map_buffer: view_x=%r, view_y=%r", view_x, view_y)
    rows = []
    for y in range(view_height):
        row = []
        for x in range(view_width):
            abs_x = clamp_width(view_x + x)
            abs_y = clamp_height(view_y + y)
            cell = map[abs_y][abs_x]

            row.append(cell.cell)
        rows.append(row)

    map_buffer._data = rows
    map_buffer.dirty = True

    #log.debug("map buffer: %r", map_buffer._data)


map = [
    [
        Cell(x=x, y=y, character=random.choice([Plain]*6 + [Hill]*4 + [Mountain]))
        for x in range(map_width)
    ]
    for y in range(map_height)
]

prettify_map(3)

map[0][0] = Pole('northpole', x=0, y=0, character='P')
map[map_height/2][map_width/2] = Pole('southpole', x=map_width/2, y=map_height/2, character='P')

map_buffer = pytality.buffer.Buffer(width=view_width, height=view_height)
update_map()
update_map_buffer()

    

@event.on('game.input')
def on_input(key):
    global view_x, view_y

    if key in ('left', 'right', 'up', 'down'):
        log.debug("moving offsets")
        if key == 'left':
            view_x -= 1
        if key == 'right':
            view_x += 1
        if key == 'up':
            view_y -= 1
        if key == 'down':
            view_y += 1

        view_x = clamp_width(view_x)
        view_y = clamp_height(view_y)

        update_map_buffer()

    if key == 'R':
        update_map()
