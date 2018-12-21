#!/usr/bin/env python

import tarfile
from simdb.utils import lammps_logfile_parser as llp
from pprint import pformat

with tarfile.open('logfiles.tar.gz', mode='r:gz') as tar:
    storage = dict()
    for fname in tar.getnames():
        fileobj = tar.extractfile(tar.getmember(fname))
        L = llp.LogFileReader(fileobj)
        storage[fname] = L.runs

with open("reference_logfiles.py", 'w') as fp:
    fp.write("reference = {\n "+pformat(storage)[1:-1]+'\n}')
