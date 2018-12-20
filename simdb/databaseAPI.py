#!/usr/bin/env python
"""
# Details:
#   Database API
#   Used to access database more easily.
# Authors:
#   Andrej Berg
#   Michael King
# History:
#   -
# Last modified: 17.04.2018
# ToDo:
#   -
# Bugs:
#   -
"""

from __future__ import absolute_import

__author__ = ["Andrej Berg", "Michael King"]
__date__ = "17.04.2018"

import pandas as pd
import numpy as np
import itertools
import os

from typing import Union, List, Tuple, Optional, Any
from collections import Iterable
from simdb.databaseModel import *
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import noload
from sqlalchemy import or_, and_


Session = sessionmaker()


def connect_database(db_path):
    """
    Open data base and return session.

    Parameters
    ----------
    db_path : str
        Path to database.

    Returns
    -------
    session : sessionmaker
        SQL session

    Raises
    ------
    OSError
        If ``db_path`` not found.
    """

    if not os.path.exists(db_path):
        raise OSError("%s does not exist." % db_path)
    engine = create_engine('sqlite:///{}'.format(db_path))
    Session.configure(bind=engine)
    session = Session()
    return session


# =========================================================================== #
# get_all_functions
# =========================================================================== #

def get_all_keywords(session):
    """
    Function to get all keywords with their values as list

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session

    Returns
    -------
    tags : dict[str, list]
        Unique keyword dictonary.
    """

    query = session.query(Keywords.name, Keywords.value).distinct()
    keywords = dict((k, list(zip(*v))[1]) for k, v in itertools.groupby(query.all(), lambda x: x[0]))

    return keywords


def get_all_groups(session):
    """
    Get all groups in database.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session

    Returns
    -------
    groups : list[str]
        list of all groups.
    """

    groups = session.query(Groups.name).select_from(Groups).all()
    return groups

# =========================================================================== #
# get/set/update keywords
# =========================================================================== #


def get_keywords(session, entry_id):
    """
    Function to get the keywords for a entry_id

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    entry_id : str
        entry id in the database

    Returns
    -------
    keywords : dict
        Keywords for the entry with `entry_id`
    """
    query = session.query(Keywords.name, Keywords.value).join(Main).filter(Main.entry_id == entry_id)
    keywords = dict(query.all())
    return keywords


def add_single_keyword(session, entry_id, name, value=None, unique=True, main_id=None):
    """
    Function to add a single keyword

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    entry_id : str
        entry id in the database
    name : str
        Name of the keyword.
    value : Union[float,int,str,bool,None]
        Value of the keyword. (Default is None.)
    unique : bool
        Keyword will be assumed to be unqiue. (Default is `True`.)
    main_id : int or None
        ID in the `main` table. (Default is `None`.)
    """

    # get keyword if unique else None
    keyword = session.query(Keywords).join(Main)\
        .filter(Keywords.name == name)\
        .filter(Main.entry_id == entry_id)\
        .one_or_none() if unique else None

    # create keyword if not there or not unique else update
    if keyword is None:
        if main_id is None:
            main_id = session.query(Main.id).filter(Main.entry_id == entry_id).one()[0]
        keyword = Keywords(name=name, value=value, main_id=main_id)
    else:
        keyword.value = value
    session.add(keyword)


def update_keywords(session, entry_id, **kwargs):
    """
    Function to update / add keywords.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    entry_id : str
        entry id in the database
    kwargs : dict
        keyword name and value
    """

    keywords = session.query(Keywords).join(Main)\
        .filter(Main.entry_id == entry_id)\
        .filter(Keywords.name.in_(kwargs.keys())).all()
    for keyword in keywords:
        keyword.value = kwargs.pop(keyword.name)

    if len(keywords) != 0:
        main_id = keywords[0].main_id
    else:
        main_id = session.query(Main.id).filter(Main.entry_id == entry_id).one()[0]

    for name, value in kwargs.items():
        keywords.append(Keywords(name=name, value=value, main_id=main_id))
    session.add_all(keywords)


