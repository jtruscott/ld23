import logging
log = logging.getLogger('event')

listeners = {}
def on(event):
    def wrapper(fn):
        log.debug("registered event '%s.%s' on '%s'", fn.__module__, fn.__name__, event)
        listeners.setdefault(event, [])
        listeners[event].append(fn)
        return fn
    return wrapper

already_warned = set()
def fire(event, *args, **kwargs):
    if event not in listeners:
        if event not in already_warned:
            log.warn("firing event '%s', which has no listeners!", event)
            already_warned.add(event)
        return
    #these are too hot to log
    if not ('tick' in event or 'draw' in event):
        log.debug("firing '%s' (%i listeners)", event, len(listeners[event]))
    for f in listeners[event]:
        try:
            f(*args, **kwargs)
        except:
            log.error("exception firing '%s' (%i listeners)", event, len(listeners[event]))
            raise
