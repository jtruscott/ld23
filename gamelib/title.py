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


title_screen = pytality.buffer.Buffer(width=main.screen_width, height=main.screen_height, x=0, y=0)

title_index = game.fps

title_messages = [
    pytality.buffer.PlainText(line, center_to=title_screen.width-4)
    for line in
    [
        "",
        "",
        "Our planet is no longer large enough",
        "to sustain it's growing population.",
        "",
        "Top scientists have come up with an ",
        "experimental technology to grow",
        "the planet itself until it can support us.",
        "",
        "The Growth Engine is now being tested",
        "on the asteroid 35 Leukothea.",
        "",
        "But not everyone is in support of this plan.",
        "Your enemies have launched drop pods of",
        "soldiers to destroy the Growth Engine",
        "before it can be fully tested.",
        "",
        "You must prevent them from succeeding!",
        "",
        "",
        "",
        "",
    ]
]
difficulty = "medium"

help_messages = [
    pytality.buffer.RichText(line)
    for line in
"""<WHITE>Help</>
<LIGHTGREY>
The Growth Engine you are protecting is in two halves,
one at the <LIGHTRED>North Pole</>, one at the <LIGHTBLUE>South Pole</>.

You'll need to defend both halves from invading enemies.
The enemies will drop from orbit near the center of the asteroid.
Stop them by building defensive towers.

Towers <WHITE>can be upgraded</> in attack speed, damage, and range.
They block enemy movement, but cannot be placed too close to
other towers or the Growth Engine itself.

The asteroid will <WHITE>get bigger over time</>, so be careful! Well-placed
towers may start drifting away from you as it grows.

For starters, try building a <WHITE>Long-Range Tower</> or two next to each pole.

<WHITE>[ENTER]</>: OK
""".splitlines()
]



header_text = pytality.buffer.PlainText("A game for Ludum Dare #23: Tiny World", y=1, center_to=title_screen.width-2, fg=pytality.colors.LIGHTGREY)
title_text = pytality.buffer.PlainText("THE BATTLE FOR 35 LEUKOTHEA", y=title_screen.height/4, center_to=title_screen.width-2, fg=pytality.colors.WHITE)
difficulty_text = pytality.buffer.RichText("<WHITE>[E]</><%s> Easy <%s>          <WHITE>[M]</><%s> Medium <%s>          <WHITE>[H]</><%s> Hard <%s>", y=title_screen.height*2/3-6)
start_text = pytality.buffer.RichText("<WHITE>[ENTER]</>: Start Game", y=title_screen.height*2/3-4)
footer_text = pytality.buffer.PlainText("by Jesse Truscott (Rectifier)", y=title_screen.height-1, center_to=title_screen.width-2, fg=pytality.colors.LIGHTGREY)

barrel = [pytality.colors.DARKGREY, pytality.colors.LIGHTGREY, pytality.colors.LIGHTGREY, pytality.colors.LIGHTGREY, pytality.colors.WHITE, pytality.colors.LIGHTGREY, pytality.colors.LIGHTGREY, pytality.colors.LIGHTGREY, pytality.colors.DARKGREY]
@event.on('title.tick')
def title_tick():
    global title_index
    ti = title_index/(game.fps)
    messages = title_messages[ti:ti+len(barrel)]
    if len(messages) < len(barrel):
        messages += title_messages[:(len(barrel)-len(messages))]

    base_y = main.screen_height/3-3
    for y, color in enumerate(barrel):
        if y >= len(messages):
            break
        msg = messages[y]
        msg.fg = color
        msg.update_data()
        msg.y = base_y + y

    title_screen.children = [header_text, title_text] + messages + [difficulty_text, start_text, footer_text]

    title_index += 1
    if title_index/(game.fps) == len(title_messages):
        title_index = 0

title_tick()

@event.on('title.draw')
def title_draw():
    difficulty_text.format((
        "LIGHTGREEN" if difficulty == "easy" else "DARKGREY",
        "/",
        "YELLOW" if difficulty == "medium" else "DARKGREY",
        "/",
        "LIGHTRED" if difficulty == "hard" else "DARKGREY",
        "/",
    ))
    difficulty_text.x = (main.screen_width/2) - (difficulty_text.width/2)
    start_text.x = (main.screen_width/2) - (start_text.width/2)
    title_screen.draw()

