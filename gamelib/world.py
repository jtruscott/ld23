import event
import logging
import pytality
import game
import random

log = logging.getLogger(__name__)

class Cell(object):
    def __init__(self, x, y, character=' ', fg=pytality.colors.LIGHTGREY, bg=pytality.colors.BLACK):
        self.x = x
        self.y = y

        self.character = character
        if x == 0 and y == 0:
            bg=pytality.colors.MAGENTA
        self.fg = fg
        self.bg = bg
        #mutable on purpose
        self.cell = [fg, bg, character]

map_width = 40
map_height = 40

map = [
    [
        Cell(x=x, y=y, character=random.choice([' ']*4 + ['\xb0']*3 + ['\xb1']))
        for x in range(map_height)
    ]
    for y in range(map_width)
]

view_width = map_width+10
view_height = map_height+10
view_x = 0
view_y = 0

map_buffer = pytality.buffer.Buffer(width=view_width, height=view_height)

def update_map_buffer():
    log.debug("update_map_buffer: view_x=%r, view_y=%r", view_x, view_y)
    rows = []
    for y in range(view_height):
        row = []
        for x in range(view_width):
            abs_x = view_x + x
            abs_y = view_y + y
            while abs_x < 0:
                abs_x += map_width
            while abs_x >= map_width:
                abs_x -= map_width

            while abs_y < 0:
                abs_y += map_height
            while abs_y >= map_height:
                abs_y -= map_height

            #log.debug("display (%r, %r) -> map (%r, %r)", x, y, abs_x, abs_y)

            cell = map[abs_y][abs_x]

            row.append(cell.cell)
        rows.append(row)

    map_buffer._data = rows
    map_buffer.dirty = True

    #log.debug("map buffer: %r", map_buffer._data)

    
update_map_buffer()

@event.on('game.input')
def world_input(key):
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

    update_map_buffer()
