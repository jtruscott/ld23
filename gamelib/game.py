import event

import logging
import threading
import time

logic_lock = threading.Lock()

log = logging.getLogger(__name__)

class GameShutdown(Exception):
    pass

mode = "game"

def start():
    global mode
    log.debug("Game starting")

    lastmode = None

    tick_thread = threading.Thread(target=tick)
    tick_thread.daemon = True
    tick_thread.start()

    while True:
        time.sleep(1)

def tick():
    global mode
    log.debug("Tick thread started")
    while True:
        time.sleep(1)
        log.debug("Tick")
        with logic_lock:
            event.fire('%s.tick' % mode)
            event.fire('%s.draw' % mode)
