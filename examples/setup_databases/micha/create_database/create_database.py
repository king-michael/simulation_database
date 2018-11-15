"""
Test the fileFinder
"""

import logging
logger = logging.getLogger('SetupDatabase:create_database:create_database')

import sys
import os

from fileHandler import FileHandler

sys.path.append("../../..")
sys.path.append("../../../..")

from simdb.databaseModel import *
from simdb.utils.fileFinder import find_files


kwargs_fileFinder = dict(
    pattern='_info_',
    path='/home/micha/SIM-PhD-King',
    dir_ignore=['OLD', 'old', 'Old', 'TMP', 'tmp', 'rm', 'template', 'testcase', 'input_files'])

if 'OWNER' in os.environ:
  OWNER = os.environ['OWNER']
else:
  OWNER = ""
logger.info('set OWNER = %s', OWNER)

fileHandler = FileHandler()
SIM_IDS=[]
PATHS=[]
DATAS=[]

logger.info('FIND FILES')
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

logger.info('CHECK FOR DUPLICATES IN sim_id')

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

logger.info('Create the Database')
db = 'tmp_database_raw.db'
logger.info('store in database : {}'.format(db))
try:
    os.remove(db)
    logger.info('removed old file: %s', db)
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
logger.info('Created the database: %s', db)