def set_keywords(session, entry_id, **kwargs):
    """
    Function to set keywords. Overwrites the old.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    entry_id : str
        entry id in the database
    kwargs : dict
        keyword name and value
    """
    main_id = session.query(Main.id).filter(Main.entry_id == entry_id).one()[0]
    session.query(Keywords).filter(Keywords.main_id == main_id).delete()
    for name, value in kwargs.items():
        session.add(Keywords(name=name, value=value, main_id=main_id))


def delete_keywords(session, entry_id, *args):
    """
    Function to delete keywords.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    entry_id : str
        entry id in the database
    args : List[str]

    Returns
    -------

    """
    keywords = session.query(Keywords).join(Main)\
        .filter(Main.entry_id == entry_id)\
        .filter(Keywords.name.in_(args)).all()
    for keyword in keywords:
        session.delete(keyword)


def delete_all_keywords(session, entry_id):
    """
    Function to delete all keywords for an entry.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    entry_id : str
        entry id in the database
    """
    keywords = session.query(Keywords).join(Main)\
        .filter(Main.entry_id == entry_id)\
        .all()
    for keyword in keywords:
        session.delete(keyword)


# =========================================================================== #
# get/set/update keywords
# =========================================================================== #


def add_meta_group(session, entry_id, meta_group_name, unique=True, main_id=None):
    """
    Add a meta information group/block to entry.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    entry_id : str
        entry id in the database
    meta_group_name : str
        Name of meta group, e.g. Thermostat, Barostat
    unique : bool
        Keyword will be assumed to be unqiue. (Default is `True`.)
    main_id : int or None
        ID in the `main` table. (Default is `None`.)

    Returns
    -------
    meta_group : MetaGroups
        added MetaGroups object
    """

    # get meta_group if unique else None
    meta_group = session.query(MetaGroups).join(Main)\
        .filter(MetaGroups.name == meta_group_name)\
        .filter(Main.entry_id == entry_id)\
        .one_or_none() if unique else None

    # create meta_group if not there or is not unique
    if meta_group is None:
        if main_id is None:
            main_id = session.query(Main.id).filter(Main.entry_id == entry_id).one()[0]
        meta_group = MetaGroups(name=meta_group_name, main_id=main_id)
        session.add(meta_group)

    return meta_group


def delete_meta_group(session, entry_id, meta_group_name):
    """
    Remove a meta information group/block from entry.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    entry_id : str
        entry id in the database
    meta_group_name: str
        Name of meta group, e.g. Thermostat, Barostat
    """

    meta_groups = session.query(MetaGroups).join(Main) \
        .filter(MetaGroups.name == meta_group_name)\
        .filter(Main.entry_id == entry_id) \
        .all()
    for meta_group in meta_groups:
        session.delete(meta_group)


def add_meta_data(session, entry_id, meta_group_name, unique=True, metagroup_id=None, **kwargs):
    """
    Add meta data to entry.

    Create MetaGroup if not there.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    entry_id : str
        entry id in the database
    unique : bool
        Keyword will be assumed to be unqiue. (Default is `True`.)
    main_id : int or None
        ID in the `main` table. (Default is `None`.)
    meta_group_name: str
        Name of meta group, e.g. Thermostat, Barostat
    **kwargs : kwargs
        keyword1="value1", keyword2="value2"

    Returns
    -------
    meta_entries : List[MetaEntry]
        List of added MetaEntries
    """
    meta_entries = session.query(MetaEntry).join(Main).join(MetaGroups) \
        .filter(MetaGroups.name == meta_group_name)\
        .filter(Main.entry_id == entry_id)\
        .filter(MetaEntry.name.in_(kwargs.keys()))\
        .all()

    if unique:
        for meta_entry in meta_entries:
            kwargs.pop(meta_entry.name)

    if metagroup_id is None:
        if len(meta_entries) != 0:
            metagroup_id = meta_entries[0].metagroup_id
        else:
            metagroup_id = session.query(MetaGroups.id).join(Main)\
                .filter(MetaGroups.name == meta_group_name) \
                .filter(Main.entry_id == entry_id).first()
            if len(metagroup_id) > 0:
                metagroup_id = metagroup_id[0]
            else:
                main_id = session.query(Main.id).filter(Main.entry_id == entry_id).one()[0]
                meta_group = MetaGroups(name=meta_group_name, main_id=main_id)
                session.add(meta_group)
                metagroup_id = meta_group.id

    for name, value in kwargs.items():
        meta_entries.append(MetaEntry(name=name, value=value, metagroup_id=metagroup_id))
    session.add_all(meta_entries)

    return meta_entries


