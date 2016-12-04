from .config import DEBUG


class Colors:
    BLUE = '\033[94m'
    HEADER = '\033[95m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    CLEAR = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def printcolor(content, color):
    colors = Colors.__dict__
    if color in colors.values():
        return color + str(content) + Colors.CLEAR
    else:
        return content


def bugprint(content: object):
    """
    Only prints message if in debug mode

    :type content: str
    :param content: the string to print
    :type end: str
    :param end: the ending passed to print
    """
    if DEBUG != None and DEBUG == 1:
        print(content)


def constrain(val, min, max):
    if val < min:
        return min
    elif val > max:
        return max
    else:
        return val
