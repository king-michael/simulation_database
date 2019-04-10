import os
from simdb.databaseModel import create_engine, Base, Main
from simdb.databaseAPI import session_handler

from test_01_storage import test_store_main_table as store_main_table

def setup_module():
    store_main_table()

def test_session_handler_contextmanager():
    with session_handler(db_path="test_database.db") as session:
        assert session.is_active == True
        session.add(Main(entry_id='1'))
        assert session.query(Main).filter(Main.entry_id == 1).one_or_none() is not None

    assert session.query(Main).filter(Main.entry_id == 1).one_or_none() is None

def teardown_module():
    os.remove("test_database.db")

if __name__ == '__main__':
    store_main_table()