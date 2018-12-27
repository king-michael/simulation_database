import os

from support.fileHandler import FileHandler

try:
    import simdb
except:
    import sys
    sys.path.append("../../../") # need this if labjournal is not installed

from simdb.databaseModel import *
import simdb.databaseAPI as api
from simdb.utils.fileFinder import find_files
from simdb.utils import lammps_logfile_parser as llfp

# ======================================================= #
# Input
# ======================================================= #

db = 'example_simulations.db'
SIMS = os.path.realpath(os.path.join(os.path.dirname(__file__),'..', '..'))
user = 'test'

# LAMMPS Settings

kwargs_fileFinder = dict(
    pattern='_info_',
    path=SIMS,
    dir_ignore=['OLD', 'old', 'Old', 'TMP', 'tmp', 'rm', 'template', 'testcase', 'input_files'])

# ======================================================= #
# Script
# ======================================================= #

session = api.connect_database(db_path=db)

# ============================================= #
# find files
# ============================================= #

fileHandler = FileHandler()
SIM_IDS=[]
PATHS=[]
DATAS=[]

ERRORS=False
WARNINGS=False

for fname in find_files(**kwargs_fileFinder):
    data = fileHandler.get_data_from_file(fname)
    data['path']=os.path.dirname(fname)

    SIM_IDS.append(data['ID'])

    DATAS.append(data)
    PATHS.append(fname)

for data in DATAS:
    sim = Main(
        entry_id = data['ID'],
        url = data['MEDIAWIKI'],
        owner = user,
        type='LAMMPS',
        path = data['path'],
        description = data['INFO'] if 'INFO' in data.keys() else ""
    )
    session.add(sim)
# session.commit()


# ============================================= #
# add keywords
# ============================================= #

for sim_id in SIM_IDS:
    sim = session.query(Main).filter(Main.entry_id == sim_id).one()
    sim.keywords.extend([
        Keywords(name='polymorph', value='calcite'),
        Keywords(name='solvation state', value='bulk'),
        Keywords(name='system state', value='crystalline'),
        Keywords(name='force field', value='Raiteri2015'),
    ])
    session.add(sim)
# session.commit()


# ============================================= #
# scan logfiles
# ============================================= #

for sim_id in SIM_IDS:
    sim = session.query(Main).filter(Main.entry_id == sim_id).one()

    logfiles = find_files(pattern='log.*.lammps',
                      path=sim.path,
                      dir_ignore=['build',
                                  'analysis',
                                  'EM_and_Equilibration'])

    logfiles.sort(key=lambda x: int(
        os.path.basename(x).replace('log.', '').replace('.lammps', '')
    ))

    dict_metagroups = llfp.logfile_to_metagroups(logfiles,
                                                 combine=True,
                                                 sort=False)

    for meta_group_name, meta_group_data in dict_metagroups.items():
        api.add_meta_data(session=session,
                          entry_id=sim.entry_id,
                          meta_group_name=meta_group_name,
                          **meta_group_data)

session.commit()
session.close()