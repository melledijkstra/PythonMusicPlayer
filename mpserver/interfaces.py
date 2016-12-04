from .tools import bugprint as b

class Logger:
    """
    The base class for all classes in mpserver package
    """
    def __init__(self):
        pass

    def log(self, content: object):
        b("[*"+str(self.__class__.__name__)+"*] " + str(content))