def update_meta_data(session, entry_id, meta_group_name, **kwargs):
    """
    Update meta data in entry.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    entry_id : str
        entry id in the database
    meta_group_name: str
        Name of meta group, e.g. Thermostat, Barostat
    **kwargs : kwargs
        update keyword to value
        keyword = "value"

    Returns
    -------
    meta_entries : List[MetaEntry]
        List of added MetaEntries
    """

    meta_entries = session.query(MetaEntry).join(Main).join(MetaGroups) \
        .filter(MetaGroups.name == meta_group_name) \
        .filter(Main.entry_id == entry_id) \
        .filter(MetaEntry.name.in_(kwargs.keys())) \
        .all()

    for meta_entry in meta_entries:
        meta_entry.value =  kwargs.pop(meta_entry.name)

    if len(meta_entries) != 0:
        metagroup_id = meta_entries[0].metagroup_id
    else:
        metagroup_id = session.query(MetaGroups.id).join(Main) \
            .filter(MetaGroups.name == meta_group_name) \
            .filter(Main.entry_id == entry_id).first()
        if len(metagroup_id) > 0:
            metagroup_id = metagroup_id[0]
        else:
            main_id = session.query(Main.id).filter(Main.entry_id == entry_id).one()[0]
            meta_group = MetaGroups(name=meta_group_name, main_id=main_id)
            session.add(meta_group)
            metagroup_id = meta_group.id

    for name, value in kwargs.items():
        meta_entries.append(MetaEntry(name=name, value=value, metagroup_id=metagroup_id))
    session.add_all(meta_entries)

    return meta_entries

def set_meta_data(session, entry_id, meta_group_name, **kwargs):
    """
    set meta data in entry.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    entry_id : str
        entry id in the database
    meta_group_name: str
        Name of meta group, e.g. Thermostat, Barostat
    **kwargs : kwargs
        set keyword to value
        keyword = "value"

    Returns
    -------
    meta_entries : List[MetaEntry]
        List of added MetaEntries
    """

    meta_datas = session.query(MetaEntry).join(Main).join(MetaGroups) \
        .filter(MetaGroups.name == meta_group_name) \
        .filter(Main.entry_id == entry_id) \
        .all()
    for meta_data in meta_datas:
        session.delete(meta_data)

    meta_entries = add_meta_data(session=session, entry_id=entry_id,
                                 meta_group_name=meta_group_name, **kwargs)

    return meta_entries

def remove_meta_data(session, entry_id, meta_group_name, **kwargs):
    """
    Remove meta data in entry.

    Parameters
    ----------
    db_path : str
        Path to the database
    entry_id : str
        Entry ID in database
    meta_group_name: str
        Name of meta group, e.g. Thermostat, Barostat
    **kwargs : kwargs
        keyword = "value": Value is given, remove if entry has given value
        keyword = None : Remove meta data entry independent of value
    """
    meta_datas = session.query(MetaEntry).join(Main).join(MetaGroups) \
        .filter(MetaGroups.name == meta_group_name) \
        .filter(Main.entry_id == entry_id) \
        .all()
    for meta_data in meta_datas:
        session.delete(meta_data)



