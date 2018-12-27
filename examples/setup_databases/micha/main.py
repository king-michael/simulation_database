#!/usr/bin/env python
"""
Script to setup the database.

Workflow:
    create_database.__main__
        setups the database
    add_keywords.__main__
        adds keywords to the entries
"""

import os
import logging
from shutil import copy2
logger = logging.getLogger('SetupDatabase')
logging.basicConfig(level=logging.DEBUG)

# =========================================================================== #
# Input
# =========================================================================== #

db_output = 'micha.db'

clean_up = False        # delete files afterwards

create_database = True  # create the database
add_keywords = True     # add_keywords to the database
add_metadata = True     # add_metadata to the database

# =========================================================================== #
# Script
# =========================================================================== #
list_databases = []

# =================================== #
# Create the database
# =================================== #
if create_database:
    from create_database import __main__
    db_raw = __main__.db_final

else:
    db_raw = 'micha_raw.db'
list_databases.append(db_raw)

# =================================== #
# Add keywords
# =================================== #
if add_keywords:
    from add_keywords import __main__
    db_raw = __main__.db_final

else:
    db_raw = 'micha_added_keywords.db'
list_databases.append(db_raw)


# =================================== #
# Add metadata
# =================================== #
if add_metadata:
    from add_metadata import __main__
    db_raw = __main__.db_final
else:
    db_raw = 'micha_added_metadata.db'
list_databases.append(db_raw)


db_final = db_raw

logger.info('copy %s --> %s', db_final, db_output)
copy2(db_final,db_output)
if clean_up:
    for db in list_databases:
        if os.path.exists(db):
            logger.debug('clean up: remove database : {}'.format(db))
            os.remove(db)
logger.info('finished')
logger.info('database = {}'.format(db_final))
