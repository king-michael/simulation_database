"""
Test of helper functions used in testing
"""
from __future__ import absolute_import
from helperfunctions import map_obj_to_string, check_list_unordered_equal

import pytest

def test_map_obj_to_string_integer():
    assert map_obj_to_string(1), "1"


def test_map_obj_to_string_string():
    assert map_obj_to_string("1"), "1"


def test_map_obj_to_string_list():
    inp = [1, "2"]
    res = map_obj_to_string(inp)
    expect = ["1", "2"]
    assert type(expect) == type(res)
    assert [all([len(expect) == len(res)] + [e == r for e, r in zip(expect, res)])]


def test_map_obj_to_string_tuple():
    inp = (1, "2")
    res = map_obj_to_string(inp)
    expect = ("1", "2")
    assert type(expect) == type(res)
    assert [all([len(expect) == len(res)] + [e == r for e, r in zip(expect, res)])]


def test_map_obj_to_string_dict():
    inp = {"a": 1, "b": "2"}
    res = map_obj_to_string(inp)
    expect = {'a' : '1', 'b' : '2'}
    assert type(expect) == type(res)
    assert [all([len(expect) == len(res)] + [e == r for e, r in zip(expect.items(), res.items())])]


@pytest.mark.parametrize('x, y, result',
     (  ([1, 2, 3], [1, 2, 3, 3], False),
        ([1, 2, 3], [1, 2, 3], True),
        ([3, 1, 2], [1, 2, 3], True),
        ([1, 2, 3, 3], [1, 2, 2, 3], False),
       )
     )
def check_check_list_unordered_equal(x, y, result):
    """
    Test `check_list_unordered_equal`
    Parameters
    ----------
    x : list
    y : list
    result : bool
        Result of the test
    """
    assert check_list_unordered_equal(x, y) == result
