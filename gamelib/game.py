import event

import logging
import threading
import time
import pytality
import os, sys
import traceback

logic_lock = threading.Lock()

log = logging.getLogger(__name__)

class GameShutdown(Exception):
    pass

mode = "game"
active_panel = "map"

highlights = set(["tower"])

fps = 15
ticks = 0


wave = 0
wave_delay = fps * 90
growings = 0

next_wave_type = "Normal"
next_wave_hp = 4
next_wave_landers = 2
next_wave_units = 2

resources = 400
lives = 100

def calc_next_wave():
    global wave, wave_landers, wave_units, wave_hp, wave_type
    global next_wave_type, next_wave_landers, next_wave_units, next_wave_hp
    wave += 1
    log.debug("Next wave is %i", wave)
    wave_type = next_wave_type
    wave_hp = next_wave_hp
    wave_landers = next_wave_landers
    wave_units = next_wave_units

    if wave % 10 == 0:
        next_wave_type = 'Swarm'
        next_wave_hp = 4 + wave/3
        next_wave_landers = 2 + wave
        next_wave_units = 1 + wave/10

    elif wave % 10 == 5:
        next_wave_type = 'Cluster'
        next_wave_hp = 4 + wave/2
        next_wave_landers = 2 + wave/8
        next_wave_units = 3 + wave/4

    else:
        next_wave_type = 'Normal'
        next_wave_hp = 4 + wave/2
        next_wave_landers = 2 + wave/5
        next_wave_units = 2 + wave/10

def start():
    log.debug("Game starting")

    lastmode = None

    tick_thread = threading.Thread(target=tick)
    tick_thread.daemon = True
    tick_thread.start()

    run('start')
    while True:
        run('input', pytality.term.getkey())



def run(event_name, *args):
    global mode
    with logic_lock:
        event.fire('%s.%s' % (mode, event_name), *args)
        event.fire('%s.predraw' % mode)
        event.fire('%s.draw' % mode)
        pytality.term.flip()
    
def tick():
    global ticks
    delay = 1.0/fps
    try:
        log.debug("Tick thread started")
        time.sleep(1)
        while True:
            goal = time.time() + delay
            run('tick')
            ticks += 1

            sleeping_for = goal - time.time()
            if sleeping_for < 0:
                log.debug("uhoh, lagging, sleeping_for was %r", sleeping_for)
                sleeping_for = 0
            time.sleep(sleeping_for)

    except Exception as e:
        logging.exception(e)
        try:
            traceback.print_exc(e, file=sys.stderr)
        finally:
            os._exit(1)
