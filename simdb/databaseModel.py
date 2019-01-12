"""
Database Model
"""

from warnings import warn

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy import DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import not_, and_, or_, any_, all_, distinct
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

association_main_groups = Table('association_main_groups', Base.metadata,
    Column('main_id', Integer, ForeignKey('main.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)


class Main(Base):
    __tablename__ = 'main'

    id = Column(Integer(), primary_key=True, index=True)
    entry_id =  Column(String(50), unique=True, index=True) # should be discussed

    path = Column(String(255))
    owner = Column(String(50), nullable=True)
    url = Column(String(255), nullable=True)

    type = Column(String(20), nullable=True)
    description = Column(String(1023), nullable=True) # maybe longer in the future

    created_on = Column(DateTime(), nullable=True)
    added_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    # book keeping
    priority = Column(Integer(), default=0)

    children = relationship('AssociationMainMain',
                            back_populates="parent",
                            foreign_keys='AssociationMainMain.parent_id',
                            cascade="all, delete-orphan",  # apply delete also for entries in assosiation
                            passive_deletes=True,  # apply delete also for entries in assosiation
                            lazy='joined'
                            )

    children_query = relationship('AssociationMainMain',
                                  foreign_keys='AssociationMainMain.parent_id',
                                  lazy='dynamic', viewonly=True
                                  )

    parents = relationship('AssociationMainMain',
                           back_populates="child",
                           foreign_keys='AssociationMainMain.child_id',
                           cascade="all, delete-orphan",  # apply delete also for entries in assosiation
                           passive_deletes=True,  # apply delete also for entries in assosiation
                           lazy='joined'
                           )

    parents_query = relationship('AssociationMainMain',
                                  foreign_keys='AssociationMainMain.child_id',
                                  lazy='dynamic', viewonly=True
                                 )

    keywords = relationship('Keywords',
                            backref='entry_id' , # check cascade_backrefs
                            lazy='joined', # lazy='joined' -> we can join this
                            cascade="all, delete-orphan", # apply delete also for childs
                            passive_deletes=True, # apply delete also for childs
                            )

    keywords_query = relationship('Keywords',
                            lazy='dynamic', # lazy='dynamic' -> returns query so we can filter
                            viewonly=True, # only a view
                            )  # lazy='dynamic' -> returns query so we can filter

    meta = relationship('MetaGroups',
                            backref='entry_id',  # check cascade_backrefs
                            lazy='dynamic',  # lazy='dynamic' -> returns query so we can filter
                            cascade="all, delete-orphan",  # apply delete also for childs
                            passive_deletes=True,  # apply delete also for childs
                            )  # lazy='dynamic' -> returns query so we can filter

    groups = relationship('Groups',
                          secondary=association_main_groups,
                          back_populates='entries',
                          # lazy='dynamic',  # lazy='dynamic' -> returns query so we can filter
                          # cascade="all, delete-orphan",  # apply delete also for groups
                          # passive_deletes=True,  # apply delete also for childs
                          )




    def __repr__(self):
        return """{}(entry_id='{}', mediawiki='{}', path='{}')""".format(
            self.__class__.__name__,
            self.entry_id,
            self.url,
            self.path)

class AssociationMainMain(Base):
   __tablename__ = 'association_main_main'
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
                                                                        self.parent.id,
                                                                        self.child.id,
                                                                        self.extra_data)

class Keywords(Base):
    __tablename__ = 'keywords'

    id = Column(Integer(), primary_key=True, index=True)
    main_id =  Column(Integer(), ForeignKey('main.id') , index=True)
    name  =  Column(String(255), index=True)
    value =  Column(String(255), nullable=True)
    priority = Column(Integer(), default=0)

    def __repr__(self):
        return "{}(main_id='{}', name='{}', value='{}')".format(
            self.__class__.__name__,
            self.main_id,
            self.name,
            self.value)

class Groups(Base):
    __tablename__ = 'groups'

    id = Column(Integer(), primary_key=True, index=True)
    name  =  Column(String(255), unique=True)
    priority = Column(Integer(), default=0)

    entries = relationship('Main',
                           secondary=association_main_groups,
                           back_populates='groups',
                           # lazy='dynamic',  # lazy='dynamic' -> returns query so we can filter
                           # cascade="all, delete-orphan",  # apply delete also for groups
                           # passive_deletes=True,  # apply delete also for childs
                           )

    def __repr__(self):
        return "{}(name='{}')".format(
            self.__class__.__name__,
            self.name)


class MetaGroups(Base):
    __tablename__ = 'metagroups'

    id = Column(Integer(), primary_key=True, index=True)
    main_id =  Column(Integer(), ForeignKey('main.id') , index=True)
    name  =  Column(String(255), index=True)
    priority = Column(Integer(), default=0)

    entries = relationship('MetaEntry',
                            backref='main_id' , # check cascade_backrefs
                            lazy='dynamic', # lazy='dynamic' -> returns query so we can filter
                            cascade="all, delete-orphan", # apply delete also for childs
                            passive_deletes=True, # apply delete also for childs
                            )  # lazy='dynamic' -> returns query so we can filter
    def to_list(self):
        return [(entry.name, entry.value) for entry in self.entries]

    def to_dict(self):
        as_list = self.to_list()
        rv = dict(as_list)
        if len(as_list) != len(rv):
            warn("Some MetaEntry is not shown in dict form due to doubled names.")
        return rv

    def __repr__(self):
        return "{cls_name}(main_id='{main_id}', name='{name}')".format(
            cls_name=self.__class__.__name__,
            main_id=self.main_id,
            name=self.name,
           )

class MetaEntry(Base):
    __tablename__ = 'metaentry'

    id = Column(Integer(), primary_key=True, index=True)
    metagroup_id =  Column(Integer(), ForeignKey('metagroups.id') , index=True)
    name  =  Column(String(255), index=True)
    value =  Column(String(255), nullable=True)
    priority = Column(Integer(), default=0)

    def __repr__(self):
        return "{cls_name}(metagroup_id='{metagroup_id}', name='{name}', value='{value}')".format(
            cls_name=self.__class__.__name__,
            metagroup_id=self.metagroup_id,
            name=self.name,
            value=self.value)

def setup_database(engine):
    """function to create the database"""
    # create Tables
    Base.metadata.create_all(engine)