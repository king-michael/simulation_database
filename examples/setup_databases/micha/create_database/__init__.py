"""
Whole workflow:
 create the database
 add missing entries
 add parent-child relation ship based on sim_id
"""

db_final = "micha.db"
import logging
logger = logging.getLogger('SetupDatabase')
logging.basicConfig(level=logging.DEBUG)


from create_database import *

from create_missing_entries import *

from find_parents import *


from shutil import copy2
logger.info('create_database: copy %s --> %s', db, db_final)
copy2(db,db_final)
logger.info('create_database: finished')