# =========================================================================== #
# entry table
# =========================================================================== #

def get_entry_table(session,
                    group_names=None,
                    keyword_names=None,
                    columns=('entry_id', 'path', 'owner', 'url', 'type', 'description')):
    """

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    group_names : None or Union[List,Tuple]
        names of groups, logic for groups is OR
    keyword_names : None or Union[List,Tuple]
        logic for tags is AND
    columns : Union[List,Tuple]
        columns which should be displayed

    Returns
    -------
    df : pandas.core.frame.DataFrame
        Pandas DataFrame of the entry table
    """

    # open database
    query = session.query(Main.id,*[getattr(Main,attr) for attr in columns])

    # filter by groups
    if isinstance(group_names, Iterable):
        raise NotImplementedError("database Model does not support this")
        query = query.join(Groups).filter(Groups.name.in_(group_names)).distinct()

    # filter by tags
    if isinstance(keyword_names, Iterable):
        query = query.join(Keywords)\
                     .filter(and_(Main.keywords.any(name=name) for name in keyword_names))\
                     .distinct(Main.id)

    # get entries as pandas table
    df = pd.read_sql(query.statement, session.bind, index_col="id")

    return df


def get_entry_details(session, entry_id):
    """
    Get all information about an entry in database.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    entry_id : str
        entry id

    Returns
    -------
    sim_dict : dict
        Simulation object in dictionary form.
    """

    sim = session.query(Main).filter(Main.entry_id == entry_id).one()
    if sim is None:
        return None
    else:
        return sim2dict(sim)


# =========================================================================== #
# utility functions
# =========================================================================== #

def sim2dict(sim):
    """
    Function to create a dictionary from a sim object.

    Notes
    -----
    sim_dict['children'] :
        returns a list of all `sim_dict(child)`
    sim_dict['parents'] :
        only returns a list of the parent `entry_id`

    Parameters
    ----------
    sim : Main
        Main table object

    Returns
    -------
    sim_dict : dict
        sim as dictionary

    """
    sim_dict = dict((c.name, getattr(sim, c.name)) for c in sim.__table__.columns)
    sim_dict['parents'] = sorted([entry.parent.entry_id for entry in sim.parents])

    sim_dict['children'] = sorted([sim2dict(entry.child) for entry in sim.children],
                                  key=lambda x: x['entry_id'])
    sim_dict['keywords'] = dict((k.name, k.value) for k in sim.keywords)
    return sim_dict

# TODO change group based functions after databaseModel changed
def add_group(db_path, entry_id, group_name):
    """Add simulation to group.

    Parameters
    ----------
    db_path : str
        Path to the database
    entry_id : str
        Entry ID in database
    group_name: str
        Name of group

    Returns
    -------
    True if entry was added to group, otherwise False.
    """

    # open databae
    s = connect_database(db_path)
    status = False

    entry = s.query(Main).filter(Main.entry_id == entry_id).first()

    if entry:

        # get group if already in DB or create new group
        group = s.query(Groups).filter(Groups.name == group_name).first()
        if not group:
            group = Groups(name=group_name)
            s.add(group)
            s.commit()

        group.entries.append(entry)
        s.commit()
        status = True

    s.close()

    return status


def remove_group(db_path, entry_id, group_name):
    """Remove simulation from group.

    Parameters
    ----------
    db_path : str
        Path to the database
    entry_id : str
        Entry ID in database
    group_name: str
        Name of group

    Returns
    -------
    True if entry was removed from group, otherwise False.
    """

    # open databae
    s = connect_database(db_path)
    status = False

    entry = s.query(Main).filter(Main.entry_id == entry_id).first()
    group = s.query(Groups).filter(Groups.name == group_name).first()

    if group:
        if entry in group.entries:
            group.entries.remove(entry)
            s.commit()
            status = True

    s.close()

    return status



