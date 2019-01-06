"""
Script to detect the folder structure.
"""

import os

from simdb.utils.detect_folder_type import guess_folder_type

# root folder
ROOT = os.path.realpath('../../examples/example_simulations')
folders = [os.path.join(ROOT,folder, subfolder)
           for folder in os.listdir(ROOT)
           if os.path.isdir(os.path.join(ROOT,folder))
           for subfolder in os.listdir(os.path.join(ROOT,folder))
           if os.path.isdir(os.path.join(ROOT,folder, subfolder))]

# cases of folders
cases = ['LAMMPS', 'GROMACS']
#config_file = 'regex_weights.ini'

# exclude dir
dir_ignore = ['analysis']


# iterate over all folders
for path in folders:
    folder = os.path.basename(path)
    print(folder, guess_folder_type(path, cases=cases, dir_ignore=dir_ignore))