"""
Whole workflow:
 add_keywords_from_folder
"""
import os
import logging
from shutil import copy2

db_final = "micha_added_keywords.db"

logger = logging.getLogger('SetupDatabase:add_keywords')
# logging.basicConfig(level=logging.DEBUG)

logger.info('Add keywords')
logger.info('store in database : {}'.format(db_final))

from add_keywords_from_folder import *

logger.info('copy %s --> %s', db, db_final)
copy2(db,db_final)
os.remove(db)
logger.info('finished adding keywords')