def selectByKeyword(table, name, value):
    '''Get mask for selection of entries by keyword.'''
    return table[name] == value


def selectByTag(table, tag):
    '''Get mask for selection of entries by tag.'''
    split = table.tags.str.split(",")
    mask = [True if np.any(np.array(i[1]) == tag) else False for i in split.iteritems()]
    return pd.Series(mask, index=range(1, len(mask) + 1))

def store_dict(entry_id,
               path,
               id = None,
               owner = None,
               url = None,
               sim_type = None,
               description = None,
               created_on = None,
               # added_on = None,
               n_atoms = None,
               n_steps = None,
               time_step = None,
               raw_keywords = {},
               raw_mdp_parameters = {},
               **kwargs
              ):
    """
    Function to get a simulation object with all features.
    The function will automatically sort if the keywords belong in the right table and create the necessary
    other database objects (`Keywords`, `MetaGroups`, `MetaEntry`)

    Parameters
    ----------
    entry_id : str
        unique entry id
    path : str
        path to the simulation
    id : int, None, optional
        database ID
    owner : str, None, optional
        owner of the simulation
    url : str, None, optional
        url pointing to more informations about the simulation
    sim_type : str, None, optional
        simulation type
    description : str, None, optional
        detail description of the simulation
    created_on : datetime, None, optional
        Datetime object (use `datetime.fromtimestamp(UNIXSTRING)`)
    n_atoms : int, None, optional
        total number of atoms in the system
    n_steps : int, None, optional
        number of simulation steps
    time_step : float, None, optional
        used timestep (in [ps])
    raw_keywords : dict, optional
        Dictionary of `(keyword, value)` that should be added as keywords
    raw_mdp_parameters : dict, optional
        Dictionary of mdp parameters as named in the database.
        If the `value` of `(keyword, value)` is a dictionary.
        The `value`-dictionary with be added in `MetaGroups` with `name = keyword`
        and all `(k, v)` of `value` assigned as `MetaEntry`.
    kwargs : dict
        Other kwargs.
        Mainly interesting to provide lists of database models for
        `keywords`, `meta` , `groups`, `children`, `parents`

    Returns
    -------
    Main
        returns a simulation object with all values assigned.
    """

    input_kwargs = locals()
    _main_kwargs = [i for i in vars(Main).keys() if not i.startswith("_")]
    
    main_kwargs = dict( (k,v) for k,v in input_kwargs.iteritems() if k in _main_kwargs and v is not None)
    # update main by mdp parameters
    for k in raw_mdp_parameters.keys()[:]:
        if k in _main_kwargs:
            main_kwargs[k] = raw_mdp_parameters[k]
            del raw_mdp_parameters[k]
    
    # update main by mdp_parameters
    for k in raw_keywords.keys()[:]:
        if k in _main_kwargs:
            main_kwargs[k] = raw_keywords[k]
            del raw_keywords[k]
    
    keywords = [] if not 'keywords' in kwargs or kwargs['keywords'] is None else  kwargs['keywords']
    keywords.extend([Keywords(name=k,value=v) for k,v in raw_keywords.iteritems()])
    
    # update keywords
    if len(keywords) != 0:
        main_kwargs['keywords'] = keywords 
    

    metagroups = [] if not 'meta' in kwargs or kwargs['meta'] is None else kwargs['meta']
    
    for key in raw_mdp_parameters.keys()[:]:
        value = raw_mdp_parameters[key]
        if type(value) == dict:
            metagroups.append(
                MetaGroups(
                    name=key,
                    entries=[MetaEntry(name=k,value=v) for k,v in value.iteritems()],
                          )
            )
    
    # update meta
    if len(metagroups) != 0:
        main_kwargs['meta'] = metagroups 
        
    # create sim
    sim = Main(**main_kwargs)
    
    return sim


