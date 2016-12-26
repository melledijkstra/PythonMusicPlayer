from datetime import datetime

from .tools import bugprint as b

class Logger:
    """
    The base class for all classes in mpserver package
    """
    def __init__(self):
        super(Logger, self).__init__()
        self._logging = True

    def log(self, content: object):
        if(self._logging):
            b("[*"+str(self.__class__.__name__)+"* | "+datetime.now().strftime('%H:%M:%S')+"] " + str(content))

    def set_logging(self, state: bool):
        """ Set the logging state of this class
        If true then it's able to log else not

        :param state: True to turn on logging and False for off
        """
        self._logging = state

class EventFiring:
    """
    This class has event firing capabilities.
    You can implement this class when an Observer pattern needs to be used
    """
    def __init__(self):
        super(EventFiring, self).__init__()
        self._event_callbacks = {}
        for attr in [attr for attr in vars(self.__class__.Events) if not callable(attr) and not attr.startswith("__")]:
            self._event_callbacks[getattr(self.__class__.Events, attr)] = []

    def _fire_event(self, fire_event):
        # check if the fired event is in the registered events
        if fire_event in self._event_callbacks.keys():
            # get all callbacks from that event that are registered
            callbacks = self._event_callbacks[fire_event]
            # loop through all registered callbacks
            for callback in callbacks:
                if callable(callback):
                    # if the callback is callable then call it
                    callback()

    def subscribe(self, event, callback):
        if event in self._event_callbacks:
            self._event_callbacks[event].append(callback)

    class Events:
        pass
