"""
Database Model
This is a data base which stores data to run the app.
At the moment only paths to DB files are stored.
One could add more Tables here if we need more features.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

# Base class
Base = declarative_base()

class DBPath(Base):
    __tablename__ = 'dbpath'

    id = Column(Integer(), primary_key=True, index=True)
    path =  Column(String(100))
    comment = Column(String(100), nullable=True)


    def __repr__(self):
        return """{}(path='{}', comment='{}'""".format(
            self.__class__.__name__,
            self.path,
            self.comment)