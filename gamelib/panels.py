import pytality

import event
import main
import game
import world

import logging

log = logging.getLogger(__name__)

def make_panel(name, x=0, y=0, width=0, height=0, core=None, title='', active=False):

    panel = pytality.buffer.Buffer(x=x, y=y, padding_x=1, padding_y=1, width=width+2, height=height+2)

    panel.name = name
    panel.core = core

    panel.enabled_box = pytality.buffer.Box(x=-1, y=-1, width=width+2, height=height+2)
    panel.disabled_box = pytality.buffer.Box(x=-1, y=-1, width=width+2, height=height+2, border_fg=pytality.colors.DARKGREY)
    panel.enabled_title = pytality.buffer.PlainText("( %s )" % title, x=(width/2 - len(title)/2 -3), y=-1, fg=pytality.colors.WHITE)
    panel.disabled_title = pytality.buffer.PlainText("  %s  " % title, x=(width/2 - len(title)/2 -3), y=-1, fg=pytality.colors.DARKGREY)

    if active:
        panel.children = (panel.core, panel.enabled_box, panel.enabled_title)
    else:
        panel.children = (panel.core, panel.disabled_box, panel.disabled_title)
    return panel

left_panel = make_panel('left', width=main.screen_width - world.view_width - 2, height=world.view_height,  core=pytality.buffer.Buffer(0, 0), title="Left!")
map_panel = make_panel('map', x=left_panel.width, width=world.view_width, height=world.view_height,  core=world.map_buffer, title="Game Map", active=True)
bottom_panel = make_panel('bottom', y=left_panel.height, width=main.screen_width-2, height=main.screen_width-left_panel.height-2,  core=pytality.buffer.Buffer(0, 0), title="Bottom!")

@event.on('game.draw')
def world_draw():
    left_panel.draw()
    map_panel.draw()
    bottom_panel.draw()

@event.on('game.input')
def world_input(key):
    neighbors= dict(
        left=(bottom_panel, left_panel, map_panel),
        map=(left_panel, map_panel, bottom_panel),
        bottom=(map_panel, bottom_panel, left_panel),
    )

    left, current, right = neighbors[game.active_panel]

    log.debug(key)
    if key == 'P':
        activate = right
        deactivate = current
    else:
        return

    game.active_panel = activate.name

    activate.children = (activate.core, activate.enabled_box, activate.enabled_title)
    activate.dirty = True

    deactivate.children = (deactivate.core, deactivate.disabled_box, deactivate.disabled_title)
    deactivate.dirty = True
