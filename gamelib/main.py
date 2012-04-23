import pytality
import event
import game
import sys
import logging
logging.disable(logging.DEBUG)
log = logging.getLogger(__name__)

screen_width = 100
screen_height = 70

def main():
    if len(sys.argv) > 1:
        pytality.term.init(backends=sys.argv[1:], width=screen_width, height=screen_height)
    else:
        pytality.term.init(width=screen_width, height=screen_height)
    pytality.term.set_title('The Battle For 35 Leukothea (LD48 #23: Tiny World)')
    pytality.term.clear()
    try:
        event.fire('setup')
        game.start()

    except game.GameShutdown:
        pytality.term.reset()
    except KeyboardInterrupt:
        pytality.term.clear()
        pytality.term.reset()
        raise
    except Exception, e:
        log.exception(e)
        raise

    finally:
        log.debug('Shutting down')
        logging.shutdown()
