"""
Test the fileFinder
"""

import logging
logger = logging.getLogger('SetupDatabase')
logging.basicConfig(level=logging.DEBUG)

import sys
import os
sys.path.append("../../..")
sys.path.append("../../../..")

# from labjournal.utils import *
from simdb.databaseModel import *
from simdb.utils.fileFinder import find_files
from fileHandler import FileHandler

kwargs_fileFinder = dict(
    pattern='_info_',
    path='/home/micha/SIM-PhD-King',
    dir_ignore=['OLD', 'old', 'Old', 'TMP', 'tmp', 'rm', 'templates', 'testcase'])

if 'OWNER' in os.environ:
  OWNER = os.environ['OWNER']
else:
  OWNER = ""
logger.info('create_database:create_missing_entries: set OWNER = %s', OWNER)

fileHandler = FileHandler()
SIM_IDS=[]
PATHS=[]
DATAS=[]

logger.info('create_database:create_database: FIND FILES')
ERRORS=False
WARNINGS=False
for fname in find_files(**kwargs_fileFinder):
    data = fileHandler.get_data_from_file(fname)
    data['path']=os.path.dirname(fname)

    try:
        SIM_IDS.append(data['ID']) # throws an ERROR if ID not in data
    except:
        print "ERROR: ID:\n ", fname # shows the FILE if an error is thrown
        ERRORS = True

    try:
        data['MEDIAWIKI']  # throws an ERROR if MEDIAWIKI not in data
    except:
        print "WARNING: NO MEDIAWIKI ENTRY:\n ", fname
        WARNINGS = True

    DATAS.append(data)  # only append if the first two cases are passed
    PATHS.append(fname)  # only append if the first two cases are passed

if ERRORS:
    exit()
if WARNINGS:
    exit()

logger.info('create_database:create_database: CHECK FOR DUPLICATES IN sim_id')

from collections import Counter
sim_count=Counter(SIM_IDS)
DUPLICATES=False
for k,v in sim_count.iteritems():
    if v != 1:
        DUPLICATES=True
        print "#======================================================#"
        for sim, path in zip(SIM_IDS,PATHS):
            if k == sim:
                print sim,path
if DUPLICATES:
    exit()

logger.info('create_database:create_database: Create the Database')
db = 'tmp_database_raw.db'
try:
    os.remove(db)
    logger.info('create_database:create_database: removed old file: %s', db)
except:
    pass
engine = create_engine('sqlite:///{}'.format(db) , echo=False) #  if we want spam
# Establishing a session
Session = sessionmaker(bind=engine)
session = Session()
setup_database(engine)
for data in DATAS:
    sim = Main(
       entry_id = data['ID'],
       url = data['MEDIAWIKI'],
       owner = OWNER,
       path = data['path'],
       description = data['INFO'] if 'INFO' in data.keys() else ""
    )
    session.add(sim)
session.commit()
session.close()
logger.info('create_database:create_database: Created the database: %s', db)
