import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from databaseModelApp import DBPath, Base

db = 'app.db'
# remove old DB
# try:
#     os.remove(db)
# except:
#     pass
engine = create_engine('sqlite:///{}'.format(db) , echo=False) #  if we want spam

# Establishing a session
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

session.add(DBPath(path="/home/andrejb/test.db", comment="Just a Test"))
session.commit()

session.close()