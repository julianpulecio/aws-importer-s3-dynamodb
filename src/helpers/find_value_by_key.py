def find_value_by_key(iterable, key):
    if type(iterable) is list:
        for elem in iterable:
            result = find_value_by_key(elem,key)
            if result is not None:
                return result
    if type(iterable) is dict:
        for elem_key, elem in iterable.items():
            if elem_key == key:
                return elem
            result = find_value_by_key(elem,key)
            if result is not None:
                return result