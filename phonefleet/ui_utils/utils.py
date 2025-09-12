def plural(some_list: list | dict | int):
    if type(some_list) is int:
        return "s" if some_list > 1 else ""
    if type(some_list) is list or type(some_list) is dict:
        return "s" if some_list and len(some_list) > 1 else ""
    return ""
