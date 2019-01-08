#!/usr/bin/env python

from simdb.databaseModel import *
from eralchemy import render_er

## Draw from SQLAlchemy base
render_er(Base, 'erd_from_simdb.png')
