"""
How to query metadata.
"""
from __future__ import print_function, nested_scopes, generators

from simdb.databaseAPI import *
import simdb.databaseAPI as api

db_path = '../../examples/setup_databases/andrej_raw.db'

session = api.connect_database(db_path=db_path)




print(api.get_all_groups(session))
group_names = [u'Group 2']
columns=('entry_id', 'path', 'owner', 'url', 'type', 'description')

# open database
query = session.query(Main.id,*[getattr(Main,attr) for attr in columns])
query = query.join(association_main_groups).join(Groups)
query = query.filter(Groups.name.in_(group_names))
sim = query.first()
print(sim)
print("2016_08_09_2ub_k11_01")
