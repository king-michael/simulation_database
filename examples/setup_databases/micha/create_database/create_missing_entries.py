"""
Create missing empty entries for database
"""
db_raw = 'tmp_database_raw.db'
db     = 'tmp_database_add_missing.db'

import logging
logger = logging.getLogger('SetupDatabase')
logging.basicConfig(level=logging.DEBUG)

import sys
sys.path.append("../../..")
sys.path.append("../../../..")

from simdb.databaseModel import *

from shutil import copy2
logger.info('create_database:create_missing_entries: copy %s --> %s', db_raw, db)
copy2(db_raw,db)

session = establish_session('sqlite:///{}'.format(db))

rv = session.query(Main.entry_id).all()

SIM_ID_MAIN = sorted(list(set([sim_id[0][:6] for sim_id in rv])))
SIM_ID_PARENTS = [sim_id[0] for sim_id in rv if len(sim_id[0]) ==6]
LAST_ID_MAIN=SIM_ID_MAIN[-1]

LAST_int=int(LAST_ID_MAIN[2:])
SIM_ID_MAIN_ALL=["MK{:04d}".format(i) for i in range(1,LAST_int+1)]

logger.info('create_database:create_missing_entries: add missing entries')

for sim_id in SIM_ID_MAIN_ALL:
    if sim_id not in SIM_ID_PARENTS:
        logger.info('create_database:create_missing_entries: add sim_id : %s', sim_id)
        sim = Main(
           entry_id=sim_id,
           url=sim_id,
           path='',
           description='',
           sim_type="MISSING ENTRY",
        )
        session.add(sim)
session.commit()
session.close()
logger.info('create_database:create_database: Created the database: %s', db)
