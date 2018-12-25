import os
import logging
import pandas as pd
from datetime import datetime

try:
    import simdb
except:
    import sys
    sys.path.append("../../../") # need this if labjournal is not installed

from simdb.utils.fileFinder import find_files
from simdb.databaseModel import *
from simdb.databaseAPI import *
import simdb.utils.tpr_parser as tpr_parser

# ======================================================= #
# Input
# ======================================================= #

db = 'example_simulations.db'
SIMS = os.path.join(os.path.dirname(__file__),'..', '..')
user = 'test'



# ========================================= #
# GROMACS - specific settings
# ========================================= #
# GMXBIN="/home/soft/gromacs/gromacs-2018/inst/shared/bin/"
GMXBIN="/home/soft/GROMACS/gromacs_2016.3_ompi-1.10.2_gcc-5.4/inst/oldcpu/bin/"
os.environ['GMXBIN'] = GMXBIN

# ======================================================= #
# script
# ======================================================= #

session = connect_database(db_path=db)

# ========================================= #
# Find files
# ========================================= #

SIM_IDS=[]
PATHS=[]
METAS=[]

for fname in find_files(pattern = 'topol.tpr', path = SIMS, dir_ignore = ['data']):
    path =  os.path.dirname(fname)
    sim_id = os.path.basename(path)
    try:
        meta = pd.Series.from_csv(os.path.join(path, "meta.csv"))
    except IOError:
        meta = pd.Series()
    SIM_IDS.append(sim_id)
    PATHS.append(path)
    METAS.append(meta)

# ========================================= #
# add entries
# ========================================= #

for i, entry_id in enumerate(SIM_IDS):
    path = PATHS[i]
    tprfile = os.path.join(path, 'topol.tpr')

    mapped_keywords = tpr_parser.main(tprfile)

    meta = METAS[i]
    try:
        description = meta['note']
        del meta['note']
    except KeyError:
        description = ""

    if 'created_on' in meta:
        created_on = meta['created_on']
        del meta['created_on']
    else:
        created_on = datetime.fromtimestamp(os.path.getmtime(tprfile))

    sim = store_dict(
        entry_id=entry_id,
        path=path,
        sim_type="GROMACS",
        description=description,
        created_on=created_on,
        owner=user,
        raw_mdp_parameters=mapped_keywords,
        raw_keywords=meta,
    )

    session.add(sim)
    session.flush()

session.commit()
session.close()
