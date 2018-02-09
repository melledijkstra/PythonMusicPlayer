import sys

import os

from .config import DEBUG

colors_enabled = None


class Colors:
    BLUE = '\033[94m'
    PINK = '\033[95m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    CLEAR = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def console_has_color():
    """
    Returns True if the running system's terminal supports color, and False
    otherwise.
    Imported from django
    """
    global colors_enabled
    if colors_enabled is None:
        plat = sys.platform
        supported_platform = plat != 'Pocket PC' and (plat != 'win32' or
                                                      'ANSICON' in os.environ)
        # isatty is not always implemented, #6223.
        is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        if not supported_platform or not is_a_tty:
            colors_enabled = False
        colors_enabled = True
    return colors_enabled


def colorstring(content, color):
    colors = Colors.__dict__
    if color in colors.values() and console_has_color():
        return color + str(content) + Colors.CLEAR
    else:
        return content


def bugprint(content: object):
    """
    Only prints message if in debug mode

    :type content: str
    :param content: the string to print
    """
    if DEBUG is not None and DEBUG == 1:
        print(content)


def constrain(val, min, max):
    if val < min:
        return min
    elif val > max:
        return max
    else:
        return val
