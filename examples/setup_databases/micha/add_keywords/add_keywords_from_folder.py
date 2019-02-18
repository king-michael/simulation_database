#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

from shutil import copy2

import sys
import logging

sys.path.append("../../..")
sys.path.append("../../../..")

from simdb.databaseModel import *
import simdb.databaseAPI as api
from .map_folder_structure import generate_keywords


logger = logging.getLogger('SetupDatabase:add_keywords:add_keywords_from_path')

# =========================================================================== #
# Input
# =========================================================================== #

db_raw = 'micha_raw.db'
db = 'tmp_database_add_keywords_from_database.db'
root='/home/micha/SIM-PhD-King/'

# =========================================================================== #
# script
# =========================================================================== #

logger.info('Add keywords from path')
logger.info('use database : {}'.format(db_raw))
logger.info('store in database : {}'.format(db))
logger.info('root = %s' % root)



logger.info('copy %s --> %s', db_raw, db)
copy2(db_raw,db)

# connect to database
session = api.connect_database(db_path=db)

table = api.get_entry_table(session=session) # load whole table

# get the path
pair_id_path = [(entry_id, path[len(root):])
                for i, (entry_id, path) in table[['entry_id', 'path']].iterrows() if path != ""]

logger.info('iterate over all paths and assign keywords')
for i, (entry_id, path) in enumerate(pair_id_path):
    list_keywords = generate_keywords(path)
    # get simulation
    sim = session.query(Main).filter(Main.entry_id == entry_id).one()
    # add keywords
    sim.keywords.extend(list(map(lambda x: Keywords(name=x.name, value=x.value), list_keywords)))
    # add simulation
    session.add(sim)

session.commit()
session.close()
logger.info('Created the database: %s', db)
