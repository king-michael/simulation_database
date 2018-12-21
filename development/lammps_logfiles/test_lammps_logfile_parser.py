import sys
import os
sys.path.insert(0,'../..')
from simdb.utils import lammps_logfile_parser as llp
from pprint import pprint, pformat

def total_test():
    path = 'files'
    files = os.listdir(path)
    for file in files:
        print '\n', file

        L = llp.LogFileReader(os.path.join(path, file))
        for run in L.runs:
            print run

def test_production():
    path = 'files'
    file = "log.1.lammps"
    L = llp.LogFileReader(os.path.join(path, file))
    for run in L.runs:
        print pformat(run)
        print pformat(llp.map_lammps_to_database(run))


test_production()