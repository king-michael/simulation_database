from __future__ import absolute_import, division, generators, nested_scopes
from simdb.databaseModel import *
from collections import namedtuple
from datetime import datetime
import os

from reference_database import *


def test_store_main_table():
    "Test function to create the database"
    if os.path.exists(db_path):
        os.remove(db_path)

    engine = create_engine('sqlite:///{}'.format(db_path))
    setup_database(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    for key, obj in reference_dict.items():
        sim = Main(**dict((attr, getattr(obj, attr)) for attr in attributes))
        session.add(sim)
    session.commit()
    session.close()

    assert os.path.exists(db_path), "Database not created"


def test_load_main_table():
    "Test if stored"

    engine = create_engine('sqlite:///{}'.format(db_path))
    Session = sessionmaker(bind=engine)
    session = Session()

    sims = session.query(Main).all()
    assert len(sims) == len(reference_dict), "should be the same length"
    for sim in sims:
        assert all(getattr(sim, attr) == getattr(reference_dict[sim.entry_id], attr) for attr in attributes),\
            "attributes are not the same"
    session.close()


def teardown_module():
    "function called to clean up"
    if os.path.exists(db_path):
        os.remove(db_path)


if __name__ == '__main__':
    test_store_main_table()
    test_load_main_table()
    teardown_module()