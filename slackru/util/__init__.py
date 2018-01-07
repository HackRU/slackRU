def ifDebugThen(func, *args, inverted=False, **kwargs):
    """ Higher-Order Debug Function

    Calls function only if debugging is enabled.
    """
    from slackru.config import config
    if config.DEBUG ^ inverted:  # Bitwise XOR operator
        func(*args, **kwargs)


def ifNotDebugThen(func, *args, **kwargs):
    ifDebugThen(func, *args, inverted=True, **kwargs)


import slackru.util.slack
