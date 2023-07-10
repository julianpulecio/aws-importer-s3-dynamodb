import inspect
from src.helpers.find_value_by_key import find_value_by_key

def dict_to_object(class_, dictionary):
    attr_dict = {}
    for arg in inspect.signature(class_.__init__).parameters:
        attr_dict[arg] = find_value_by_key(dictionary, arg)
    del attr_dict['self']

    return class_(**attr_dict)