"""
Whole workflow:
 create the database
 add missing entries
 add parent-child relation ship based on sim_id
"""


db_final = "micha_raw.db"
owner = "micha"

import logging
logger = logging.getLogger('SetupDatabase:create_database')
# logging.basicConfig(level=logging.DEBUG)

import os
os.environ['OWNER'] = owner
logger.info('Create the database')
logger.info('store in database : {}'.format(db_final))
from create_database import *

from create_missing_entries import *
os.remove(db_raw)

from find_parents import *
os.remove(db_raw)

from shutil import copy2
logger.info('copy %s --> %s', db, db_final)
copy2(db,db_final)
os.remove(db)
logger.info('finished')

