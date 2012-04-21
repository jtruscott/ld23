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
        panel.children = (panel.enabled_box, panel.enabled_title, panel.core)
    else:
        panel.children = (panel.disabled_box, panel.disabled_title, panel.core)
    return panel

def make_option_label(name, value, active=False, selected=False, **kwargs):
    class Label( pytality.buffer.RichText):
        def set_active(self, active=None, selected=None):
            if active is not None:
                self.active = active
            else:
                active = self.active
            if selected is not None:
                self.selected = selected
            else:
                selected = self.selected

            color = "LIGHTGREY"
            l,r = " ", " "
            if active:
                color = "WHITE"
            if selected:
                l,r = "(", ")"
    
            self.format((color, l, r))

    panel = Label("<%s>%s" + name + "%s</>", **kwargs)
    panel.active = active
    panel.selected = selected
    panel.set_active(active)

    panel.value = value
    return panel

highlight_buffer = pytality.buffer.Buffer(0, 0)
bottom_buffer = pytality.buffer.Buffer(0, 0)

left_panel = make_panel('left', width=main.screen_width - world.view_width - 4, height=main.screen_height-44,  core=pytality.buffer.Buffer(0, 0), title="Left!")
map_panel = make_panel('map', x=left_panel.width, width=world.view_width, height=world.view_height,  core=world.map_buffer, title="Game Map", active=True)
highlight_panel = make_panel('highlight', x=left_panel.width, y=map_panel.height, height=main.screen_height - map_panel.height-2, width=map_panel.width-2, core=highlight_buffer, title="Highlighting")
bottom_panel = make_panel('bottom', y=left_panel.height, width=main.screen_width - world.view_width - 4, height=40,  core=bottom_buffer, title="Bottom!")

status_bar = pytality.buffer.PlainText("X: %-4i    Y: %-4i    Time: %s", y=bottom_panel.height-3, x=bottom_panel.width-37)
bottom_buffer.children.append(status_bar)

@event.on('setup')
def on_setup():
    highlight_buffer.children = [
        make_option_label("Tower Range", "tower", x=2, y=0, selected=True),
        make_option_label("Enemy Pathfinding", "pathfinding", x=highlight_panel.width-23),
        make_option_label("Thing", "thing", x=2, y=2),
    ]
    highlight_panel.child_index = None

@event.on('game.predraw')
def on_predraw():
    x,y = world.cursor_pos()
    cursor_cell = world.get_at(x, y)

    #overlay the cursor
    #(next draw cell.cell will get overwritten anyway)
    n,e,w,s = cursor_cell.neighbors()
    n.cell[2] = '\xc2'
    e.cell[2] = '\xb4'
    s.cell[2] = '\xc1'
    w.cell[2] = '\xc3'

    #update status bar
    t = '%3i:%02i' % divmod(game.ticks/game.fps, 60)
    status_bar.format((x, y, t))

@event.on('game.draw')
def on_draw():
    left_panel.draw()
    map_panel.draw()
    highlight_panel.draw()
    bottom_panel.draw()

@event.on('game.input')
def on_input(key):
    if key == '\t':
        neighbors= dict(
            left=(left_panel, map_panel),
            map=(map_panel, highlight_panel),
            highlight=(highlight_panel, bottom_panel),
            bottom=(bottom_panel, left_panel),
        )

        current, next = neighbors[game.active_panel]

        activate = next
        deactivate = current

        game.active_panel = activate.name

        activate.children = (activate.enabled_box, activate.enabled_title, activate.core)
        activate.dirty = True

        deactivate.children = (deactivate.disabled_box, deactivate.disabled_title, deactivate.core)
        deactivate.dirty = True

        if activate.name == 'highlight':
            activate.child_index = 0
            highlight_buffer.children[0].set_active(active=True)

    elif game.active_panel == 'highlight':
        if key in ('left', 'right', 'up', 'down', ' ', 'enter'):
            highlight_input(key)


def highlight_input(key):
    if key in ('left', 'up'):
        highlight_buffer.children[highlight_panel.child_index].set_active(active=False)
        highlight_panel.child_index = max(highlight_panel.child_index-1, 0)
        highlight_buffer.children[highlight_panel.child_index].set_active(active=True)
        
    if key in ('right', 'down'):
        highlight_buffer.children[highlight_panel.child_index].set_active(active=False)
        highlight_panel.child_index = min(len(highlight_buffer.children)-1, highlight_panel.child_index+1)
        highlight_buffer.children[highlight_panel.child_index].set_active(active=True)

    if key in (' ', 'enter'):
        child = highlight_buffer.children[highlight_panel.child_index]
        if child.selected:
            child.set_active(selected=False)
            game.highlights.discard(child.value)
        else:
            child.set_active(selected=True)
            game.highlights.add(child.value)

    highlight_panel.dirty = True
