"""
Script to add metadata from logfiles

"""

import os
from shutil import copy2
import logging
from simdb.databaseModel import Main
import simdb.databaseAPI as api

from simdb.utils.fileFinder import find_files
from simdb.utils import lammps_logfile_parser as llfp

# =========================================================================== #
# input
# =========================================================================== #

# database name
db_raw = 'micha_added_keywords.db'
db = 'tmp_database_add_keywords_from_database.db'

# pattern of the logfile
pattern = 'log.*.lammps'

# directories to ignore
dir_ignore = ['build',
              'analysis',
              'EM_and_Equilibration']

# sort key to sort files
sort_key = lambda x: int(os.path.basename(x).replace('log.', '').replace('.lammps', ''))

# =========================================================================== #
# script
# =========================================================================== #
logger = logging.getLogger('SetupDatabase:add_metadata:add_metadata_from_logfiles')

# copy database
logger.info('copy %s --> %s', db_raw, db)
copy2(db_raw,db)

# connect to database
session = api.connect_database(db_path=db)

# get all simulations
sims = session.query(Main).all()

logger.info('iterate over the simulations')
# iterate over all simulations
for sim in sims:
    logger.info("search: sim.entry_id = {}".format(sim.entry_id))

    # skip if the path does not exist
    if not os.path.exists(sim.path):
        continue

    # get all logfiles
    logfiles = find_files(pattern='log.*.lammps',
                      path=sim.path,
                      dir_ignore=dir_ignore)

    # skip if no logfiles are found
    if len(logfiles) == 0:
        continue

    # get logfiles
    dict_metagroups = llfp.logfile_to_metagroups(logfiles,
                                                 combine=True,
                                                 sort=True,
                                                 sort_key=sort_key)

    #
    for meta_group_name, meta_group_data in dict_metagroups.items():
        api.add_meta_data(session=session,
                          entry_id=sim.entry_id,
                          meta_group_name=meta_group_name,
                          **meta_group_data)

session.commit()
session.close()