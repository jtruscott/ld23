import pytality
import main
import game
import event
import world
import random
import panels
import logging
import os

log = logging.getLogger(__name__)

victory_box = None
@event.on('victory')
def on_victory():
    global victory_box
    log.debug("Victory!")
    victory_box = pytality.buffer.Box(x=main.screen_width/5, y=main.screen_height/2-6, width=main.screen_width*3/5, height=12)
    victory_box.children = [
        pytality.buffer.PlainText("YOU WIN!", y=1, center_to=victory_box.width-2, fg=pytality.colors.WHITE),
        pytality.buffer.PlainText("You defeated %i waves of enemies" % game.wave, y=4, center_to=victory_box.width-2, fg=pytality.colors.WHITE),
        pytality.buffer.PlainText("with %i lives left." % game.lives, y=5, center_to=victory_box.width-2, fg=pytality.colors.WHITE),
        pytality.buffer.PlainText("Press [C] to continue playing, or [ENTER] to exit.", y=9, center_to=victory_box.width-2, fg=pytality.colors.DARKGREY),
    ]

    game.mode = "victory"
    game.last_active_panel = game.active_panel
    game.active_panel = "victory"

@event.on('victory.draw')
def on_draw():
    victory_box.draw()

@event.on('victory.input')
def on_input(key):
    if key == 'c':
        game.active_panel = game.last_active_panel
        game.mode = "game"

        #clear everything to avoid artifacting
        panels.left_panel.draw(dirty=True)
        panels.map_panel.draw(dirty=True)
        panels.highlight_panel.draw(dirty=True)
        panels.bottom_panel.draw(dirty=True)
    elif key == 'enter':
        pytality.term.clear()
        raise game.GameShutdown()

@event.on('victory.tick')
def on_tick():
    pass
