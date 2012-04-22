import pytality

import event
import main
import game
import world
from tower import tower_types

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

highlight_buffer = pytality.buffer.Buffer(0, 0)
info_buffer = pytality.buffer.Buffer(width=main.screen_width - world.view_width - 4, height=main.screen_height-42)
bottom_buffer = pytality.buffer.Buffer(width=main.screen_width - world.view_width - 4, height=36)

left_panel = make_panel('left', width=main.screen_width - world.view_width - 4, height=main.screen_height-40,  core=info_buffer, title="Info")
map_panel = make_panel('map', x=left_panel.width, width=world.view_width, height=world.view_height,  core=world.map_buffer, title="Game Map", active=True)
highlight_panel = make_panel('highlight', x=left_panel.width, y=map_panel.height, height=main.screen_height - map_panel.height-2, width=map_panel.width-2, core=highlight_buffer, title="Hotkeys")
bottom_panel = make_panel('bottom', y=left_panel.height, width=bottom_buffer.width, height=bottom_buffer.height, core=bottom_buffer, title="Current Cell")

info_text = pytality.buffer.RichText("%s", x=1, y=0, wrap_to=info_buffer.width-1)

message_log = pytality.buffer.MessageBox(draw_top=None, draw_left=None, draw_bottom=None, draw_right=None, x=0, y=left_panel.height-20, width=info_buffer.width, height=18)
message_title = pytality.buffer.PlainText('Messages:', x=0,y=message_log.y)
message_log.scroll_cursor = pytality.buffer.NoScrollbar()

cell_special_text = pytality.buffer.RichText("%s", x=1, y=1, wrap_to=bottom_buffer.width-1)
cell_terrain_text = pytality.buffer.RichText("<DARKGREY>Terrain Type: %s</>", x=1, y=3, wrap_to=bottom_buffer.width-1)
cell_tower_text = pytality.buffer.RichText("<DARKGREY>Tower: %s</>%s", x=1, y=5, wrap_to=bottom_buffer.width-1)
cell_tower_info = pytality.buffer.RichText("%s", x=1, y=7, wrap_to=bottom_buffer.width-1)

status_bar = pytality.buffer.PlainText("X: %-4i    Y: %-4i    Time: %s", y=bottom_panel.height-3, x=bottom_panel.width-37)


highlight_range = True
highlight_pathfinding = False
@event.on('error')
def on_error(msg):
    message_log.add('<RED>%s</>' % msg)

@event.on('message')
def on_error(msg):
    message_log.add(msg)