@event.on('title.input')
def title_input(key):
    global difficulty
    if key == "e" or (key == "left" and difficulty == "medium"):
        difficulty = "easy"
    elif key == "m" or (key == "left" and difficulty == "hard") or (key == "right" and difficulty == "easy"):
        difficulty = "medium"
    elif key == "h" or (key == "right" and difficulty == "medium"):
        difficulty = "hard"

    if key == "enter":
        if difficulty == "easy":
            game.lives = 120
            game.resources = 500
            game.reward_factor = 12
            game.high_power = 2.0
            game.mid_power = 1.1
            game.low_power = 0.75
        elif difficulty == "medium":
            game.lives = 100
            game.resources = 400
            game.reward_factor = 10
            game.high_power = 2.2
            game.mid_power = 1.2
            game.low_power = 0.8
        else:
            game.lives = 80
            game.resources = 400
            game.reward_factor = 8
            game.high_power = 2.3
            game.mid_power = 1.4
            game.low_power = 0.85

        create_help()
        game.mode = "game"
        event.fire("message", "Game started on %s difficulty." % difficulty.capitalize())

help_box = None
def create_help():
    global help_box
    width = max([message.width for message in help_messages]) + 4
    help_box = pytality.buffer.Box(x=(main.screen_width - width) /2, y=main.screen_height/2-(len(help_messages)/2)-2, width=width, height=len(help_messages)+4)
    for y, message in enumerate(help_messages):
        message.y = y+1
        message.x = (help_box.width/2) - (message.width/2) -1
    help_box.children = help_messages

@event.on('game.input')
def game_input(key):
    global help_box
    if help_box and key == 'enter':
        help_box = None
        #clear everything to avoid artifacting
        panels.left_panel.draw(dirty=True)
        panels.map_panel.draw(dirty=True)
        panels.highlight_panel.draw(dirty=True)
        panels.bottom_panel.draw(dirty=True)

@event.on('game.draw')
def game_draw():
    if help_box:
        help_box.draw(dirty=True)

#----------------

victory_box = None
@event.on('victory')
def on_victory():
    global victory_box
    log.debug("Victory!")
    victory_box = pytality.buffer.Box(x=main.screen_width/5, y=main.screen_height/2-6, width=main.screen_width*3/5, height=13, border_bg=pytality.colors.GREEN)
    victory_box.children = [
        pytality.buffer.PlainText("YOU WIN!", y=1, center_to=victory_box.width-2, fg=pytality.colors.WHITE),
        pytality.buffer.PlainText("You defeated %i waves of enemies" % game.wave, y=4, center_to=victory_box.width-2, fg=pytality.colors.WHITE),
        pytality.buffer.PlainText(" on %s difficulty with %i lives left." % (difficulty.capitalize(), game.lives), y=5, center_to=victory_box.width-2, fg=pytality.colors.WHITE),
        pytality.buffer.PlainText("The people of Earth thank you.", y=7, center_to=victory_box.width-2, fg=pytality.colors.LIGHTGREY),
        pytality.buffer.PlainText("Press [C] to continue playing, or [ENTER] to exit.", y=9, center_to=victory_box.width-2, fg=pytality.colors.DARKGREY),
    ]

    game.mode = "victory"
    game.last_active_panel = game.active_panel
    game.active_panel = "victory"

@event.on('victory.draw')
def victory_draw():
    victory_box.draw()

@event.on('victory.input')
def victory_input(key):
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
def victory_tick():
    pass

defeat_box = None
@event.on('defeat')
def on_victory():
    global defeat_box
    log.debug("Defeat!")
    defeat_box = pytality.buffer.Box(x=main.screen_width/5, y=main.screen_height/2-6, width=main.screen_width*3/5, height=13, border_bg=pytality.colors.RED)
    defeat_box.children = [
        pytality.buffer.PlainText("YOU LOSE!", y=1, center_to=defeat_box.width-2, fg=pytality.colors.WHITE),
        pytality.buffer.PlainText("You survived %i waves of enemies" % game.wave, y=4, center_to=defeat_box.width-2, fg=pytality.colors.WHITE),
        pytality.buffer.PlainText("on %s difficulty before the" % difficulty.capitalize(), y=5, center_to=defeat_box.width-2, fg=pytality.colors.WHITE),
        pytality.buffer.PlainText("Growth Engine was destroyed", y=6, center_to=defeat_box.width-2, fg=pytality.colors.WHITE),
        pytality.buffer.PlainText("Press [ENTER] to exit.", y=9, center_to=defeat_box.width-2, fg=pytality.colors.DARKGREY),
    ]

    game.mode = "defeat"
    game.last_active_panel = game.active_panel
    game.active_panel = "defeat"

@event.on('defeat.draw')
def defeat_draw():
    defeat_box.draw()

@event.on('defeat.input')
def defeat_input(key):
    if key == 'enter':
        pytality.term.clear()
        raise game.GameShutdown()

@event.on('defeat.tick')
def defeat_tick():
    pass



#@event.on('game.input')
def on_input(key):
    if key == 'v':
        event.fire('victory')

    if key == 'b':
        event.fire('defeat')
