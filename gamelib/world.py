import event
import logging
import pytality
import game
import random
import math
import time
log = logging.getLogger(__name__)

colors = pytality.colors

Plain = ' '
Hill = '\xb0'
Mountain = '\xb1'

terrain_weights = [Plain]*6 + [Hill]*4 + [Mountain]
highlight_colors = dict(
    pathfinding=colors.MAGENTA,
    tower=colors.GREEN
)

cell_names = {
    Plain: 'Flat',
    Hill: 'Rough',
    Mountain: 'Mountainous',
    'P': 'Flat',
}
map_width = 60
map_height = 60

view_width = map_width
view_height = map_height
view_x = 0
view_y = 0

def cursor_pos():
    return clamp_width(view_x + (view_width/2)), clamp_height(view_y + (view_height/2))

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
        self.baddies = set()

        #mutable on purpose
        self.cell = [fg, bg, character]

        self.buildable = True
        self.smoothed = False

        #what effects are going on? (must be recalculatable)
        self.effects = set()

        #what snazzy things do we want to show?
        self.highlights = set()

        #who's pathing through us? (in case we change)
        self.in_path_of = set()

        #is there a tower here?
        self.tower = None

        #what about a lander?
        self.lander = None

    def reset_effects(self):
        self.buildable = True
        self.effects = set()
        if not self.in_path_of:
            self.highlights.discard('pathfinding')

    def add_effects(self):
        if self.tower:
            for neighbor in self.in_range(self.tower.range):
                neighbor.effects.add(self.tower.effect)
                neighbor.highlights.add('tower')
            for neighbor in self.in_range(1):
                neighbor.buildable = False

    def calculate_image(self, viewmode=None):
        character = self.character
        fg = self.fg
        bg = self.bg

        for highlight in game.highlights:
            if highlight in self.highlights:
                bg = highlight_colors[highlight]
        if 'northpole' in self.effects:
            bg = colors.RED
        elif 'southpole' in self.effects:
            bg = colors.BLUE

        if self.tower:
            fg = self.tower.fg
            bg = colors.GREEN
            character = self.tower.character

        elif len(self.baddies):
            fg = colors.LIGHTCYAN
            character = 'E'

        
        self.cell[0] = fg
        self.cell[1] = bg
        self.cell[2] = character


    def in_range(self, radius):
        for y in range(-radius, radius+1):
            for x in range(-radius, radius+1):
                if math.sqrt(y**2 + x**2) > radius+0.5:
                    continue
                abs_y = clamp_height(y + self.y)
                abs_x = clamp_width(x + self.x)
                #log.debug('radius: %r, %r', abs_x, abs_y)
                yield map[abs_y][abs_x]

    def neighbors(self):
        x = self.x
        y = self.y
        return (get_at(x, y-1), get_at(x+1, y), get_at(x-1, y), get_at(x, y+1))

class Pole(Cell):
    def __init__(self, ns, **kwargs):
        self.ns = ns
        if ns == 'northpole':
            kwargs['fg'] = colors.LIGHTMAGENTA
            kwargs['bg'] = colors.LIGHTRED
        else:
            kwargs['fg'] = colors.LIGHTCYAN
            kwargs['bg'] = colors.LIGHTBLUE


        Cell.__init__(self, **kwargs)

    def add_effects(self):
        for neighbor in self.in_range(2):
            neighbor.effects.add(self.ns)
            neighbor.buildable = False


def all_cells():
    for col in map:
        for cell in col:
            yield cell

