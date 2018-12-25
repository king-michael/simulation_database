import os

try:
    import simdb
except:
    import sys
    sys.path.append("../../../") # need this if labjournal is not installed

from simdb.databaseModel import *

db = 'example_simulations.db'

# remove old DB
if os.path.exists(db):
    os.remove(db)

engine = create_engine('sqlite:///{}'.format(db) , echo=False) #  if we want spam

# Establishing a session
Session = sessionmaker(bind=engine)
session = Session()
setup_database(engine)



session.close()