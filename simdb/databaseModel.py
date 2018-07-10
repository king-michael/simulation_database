"""
Database Model
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy import DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import not_, and_
from sqlalchemy import Table
from sqlalchemy import exists
# Base class
Base = declarative_base()

#===================================================================#
# Database Models
#===================================================================#
# Column parameters:
#  http://docs.sqlalchemy.org/en/latest/core/metadata.html?highlight=onupdate#sqlalchemy.schema.Column.params.onupdate

# relationship:
#    lazy = 'dynamic'  # returns query => can be used with .filter .order => .all()
#    lazy = 'select'   # automatically runs a second query if accessed, returns results (two query in total)
#    lazy = 'joined'   # joins them at the query of the entry (one query in total)
#    lazy = 'subquery' #  same as joined, otherway, different performance

# TODO Add mapping Association-->Main; e.g. Main.parents shold return list of Main obj

class Main(Base):
    __tablename__ = 'main'

    id = Column(Integer(), primary_key=True, index=True)
    entry_id =  Column(String(50), unique=True, index=True) # should be discussed
    mediawiki = Column(String(255), nullable=True)
    path = Column(String(255))
    sim_type = Column(String(20), nullable=True)
    description = Column(String(1023), nullable=True) # maybe longer in the future
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    children = relationship('AssociationMainMain',
                            back_populates="parent",
                            foreign_keys='AssociationMainMain.parent_id',
                            cascade="all, delete-orphan",  # apply delete also for entries in assosiation
                            passive_deletes=True,  # apply delete also for entries in assosiation
                            lazy='dynamic'
                            )
    parents = relationship('AssociationMainMain',
                           back_populates="child",
                           foreign_keys='AssociationMainMain.child_id',
                           cascade="all, delete-orphan",  # apply delete also for entries in assosiation
                           passive_deletes=True,  # apply delete also for entries in assosiation
                           lazy='dynamic'
                           )
    keywords = relationship('Keywords',
                            backref='entry_id' , # check cascade_backrefs
                            lazy='dynamic', # lazy='dynamic' -> returns query so we can filter
                            cascade="all, delete-orphan", # apply delete also for childs
                            passive_deletes=True, # apply delete also for childs
                            )  # lazy='dynamic' -> returns query so we can filter
    groups = relationship('Groups',
                          backref='entry_id',  # check cascade_backrefs
                          lazy='dynamic',  # lazy='dynamic' -> returns query so we can filter
                          cascade="all, delete-orphan",  # apply delete also for childs
                          passive_deletes=True,  # apply delete also for childs
                          )  # lazy='dynamic' -> returns query so we can filter



    def __repr__(self):
        return """{}(entry_id='{}', mediawiki='{}', path='{}')""".format(
            self.__class__.__name__,
            self.entry_id,
            self.mediawiki,
            self.path)

class AssociationMainMain(Base):
   __tablename__ = 'association_main_keywords'
   parent_id = Column(Integer, ForeignKey('main.id'), primary_key=True)
   child_id = Column(Integer, ForeignKey('main.id'), primary_key=True)
   extra_data = Column(String(50))
   parent = relationship("Main",
                         foreign_keys='AssociationMainMain.parent_id',
                         back_populates="children"
                         )
   child = relationship("Main",
                        foreign_keys='AssociationMainMain.child_id',
                        back_populates="parents"
                        )

   def __repr__(self):
       return """{}(parent='{}', child='{}', extra_data='{}')""".format(self.__class__.__name__,
                                                                        self.parent.sim_id,
                                                                        self.child.sim_id,
                                                                        self.extra_data)

class Keywords(Base):
    __tablename__ = 'keywords'

    id = Column(Integer(), primary_key=True, index=True)
    main_id =  Column(Integer(), ForeignKey('main.id') , index=True)
    name  =  Column(String(255), index=True)
    value =  Column(String(255), nullable=True)

    def __repr__(self):
        return "{}(main_id='{}', name='{}', value='{}')".format(
            self.__class__.__name__,
            self.main_id,
            self.name,
            self.value)

class Groups(Base):
    __tablename__ = 'groups'

    id = Column(Integer(), primary_key=True, index=True)
    main_id =  Column(Integer(), ForeignKey('main.id') , index=True)
    name  =  Column(String(255), index=True)

    def __repr__(self):
        return "{}(main_id='{}', name='{}')".format(
            self.__class__.__name__,
            self.main_id,
            self.name)

def establish_session(db_address='sqlite:///:memory:'):
    '''
    :param db_address: ['sqlite:///:memory:', 'sqlite:///./test.db']
    :return: session
    '''
    engine = create_engine(db_address, echo=False) #  if we want spam
    # Establishing a session
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def setup_database(engine):
    """function to create the database"""
    # create Tables
    Base.metadata.create_all(engine)