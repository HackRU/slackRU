def flatten(lst):
    res = []
    for itm in lst:
        if isinstance(itm, list):
            res += flatten(itm)
        else:
            res.append(itm)
    return res
