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

mode = "title"
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

reward_factor = 10
mid_power = 1.4
high_power = 2.3
low_power = 0.8

def calc_next_wave():
    global wave, wave_landers, wave_units, wave_hp, wave_type
    global next_wave_type, next_wave_landers, next_wave_units, next_wave_hp
    wave += 1
    log.debug("Next wave is %i", wave)
    wave_type = next_wave_type
    wave_hp = next_wave_hp
    wave_landers = next_wave_landers
    wave_units = next_wave_units

    #every six waves, things get harder.
    stage = int(wave/6)

    if wave % 6 == 0:
        next_wave_type = 'Swarm'
        next_wave_hp = 4 + int(wave ** low_power)
        next_wave_landers = 4 + int(stage ** high_power)
        next_wave_units = 1 + stage

    elif wave % 6 == 3:
        next_wave_type = 'Cluster'
        next_wave_hp = 8 + int(wave ** 1.2)
        next_wave_landers = 2 +  + int(stage ** mid_power)
        next_wave_units = 3 +  + int(stage ** mid_power)

    else:
        next_wave_type = 'Normal'
        next_wave_hp = 5 + wave
        next_wave_landers = 2 + int(stage ** mid_power)
        next_wave_units = 1 + stage
    
    if wave == 31:
        event.fire('victory')

def start():
    log.debug("Game starting")

    lastmode = None

    tick_thread = threading.Thread(target=tick)
    tick_thread.daemon = True
    tick_thread.start()

    run('start')
    while True:
        k = pytality.term.getkey()
        if k:
            run('input', k.lower())



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
