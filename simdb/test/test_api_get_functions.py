from __future__ import absolute_import, generators, nested_scopes, division
import pytest
from reference_database import *
from test_01_storage import test_store_main_table as setup_main_table
import os
from pandas import NaT

import simdb.databaseAPI as api



def setup_module():
    setup_main_table()

def map_datetime(reference_dict):
    "map NaT to None"
    out = dict()
    for entry_id, obj in reference_dict.items():
        if obj.created_on is None:
            tmp = obj._asdict()
            tmp['created_on'] = NaT
            obj = obj_main(**tmp)
        out[entry_id] = obj
    return out


@pytest.mark.parametrize('attributes, reference_dict',
              ((attributes, reference_dict),))
def test_get_entry_table(attributes, reference_dict):
    "test the get entry_table function"
    table = api.get_entry_table(db_path=db_path)

    assert table.shape[0] == len(reference_dict), "should be the same length"
    reference_dict = map_datetime(reference_dict)

    for i, sim in table.iterrows():
        for attr in attributes:
            test =  getattr(sim, attr)
            ref = getattr(reference_dict[sim.entry_id], attr)
            if ref is NaT or ref is None:
                assert test is ref ,\
                     "\n attribute = {} for {} is not (==) the same:".format(attr, sim.entry_id) +\
                     "\n reference:\n  {}".format(ref) +\
                     "\n testdata:\n  {}".format(test)
            else:
                assert test == ref, \
                    "\n attribute = {} for {} is not the same:".format(attr, sim.entry_id) + \
                    "\n reference:\n  {}".format(getattr(reference_dict[sim.entry_id], attr)) + \
                    "\n testdata:\n  {}".format(getattr(sim, attr))



def teardown_module():
    "function called to clean up"
    if os.path.exists(db_path):
        os.remove(db_path)


if __name__ == '__main__':
    setup_module()
    test_get_entry_table(attributes, reference_dict)
    teardown_module()