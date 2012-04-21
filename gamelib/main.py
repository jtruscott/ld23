import pytality
import event
import game

import logging

log = logging.getLogger(__name__)

screen_width = 120
screen_height = 80

def main():
    pytality.term.init(width=screen_width, height=screen_height)
    pytality.term.set_title('Some Kind Of TD (LD48 #23: Tiny World)')
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
