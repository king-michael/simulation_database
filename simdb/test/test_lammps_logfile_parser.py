import os

from simdb.utils import lammps_logfile_parser as llp
from pprint import pprint, pformat
import tarfile
import pytest
from references.reference_logfiles import reference_logfiles
tar = tarfile.open(os.path.join(os.path.dirname(__file__),
                                'references','logfiles.tar.gz'),
                       mode='r:gz')


def tear_down():
    global tar
    tar.close()



@pytest.mark.parametrize('filename, reference',
     tuple([(os.path.join(os.path.dirname(__file__),
                          'references', 'log.0.lammps'),
             reference_logfiles['log.0.lammps'])])
     )
def test_LogFileReader_normalfile(filename, reference):
    L = llp.LogFileReader(filename)
    assert L.runs == reference

@pytest.mark.parametrize('filename, reference',
     tuple([(tar.extractfile(tar.getmember(fname)), reference_logfiles[fname])
            for fname in tar.getnames()])
     )
def test_LogFileReader_fileobj(filename, reference):
    L = llp.LogFileReader(filename)
    assert L.runs == reference

if __name__ == '__main__':
    tear_down()