@event.on('setup')
def on_setup():
    info_buffer.children = [
        info_text,
        message_log,
        message_title,
    ]
    message_log.add("Game started")

    bottom_buffer.children = [
        cell_special_text,
        cell_terrain_text,
        cell_tower_text,
        cell_tower_info,
        status_bar
    ]


    highlight_buffer.children = [
        pytality.buffer.RichText("""
<WHITE>[1]</>: %s range highlights   <WHITE>[2]</>: %s pathing highlights

<WHITE>[P]</>: Cycle between poles      <WHITE>[T]</>: Cycle between towers
""", x=1, wrap_to=highlight_panel.width-3)
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

    highlight_buffer.children[0].format(("Hide" if highlight_range else "Show", "Hide" if highlight_pathfinding else "Show"))
    #update info panel

    next_wave_timer = ""
    if game.wave_delay:
        next_wave_timer = " in <WHITE>%2i:%02i</>"  % divmod(game.wave_delay/game.fps, 60)

    wave_info = ""
    if not game.wave:
        wave_info = "\n\nFirst Wave%s\n<DARKGREY>Skip countdown with <WHITE>[ESC]</></>\n" % next_wave_timer
    else:

        if game.wave_delay:
            wave_info = """
Skip countdown with <WHITE>[ESC]</>

"""
        else:
            wave_info = """
<DARKGREY>Wave <WHITE>%4i</><DARKGREY>: <WHITE>%s</>
       (<WHITE>%i</> Landers, <WHITE>%i</> Units, <WHITE>%i</> HP)</>
""" % (game.wave, game.wave_type, game.wave_landers, game.wave_units, game.wave_hp,)
        wave_info += """
<DARKGREY>Next Wave: <LIGHTGREY>%s</>%s
       (<LIGHTGREY>%i</> Landers, <LIGHTGREY>%i</> Units, <LIGHTGREY>%i</> HP)</>
""" %   (game.next_wave_type, next_wave_timer, game.next_wave_landers, game.next_wave_units, game.next_wave_hp,)

    info_text.format(("""
<BROWN>Resources: </><YELLOW>$%-8i</>
%s
<RED>Lives: </><LIGHTRED>%-4i</>
    """ % (
            game.resources,
            wave_info,
            game.lives),))

    #update current-cell panel
    if cursor_cell == world.north_pole:
        cell_special_text.format(("<LIGHTRED>North Pole",))
    elif cursor_cell == world.south_pole:
        cell_special_text.format(("<LIGHTBLUE>South Pole",))
    else:
        cell_special_text.format(('',))

    if cursor_cell.tower:
        tower = cursor_cell.tower
        cell_tower_text.format((tower.name, ''))

        upgrade_lines = []
        for upgrade_key, upgrade_type in (("R", "range"), ("D", "damage"), ("S","speed")):
            upgrade_cost = tower.upgrade_cost(upgrade_type)
            if upgrade_cost:
                if upgrade_cost < game.resources:
                    hotkey_color = "WHITE"
                    money_color = "YELLOW"
                else:
                    hotkey_color = "LIGHTGREY"
                    money_color = "BROWN"

                if upgrade_key == "S":
                    value = '%.1f' %  (float(game.fps) / (tower.cooldown - tower.cooldown_reduction))
                elif upgrade_key == "D":
                    value = tower.damage + tower.damage_increment
                else:
                    value = tower.range + tower.range_increment

                upgrade_lines.append("<DARKGREY>Upgrade <%s>[%s]</>%s to <LIGHTGREY>%s</> (<%s>$%i</>)</>" % (hotkey_color, upgrade_key, upgrade_type[1:], value, money_color, upgrade_cost))
            else:
                upgrade_lines.append("<DARKGREY>At maximum upgrade.</>")

        cell_tower_info.format("""<DARKGREY>Range:</> <LIGHTGREY>%-2i</>

<DARKGREY>Damage:</> <LIGHTGREY>%-2i</>

<DARKGREY>Speed:</> <LIGHTGREY>%-2.1f</> hits/sec


%s
%s
%s




<DARKGREY>Kills:</> %-3i

<DARKGREY>Sell Value <WHITE>[<YELLOW>$</>]</>:</> %-3i

""" % (tower.range, tower.damage, float(game.fps)/tower.cooldown, upgrade_lines[0], upgrade_lines[1], upgrade_lines[2], tower.kills, tower.value))
    else:
        if cursor_cell.buildable:
            cell_tower_text.format(("None", " (<GREEN>Buildable</>)"))
            tower_descs = ["<DARKGREY>Build:</>\n"]
            for tower_type in tower_types:
                tower_descs.append("""%s <DARKGREY>(<%s>$%i</>)
Damage: %-2i    Range: %-2i
Speed: %-1.1f hits/sec</>
""" % (tower_type.build_name, ("YELLOW" if tower_type.base_cost < game.resources else "BROWN"), tower_type.base_cost, tower_type.base_damage, tower_type.base_range,  float(game.fps)/tower_type.base_cooldown))
            cell_tower_info.format(("\n".join(tower_descs),))
        else:
            cell_tower_text.format(("None", " (<RED>Not Buildable</>)"))
            cell_tower_info.format(("                    \n"*20,))

    cell_terrain_text.format(world.cell_names.get(cursor_cell.character, 'Unknown'))
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
    global highlight_range, highlight_pathfinding
    if key == '1':
        highlight_range = not highlight_range
        if highlight_range:
            game.highlights.add('tower')
        else:
            game.highlights.discard('tower')

    elif key == '2':
        highlight_pathfinding = not highlight_pathfinding
        if highlight_pathfinding:
            game.highlights.add('pathfinding')
        else:
            game.highlights.discard('pathfinding')

    return
