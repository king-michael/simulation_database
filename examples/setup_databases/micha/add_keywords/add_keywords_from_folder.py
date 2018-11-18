#!/usr/bin/env python

from shutil import copy2

import sys
import logging
sys.path.append("../../..")
sys.path.append("../../../..")

from simdb.databaseModel import *
from simdb.databaseAPI import *
from map_folder_structure import generate_keywords


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

table = getEntryTable(db_raw, load_keys=True, load_tags=True) # load whole table
# get the path
pair_id_path = [(entry_id, path[len(root):])
                for i, (entry_id, path) in table[['entry_id', 'path']].iterrows() if path != ""]

logger.info('add_keywords_from_path: copy %s --> %s', db_raw, db)
copy2(db_raw,db)

session = establish_session('sqlite:///{}'.format(db))

logger.info('add_keywords_from_path: iterate over all paths and assign keywords')
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
logger.info('add_keywords_from_path: Created the database: %s', db)