class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    CLEAR = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def constrain(val, minn, maxn):
    if val < minn:
        return minn
    elif val > maxn:
        return maxn
    else:
        return val
