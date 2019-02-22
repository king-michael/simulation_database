# coding=utf-8
"""
Create missing empty entries for database
"""
from __future__ import print_function
db_raw = 'tmp_database_raw.db'
db     = 'tmp_database_add_missing.db'

import logging
logger = logging.getLogger('SetupDatabase:create_database:create_missing_entries')

import sys
import os
sys.path.append("../../..")
sys.path.append("../../../..")

from simdb.databaseModel import *
import simdb.databaseAPI as api
from shutil import copy2


logger.info('Create missing entries')
logger.info('use database : {}'.format(db_raw))
logger.info('store in database : {}'.format(db))

if 'OWNER' in os.environ:
  OWNER = os.environ['OWNER']
else:
  OWNER = ""
logger.info('set OWNER = %s', OWNER)

logger.info('copy %s --> %s', db_raw, db)
copy2(db_raw,db)

# connect to database
session = api.connect_database(db_path=db)

rv = session.query(Main.entry_id).all()

SIM_ID_MAIN = sorted(list(set([sim_id[0][:6] for sim_id in rv])))
SIM_ID_PARENTS = [sim_id[0] for sim_id in rv if len(sim_id[0]) ==6]
LAST_ID_MAIN=SIM_ID_MAIN[-1]

try:
    LAST_int=int(LAST_ID_MAIN[2:])
except:
    print(LAST_ID_MAIN)
    raise
SIM_ID_MAIN_ALL=["MK{:04d}".format(i) for i in range(1,LAST_int+1)]

logger.warn('add missing entries')

for sim_id in SIM_ID_MAIN_ALL:
    if sim_id not in SIM_ID_PARENTS:
        logger.info(' add sim_id : %s', sim_id)
        sim = Main(
           entry_id = sim_id,
           url = sim_id,
           path = '',
           owner = OWNER,
           description = '',
           type='MISSING ENTRY',
        )
        session.add(sim)
session.commit()
session.close()
logger.info('Created the database: %s', db)