def prettify_map(iterations, lazy=False):
    #make the map a little prettier
    #by taking out some jaggy bits
    #and smoothing the terrain a bit

    #after two iterations, this appears to be idempotent - which is good, as it means we can run it after expanding the world
    for iteration in range(iterations):
        for y in range(map_height):
            for x in range(map_width):
                cell = map[y][x]
                if lazy and cell.smoothed >= iteration:
                    continue
                cell.smoothed = iteration
                n,e,w,s = cell.neighbors()
                
                #poles want to be flat ground
                #sometimes this makes them struggle against mountains, oh well
                if cell.character == 'P':
                    for neighbor in cell.in_range(2):
                        if neighbor.character in (Plain, Hill, Mountain):
                            neighbor.character = Plain

                elif(n.character == e.character == w.character == s.character) and n.character != cell.character and cell.character in (Plain, Hill, Mountain):
                    #log.debug("prettify, iteration %i, changing cell to %r", iteration, n.character)
                    cell.character = n.character

                elif cell.character == Mountain:
                    for c in (n,e,w,s):
                        if c.character == Plain:
                            #log.debug("prettify, iteration %i, changing cell to Hill", iteration)
                            c.character = Hill

def update_map():
    #three passes!
    #this is kinda silly but i'd rather not have bugs from being smart
    for cell in all_cells():
        cell.reset_effects()

    for cell in all_cells():
        cell.add_effects()

def clear_highlight(type=None):
    if not type:
        for cell in all_cells():
            cell.highlights.clear()
    else:
        for cell in all_cells():
            cell.highlights.discard(type)

def update_map_buffer():
    #log.debug("update_map_buffer: view_x=%r, view_y=%r", view_x, view_y)
    rows = []
    for y in range(view_height):
        row = []
        for x in range(view_width):
            abs_x = clamp_width(view_x + x)
            abs_y = clamp_height(view_y + y)
            cell = map[abs_y][abs_x]

            cell.calculate_image()

            row.append(cell.cell)
        rows.append(row)

    map_buffer._data = rows
    map_buffer.dirty = True

    #log.debug("map buffer: %r", map_buffer._data)


map = [
    [
        Cell(x=x, y=y, character=random.choice(terrain_weights))
        for x in range(map_width)
    ]
    for y in range(map_height)
]


north_pole = map[0][0] = Pole('northpole', x=0, y=0, character='P')
south_pole = map[map_height/2][map_width/2] = Pole('southpole', x=map_width/2, y=map_height/2, character='P')

prettify_map(3)

map_buffer = pytality.buffer.Buffer(width=view_width, height=view_height)
    
def grow_map():
    #add space to the map!
    #tiles and towers get updated. However, pathfinding is not, so this should only run between waves.
    global map_width, map_height

    new_y = random.randint(0, map_height)
    new_x = random.randint(0, map_width)
    log.debug("grow_map: new_x=%r, new_y=%r", new_x, new_y)

    start_time = time.time()
    #add the new cell to each row
    #don't worry about coordinates, we're about to reindex everything
    for row in map:
        new_cell = Cell(x=None, y=None, character=random.choice(terrain_weights))
        row.insert(new_x, new_cell)

    #add the new row
    new_row = [Cell(x=None, y=None, character=random.choice(terrain_weights))for _ in range(map_height+1)]
    map.insert(new_y, new_row)
    add_time = time.time()

    #reindex
    for y, row in enumerate(map):
        for x, cell in enumerate(row):
            #log.debug("Cell was %r,%r, reindexing as %r, %r", cell.x, cell.y, x, y)
            cell.x = x
            cell.y = y

    reindex_time = time.time()

    map_width += 1
    map_height += 1

    #smooth
    prettify_map(2, lazy=True)
    smooth_time = time.time()

    #fixup the highlights
    for cell in all_cells():
        cell.highlights.discard('tower')

    log.debug("grow_map: total took %.2f", smooth_time - start_time)
    log.debug("grow_map: add took %.2f, reindex took %.2f, smooth took %.2f", add_time - start_time, reindex_time - add_time, smooth_time - reindex_time,)


@event.on('game.input')
def on_input(key):
    global view_x, view_y

    if game.active_panel != 'map':
        return

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

@event.on('game.predraw')
def on_tick():
    
    update_map()
    update_map_buffer()
