"""
How to query metadata.
"""
from __future__ import print_function, nested_scopes, generators
from simdb.databaseModel import *

import simdb.databaseAPI as api


db_path = 'micha.db'

session = api.connect_database(db_path=db_path)

print("#"*80+"\n#> api.api.get_groups(session, entry_id='MK0085', as_list=True)")
metagroups = api.get_meta_groups(session, entry_id='MK0085', as_list=True)
for metagroup in metagroups:
    print(metagroup)

print("#"*80+"\n#> api.api.get_groups(session, entry_id='MK0085', as_list=False)")
metagroups = api.get_meta_groups(session, entry_id='MK0085', as_list=False)
for metagroup in metagroups.items():
    print(metagroup)

print("#"*80+"\n#> api.api.get_groups(session, entry_id='MK0085')")
metagroups = api.get_meta_groups(session, entry_id='MK0085')
for metagroup in metagroups.items():
    print(metagroup)

print("#"*80+"\n#> api.get_single_metagroups(session, entry_id='MK0086', 'thermostat', as_list=True)")
metagroup = api.get_single_meta_group(session, entry_id='MK0085', name='thermostat', as_list=True)
print(metagroup)

print("#"*80+"\n#> api.get_single_metagroups(session, entry_id='MK0086', 'thermostat', as_list=False)")
metagroup = api.get_single_meta_group(session, entry_id='MK0085', name='thermostat', as_list=False)
print(metagroup)

print("#"*80+"\n#> api.get_single_metagroups(session, entry_id='MK0086', 'thermostat')")
metagroup = api.get_single_meta_group(session, entry_id='MK0085', name='thermostat')
print(metagroup)

