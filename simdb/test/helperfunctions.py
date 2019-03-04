"""
Utility function needed for testing
"""
import collections

def map_obj_to_string(obj):
    """
    Function to create a string version from an object.

    Parameters
    ----------
    obj
        Some python object

    Returns
    -------
    str_version

    Examples
    --------
    >>> map_obj_to_string(1)
    "1"
    >>> map_obj_to_string("1")
    "1"
    >>> map_obj_to_string([1,"2"])
    ["1", "2"]
    >>> map_obj_to_string(("1", 2))
    ("1", "2")
    >>> map_obj_to_string({"a" : 1, "b" : "2"})
    {"a" : "1", "b" : "2"}
    """
    if isinstance(obj, list):
        rv = list(map_obj_to_string(i) for i in obj)
    elif isinstance(obj, tuple):
        rv = tuple(map_obj_to_string(i) for i in obj)
    elif isinstance(obj, dict):
        rv = dict((k,map_obj_to_string(v)) for k, v in obj.items())
    else:
        rv = str(obj)
    return rv

def check_list_unordered_equal(x, y):
    """
    Function to check if two list are equal.
    Parameters
    ----------
    x : list
    y : list

    Returns
    -------
    result : bool
        Check if two list are the same

    Examples
    >>> check_list_equal([1, 2, 3], [1, 2, 3, 3])
    False
    >>> check_list_equal([1, 2, 3], [1, 2, 3])
    True
    >>> check_list_equal([1, 2, 3, 3], [1, 2, 2, 3])
    False
    """
    return collections.Counter(x) == collections.Counter(y)