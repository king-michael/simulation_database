"""
Whole workflow:
 add_keywords_from_folder
"""

import os
import logging

db_final = "micha_added_metadata.db"

logger = logging.getLogger('SetupDatabase:add_metadata')

logger.info('Add keywords')
logger.info('store in database : {}'.format(db_final))
from add_metadata_from_logfiles import *

copy2(db,db_final)
os.remove(db)