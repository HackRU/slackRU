def ifDebug(func, *args, inverted=False, **kwargs):
    """ Higher-Order Debug Function

    Calls function (1st arg) only if debugging is enabled.
    """
    from slackru.config import config
    if config.debug ^ inverted:  # Bitwise XOR operator
        func(*args, **kwargs)


def ifNotDebug(func, *args, **kwargs):
    ifDebug(func, *args, inverted=True, **kwargs)


import slackru.util.slack
