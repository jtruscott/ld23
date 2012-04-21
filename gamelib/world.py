import event
import logging

log = logging.getLogger(__name__)

class Cell(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

map_width = 40
map_height = 40

map = [
    [
        Cell(x=x, y=y)
        for y in range(map_height)
    ]
    for x in range(map_width)
]
