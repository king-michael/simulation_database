#!/usr/bin/env python
"""
Python script to run all subroutines to create the example database.
"""

# Create database
from create_empty_database import *

# add gromacs
from add_gromacs_simulations import *

# add LAMMPS simulations
from add_lammps_simulations import *