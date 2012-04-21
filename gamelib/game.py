import event

import logging
import threading
import time
import pytality

logic_lock = threading.Lock()

log = logging.getLogger(__name__)

class GameShutdown(Exception):
    pass

mode = "game"
active_panel = "map"

highlight_mode = "pathing_north"

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
    log.debug("Tick thread started")
    time.sleep(1)
    while True:
        goal = time.time() + 0.5
        run('tick')
        time.sleep(max(0.1, goal - time.time()))
