import os
import sys

from .config import LOG

colors_supported = None


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
    Returns True if the running system's terminal
    supports color, and False otherwise.
    Imported from django
    @see https://github.com/django/django/blob/master/django/core/management/color.py
    """
    global colors_supported
    if colors_supported is None:
        plat = sys.platform
        supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)
        pycharm_hosted = int(os.environ.get('PYCHARM_HOSTED', 0)) is 1

        # isatty is not always implemented, #6223.
        is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        colors_supported = supported_platform and is_a_tty or pycharm_hosted
    return colors_supported


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
    if LOG is not None and LOG == 1:
        print(content)


def constrain(val, min, max):
    if val < min:
        return min
    elif val > max:
        return max
    else:
        return val


def print_progress_bar(iteration: int, total: int, prefix: str = '', suffix: str = '', decimals: int = 1,
                       length: int = 100, fill: str = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '░' * (length - filled_length)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
