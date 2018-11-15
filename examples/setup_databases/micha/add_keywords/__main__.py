"""
Whole workflow:
 add_keywords_from_folder
"""

db_final = "micha_added_keywords.db"
owner = "micha"

import logging
logger = logging.getLogger('SetupDatabase:add_keywords')
# logging.basicConfig(level=logging.DEBUG)

import os
os.environ['OWNER'] = owner
logger.info('Add keywords')
logger.info('store in database : {}'.format(db_final))

from add_keywords_from_folder import *


from shutil import copy2
logger.info('copy %s --> %s', db, db_final)
copy2(db,db_final)
os.remove(db)
logger.info('finished adding keywords')

