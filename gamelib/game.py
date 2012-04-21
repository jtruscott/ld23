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

fps = 10
ticks = 0

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
            if sleeping_for < 0.01:
                log.debug("uhoh, lagging, sleeping_for was %r", sleeping_for)
                sleeping_for = 0.01
            time.sleep(sleeping_for)

    except Exception as e:
        logging.exception(e)
        try:
            traceback.print_exc(e, file=sys.stderr)
        finally:
            os._exit(1)
