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
import sys
from warnings import warn
from typing import Union, List, Tuple, Optional, Any
from collections import Iterable

from contextlib import contextmanager
from simdb.databaseModel import *
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import noload
from sqlalchemy import or_, and_

# define string types
string_types = str if sys.version_info[0] == 3 else basestring

session_info = {
    "SIMDB_PRIORITY" : 0
}
Session = sessionmaker(info=session_info)


def create_new_database(db_path, priority=None):
    """
    Creates a new database.

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
    IOError
        If ``db_path`` not found.
    """
    if os.path.exists(db_path):
        raise IOError("%s does exist." % db_path)
    engine = create_engine('sqlite:///{}'.format(db_path))
    Session.configure(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)

    session.info["SIMDB_PRIORITY"] = priority or session.info["SIMDB_PRIORITY"]

    return session


def connect_database(db_path, priority=None):
    """
    Open database and return session.

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
    IOError
        If ``db_path`` not found.
    """

    if not os.path.exists(db_path):
        raise IOError("%s does not exist." % db_path)
    engine = create_engine('sqlite:///{}'.format(db_path))
    Session.configure(bind=engine)
    session = Session()

    session.info["SIMDB_PRIORITY"] = priority or session.info["SIMDB_PRIORITY"]

    return session


@contextmanager
def session_handler(db_path, create=False, priority=None):
    """
    Context manager for sessions.

    Parameters
    ----------
    db_path : str
        Database path.
    mode : str
        'r' for read
        'w' for write

    Yields
    ------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session

    Raises
    ------
    IOError
        If file does not exist and create is ``False``.
    """
    if os.path.exists(db_path) or create:
        engine = create_engine('sqlite:///{}'.format(db_path))
        Session.configure(bind=engine)
        session = Session()
        session.info["SIMDB_PRIORITY"] = priority or session.info["SIMDB_PRIORITY"]
    else:
        raise IOError("No such file or directory: '{}'".format(db_path))
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        Session.configure(bind=None)
        session.close()

# =========================================================================== #
# get_all_functions
# =========================================================================== #

def get_all_keywords(session, groups=None, count=False):
    """
    Function to get all keywords.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    groups : list(str)
        list of groups for selection
    count : bool
        return count together with keywords and
        values list(tuple(str, int))

    Returns
    -------
    out : list(str)
        Unique keyword list.
    """

    if groups:

        keywords = session.query(Keywords.name).join(Main) \
            .join(association_main_groups) \
            .join(Groups).filter(Groups.name.in_(groups)).distinct().all()
        keywords = [k[0] for k in keywords]

        if count:
            q = session.query(Main.entry_id).filter(Groups.name.in_(groups)).join(Keywords)
            keyword_counts = [q.filter(Keywords.name == k).distinct().count() for k in keywords]

    else:

        # no groups selected
        keywords = session.query(Keywords.name).distinct().all()
        keywords = [k[0] for k in keywords]

        if count:
            q = session.query(Main.entry_id).join(Keywords)
            keyword_counts = [q.filter(Keywords.name == k).distinct().count() for k in keywords]

    if count:
        out = list(zip(keywords, keyword_counts))
    else:
        out = keywords

    if len(out) == 0:
        return None
    else:
        return out


def get_all_keyword_values(session, keyword_name, groups=None, count=False):
    """
        Function to get all values of certain keyword.

        Parameters
        ----------
        session : sqlalchemy.orm.session.Session
            SQL Alchemy session
        groups : list(str)
            list of groups for selection
        count : bool
            return count together with keywords and
            values list(tuple(str, int))

        Returns
        -------
        out : list(str)
            Unique keyword list.
        """

    if groups:

        values = session.query(Keywords.value).join(Main) \
            .join(association_main_groups) \
            .join(Groups).filter(Groups.name.in_(groups)) \
            .filter(Keywords.name == keyword_name).distinct().all()
        values = [v[0] for v in values]

        if count:
            q = session.query(Main.entry_id).filter(Groups.name.in_(groups)).join(Keywords)
            value_counts = [q.filter(Keywords.name == keyword_name, Keywords.value == v).distinct().count() for v in
                            values]

    else:

        values = session.query(Keywords.value).filter_by(name=keyword_name).distinct().all()
        values = [v[0] for v in values]

        if count:
            q = session.query(Main.entry_id).join(Keywords)
            value_counts = [q.filter(Keywords.name == keyword_name, Keywords.value == v).distinct().count() for v in
                            values]

    if count:
        out = list(zip(values, value_counts))
    else:
        out = values

    return out


def get_all_groups(session, count=False):
    """
    Get all groups in database.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    count : bool
        return counts for entries in groups
        together with group names list((str, i))

    Returns
    -------
    groups : list[str]
        list of all groups.
    """
    groups = session.query(Groups.name).select_from(Groups).all()
    groups = [g[0] for g in groups]
    if count:
        group_counts = [session.query(Main.entry_id).filter(Main.groups.any(name=g)).count() for g in groups]
        groups = list(zip(groups, group_counts))

    if len(groups) == 0:
        return None
    else:
        return groups


# =========================================================================== #
# entry table
# =========================================================================== #

def get_entry_table(session,
                    group_names=None,
                    keyword_names=None,
                    apply_filter=None,
                    columns=('entry_id', 'path', 'owner', 'url', 'type', 'description'),
                    order_by='id',
                    order='assending',
                    groups_logic="OR",
                    keywords_logic="OR"):
    """

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    group_names : None or Union[List,Tuple]
        names of groups, logic for groups is OR
    keyword_names : None or Union[List,Tuple]
        logic for keywords is AND
    apply_filter: None or sqlalchemy.sql.selectable.Exists
        this is a way to perform a more complex selection
        i.e. Main.keywords.any(name="keyword1", value="value1")
             and_(Main.keywords.any(name="keyword1", value="v1"), Main.keywords.any(name="keyword2", value="v2"))
    columns : Union[List,Tuple]
        columns which should be displayed
    order_by : None or str
        Whether results should be sorted or not.
    order : str
        `ascending` or `descending`

    Returns
    -------
    df : pandas.core.frame.DataFrame
        Pandas DataFrame of the entry table
    """

    # open database
    query = session.query(Main.id, *[getattr(Main, attr) for attr in columns])

    # filter by groups
    if isinstance(group_names, Iterable):
        # handle str or list/tuple
        if isinstance(group_names, string_types):
            query = query.filter(Groups.name == group_names)
        else:
            if groups_logic == "OR":
                query = query.filter(or_(*[Main.groups.any(name=group) for group in group_names]))
            elif groups_logic == "AND":
                query = query.filter(and_(*[Main.groups.any(name=group) for group in group_names]))
            else:
                raise Exception("{} is not a valid option for groups_logic".format(groups_logic))

    # filter by keywords
    if isinstance(keyword_names, Iterable):
        if isinstance(keyword_names, string_types):
            query = query.filter(Keywords.name == keyword_names)
        else:
            if keywords_logic == "OR":
                query = query.filter(or_(*[Main.keywords.any(name=keyword) for keyword in keyword_names]))
            elif keywords_logic == "AND":
                query = query.filter(and_(*[Main.keywords.any(name=keyword) for keyword in keyword_names]))
            else:
                raise Exception("{} is not a valid option for keywords_logic".format(keywords_logic))

    # apply additional filter
    if apply_filter is not None:
        query = query.filter(apply_filter)

    query = query.distinct(Main.id)

    if order_by is not None:
        if isinstance(order_by, string_types):
            order_by = getattr(Main, order_by, 'id')
        if order == 'ascending':
            query = query.order_by(order_by.asc())
        elif order == 'descending':
            query = query.order_by(order_by.desc())
        else:
            query = query.order_by(order_by)

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

    sim_dict['groups'] = [g.name for g in sim.groups]
    return sim_dict


# =========================================================================== #
# add/update entries
# =========================================================================== #

def add_entry(session, entry_id, priority=None, **kwargs):
    """
    Placeholder function.
    """

    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]

    entry = session.query(Main).filter(Main.entry_id == entry_id).first()

    if entry is not None:

        print("entry_id='{}' already in DB. Use update_entry().".format(entry_id))

    else:

        entry = Main(entry_id=entry_id, priority=priority, **kwargs)
        session.add(entry)


def update_entry(session, entry_id, priority=None, **kwargs):
    """
    Placeholder function.
    """

    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]

    entry = session.query(Main).filter(Main.entry_id == entry_id).first()

    if entry is not None:

        if priority >= entry.priority:
            entry.priority = priority
            for name, value in kwargs.items():
                setattr(entry, name, value)

    else:

        entry = Main(entry_id=entry_id, priority=priority, **kwargs)
        session.add(entry)


def delete_entry(session, entry_id, priority=None):
    """
    Placeholder function.
    """

    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]

    entry = session.query(Main).filter(Main.entry_id == entry_id).first()

    if entry is not None:
        if priority >= entry.priority:
            session.delete(entry)


# =========================================================================== #
# get/set/update keywords
# =========================================================================== #


def get_keywords(session, entry_id):
    """
    Function to get the `Keywords` for a `entry_id`.

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


def add_single_keyword(session, entry_id, name, value=None, unique=True, main_id=None, priority=None):
    """
    Function to add a single `Keyword`.

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

    # evaluate priority
    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]

    # get keyword if unique else None
    keyword = session.query(Keywords).join(Main)\
        .filter(Keywords.name == name)\
        .filter(Main.entry_id == entry_id)\
        .one_or_none() if unique else None

    # create keyword if not there or not unique else update
    if keyword is None:
        if main_id is None:
            main_id = session.query(Main.id).filter(Main.entry_id == entry_id).one()[0]
        keyword = Keywords(name=name, value=value, main_id=main_id, priority=priority)
    else:
        if priority >= keyword.priority:
            keyword.priority = priority
            keyword.value = value

    session.add(keyword)


def update_keywords(session, entry_id, priority=None, **kwargs):
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

    # evaluate priority
    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]

    keywords = session.query(Keywords).join(Main)\
        .filter(Main.entry_id == entry_id)\
        .filter(Keywords.name.in_(kwargs.keys())).all()
    for keyword in keywords:
        if priority >= keyword.priority:
            keyword.priority = priority
            keyword.value = kwargs.pop(keyword.name)

    if len(keywords) != 0:
        main_id = keywords[0].main_id
    else:
        main_id = session.query(Main.id).filter(Main.entry_id == entry_id).one()[0]

    for name, value in kwargs.items():
        keywords.append(Keywords(name=name, value=value, main_id=main_id, priority=priority))
    session.add_all(keywords)


def set_keywords(session, entry_id, priority=None, **kwargs):
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

    # evaluate priority
    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]

    main_id = session.query(Main.id).filter(Main.entry_id == entry_id).one()[0]
    keywords = session.query(Keywords).filter(Keywords.main_id == main_id).all()
    for keyword in keywords:
        if priority >= keyword.priority:
            session.delete(keyword)

    # for name, value in kwargs.items():
    #     session.add(Keywords(name=name, value=value, main_id=main_id))
    update_keywords(session, entry_id, priority=priority, **kwargs)


def delete_keywords(session, entry_id, priority=None, *args):
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

    # evaluate priority
    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]

    keywords = session.query(Keywords).join(Main)\
        .filter(Main.entry_id == entry_id)\
        .filter(Keywords.name.in_(args)).all()
    for keyword in keywords:
        if priority >= keyword.priority:
            session.delete(keyword)


def delete_all_keywords(session, entry_id, priority=None):
    """
    Function to delete all keywords for an entry.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    entry_id : str
        entry id in the database
    """
    # evaluate priority
    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]

    keywords = session.query(Keywords).join(Main)\
        .filter(Main.entry_id == entry_id)\
        .all()
    for keyword in keywords:
        if priority >= keyword.priority:
            session.delete(keyword)


# =========================================================================== #
# get/set/update Meta Data
# =========================================================================== #

def get_meta_groups(session, entry_id, as_list=False):
    """
    Function to get the `MetaGroups` for a `entry_id`.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    entry_id : str
        entry id in the database
    as_list : bool
        The result should be returned as list of tuples. This avoids problems with double namings.
        Default is `False`.

    Returns
    -------
    keywords : list or dict
        MetaGroups for the entry with `entry_id`.
        The output format is controlled via `as_list`.

    Warns
    -----
    UserWarning :
        If multiple `MetaGroups` have the same name.
    UserWarning :
        If multiple `MetaEntry` in a `MetaGroups` have the same name.
    """
    metagroups = session.query(MetaGroups).join(Main)\
        .filter(Main.entry_id == entry_id)\
        .order_by(MetaGroups.name).all()
    if as_list:
        return [(metagroup.name, metagroup.to_list()) for metagroup in metagroups]
    else:
        tmp = [(metagroup.name, metagroup.to_dict()) for metagroup in metagroups]
        as_dict = dict(tmp)
        if len(tmp) != len(as_dict):
            warn("Some MetaGroups is not shown in dict form due to doubled names.")
        return as_dict


def get_single_meta_group(session, entry_id, name, as_list=False):
    """
    Function to get the `MetaGroups` for a `entry_id`.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    entry_id : str
        entry id in the database
    name : str
        Name of the MetaGroup.
    as_list : bool
        The result should be returned as list of tuples. This avoids problems with double namings.
        Default is `False`.

    Returns
    -------
    keywords : list or dict
        MetaGroups for the entry with `entry_id`.
        The output format is controlled via `as_list`.

    Warns
    -----
    UserWarning :
        If multiple `MetaGroups` have the same name.
    UserWarning :
        If multiple `MetaEntry` in a `MetaGroups` have the same name.
    """
    metagroup = session.query(MetaGroups).join(Main)\
        .filter(Main.entry_id == entry_id)\
        .filter(MetaGroups.name == name).one_or_none()
    if metagroup is None:
        return None
    return metagroup.to_list() if as_list else metagroup.to_dict()

def add_meta_group(session, entry_id, meta_group_name, unique=True, main_id=None, priority=None):
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

    # evaluate priority
    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]

    # get meta_group if unique else None
    meta_group = session.query(MetaGroups).join(Main)\
        .filter(MetaGroups.name == meta_group_name)\
        .filter(Main.entry_id == entry_id)\
        .one_or_none() if unique else None

    # create meta_group if not there or is not unique
    if meta_group is None:
        if main_id is None:
            main_id = session.query(Main.id).filter(Main.entry_id == entry_id).one()[0]
        meta_group = MetaGroups(name=meta_group_name, main_id=main_id, priority=priority)
        session.add(meta_group)
    else:
        meta_group.priority = max(priority, meta_group.priority)

    return meta_group


def delete_meta_group(session, entry_id, meta_group_name, priority=None):
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

    # evaluate priority
    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]

    meta_groups = session.query(MetaGroups).join(Main) \
        .filter(MetaGroups.name == meta_group_name)\
        .filter(Main.entry_id == entry_id) \
        .all()
    for meta_group in meta_groups:
        if priority >= meta_group.priority:
            session.delete(meta_group)


def add_meta_data(session, entry_id, meta_group_name, unique=True, metagroup_id=None, priority=None, **kwargs):
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

    # evaluate priority
    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]

    meta_entries = session.query(MetaEntry).join(MetaGroups) \
        .filter(MetaGroups.name == meta_group_name)\
        .filter(MetaEntry.metagroup_id == MetaGroups.id)\
        .filter(MetaGroups.main_id == entry_id)\
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
            if metagroup_id is not None and len(metagroup_id) > 0:
                metagroup_id = metagroup_id[0]
            else:
                main_id = session.query(Main.id).filter(Main.entry_id == entry_id).one()[0]
                meta_group = MetaGroups(name=meta_group_name, main_id=main_id, priority=priority)
                session.add(meta_group)
                session.flush()
                metagroup_id = meta_group.id
    for name, value in kwargs.items():
        meta_entries.append(MetaEntry(name=name, value=value, metagroup_id=metagroup_id, priority=priority))
    session.add_all(meta_entries)

    return meta_entries


def update_meta_data(session, entry_id, meta_group_name, priority=None, **kwargs):
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

    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]

    # get id of meta group, None if meta group does not exist
    metagroup_id = session.query(MetaGroups.id).join(Main) \
        .filter(MetaGroups.name == meta_group_name) \
        .filter(Main.entry_id == entry_id).first()

    if metagroup_id is not None:

        # meta group exists
        metagroup_id = metagroup_id[0]

        # get all meta entries for selected group and db entry which should be updated
        meta_entries = session.query(MetaEntry).join(MetaGroups).join(Main) \
            .filter(MetaGroups.id == metagroup_id)\
            .filter(MetaEntry.name.in_(kwargs.keys())) \
            .all()

        # update existing meta entries, remove updated from kwargs
        for meta_entry in meta_entries:
            if priority >= meta_entry.priority:
                meta_entry.value = kwargs.pop(meta_entry.name)
                meta_entry.priority = priority

    else:

        # create new meta group
        meta_entries = []
        main_id = session.query(Main.id).filter(Main.entry_id == entry_id).one()[0]
        meta_group = MetaGroups(name=meta_group_name, main_id=main_id, priority=priority)
        session.add(meta_group)
        session.flush()
        metagroup_id = meta_group.id

    # add missing meta entries to group
    for name, value in kwargs.items():
        meta_entries.append(MetaEntry(name=name, value=value, metagroup_id=metagroup_id, priority=priority))
    session.add_all(meta_entries)

    return meta_entries

def set_meta_data(session, entry_id, meta_group_name, priority=None, **kwargs):
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

    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]

    meta_datas = session.query(MetaEntry).join(MetaGroups).join(Main) \
        .filter(MetaGroups.name == meta_group_name) \
        .filter(Main.entry_id == entry_id) \
        .all()
    for meta_data in meta_datas:
        if priority >= meta_data.priority:
            session.delete(meta_data)

    meta_entries = update_meta_data(session=session, entry_id=entry_id,
                                    meta_group_name=meta_group_name, priority=priority, **kwargs)

    return meta_entries

def remove_meta_data(session, entry_id, meta_group_name, priority=None, **kwargs):
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

    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]

    meta_datas = session.query(MetaEntry).join(MetaGroups).join(Main) \
        .filter(MetaGroups.name == meta_group_name) \
        .filter(Main.entry_id == entry_id) \
        .filter(MetaEntry.name.in_(kwargs.keys())) \
        .all()

    for meta_data in meta_datas:
        value = kwargs.get(meta_data.name)
        if priority >= meta_data.priority and (value is None or value == meta_data.value):
            session.delete(meta_data)



# =========================================================================== #
# MANAGE GROUPS                                                               #
# =========================================================================== #

def add_group(session, group_name, priority=None):
    """Add group to database.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    group_name: str
        Name of group
    priority: int or None
        use session priority if None
    """

    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]
    group = session.query(Groups).filter(Groups.name == group_name).first()

    if not group:
        group = Groups(name=group_name, priority=priority)
        session.add(group)
    else:
        if priority >= group.priority:
            group.priority = priority


def remove_group(session, group_name, priority=None):
    """Remove group from database.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    group_name: str
        Name of group
    priority: int or None
        use session priority if None
    """

    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]
    group = session.query(Groups).filter(Groups.name == group_name).first()

    if group:
        if priority >= group.priority:
            session.delete(group)


def rename_group(session, group_name, new_group_name, priority=None):
    """Rename group in database.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    group_name: str
        Name of group
    new_group_name: str
        Name of group
    priority: int or None
        use session priority if None
    """

    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]
    group = session.query(Groups).filter(Groups.name == group_name).first()

    if group:
        if priority >= group.priority:
            group.name = new_group_name
            group.priority = priority


def add_to_group(session, entry_id, group_name, priority=None):
    """Add simulation to group.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    entry_id : str
        Entry ID in database
    group_name: str
        Name of group
    priority: int or None
        use session priority if None
    """
    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]
    entry = session.query(Main).filter(Main.entry_id == entry_id).first()

    if entry:

        # get group if already in DB or create new group
        group = session.query(Groups).filter(Groups.name == group_name).first()
        if not group:
            group = Groups(name=group_name, priority=priority)
            session.add(group)

        if group not in entry.groups:
            entry.groups.append(group)



def remove_from_group(session, entry_id, group_name):
    """Remove simulation from group.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    entry_id : str
        Entry ID in database
    group_name: str
        Name of group
    """

    entry = session.query(Main).filter(Main.entry_id == entry_id).first()
    group = session.query(Groups).filter(Groups.name == group_name).first()

    if group:
        if entry in group.entries:
            group.entries.remove(entry)


def get_group_keywords(session, group_name):
    """
    Function to get the `Keywords` for a group.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    group_name : str
        group name in the database

    Returns
    -------
    group_keywords : dict
        Keywords for the group
    """
    group = session.query(Groups).filter(Groups.name == group_name).first()

    if group is not None:

        return dict([(k.name, k.value) for k in group.keywords])

    else:

        raise NoResultFound("group_name = '{}' was not found in database.".format(group_name))


def update_group_keywords(session, group_name, priority=None, **kwargs):
    """
    Function to update / add group keywords.
    Will create new group if group is not in database.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    group_name : str
        group name in the database
    kwargs : dict
        keyword name and value
    priority: int or None
        use session priority if None
    """

    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]
    group = session.query(Groups).filter(Groups.name == group_name).first()

    if group is not None:

        # update existing group keywords
        group_keywords = group.keywords_query.filter(GroupKeywords.name.in_(kwargs.keys())).all()
        for keyword in group_keywords:
            if priority >= keyword.priority:
                keyword.value = kwargs.pop(keyword.name)
                keyword.priority = priority

    else:

        # create new group
        group = Groups(name=group_name, priority=priority)
        session.add(group)

    # add missing keywords
    for name, value in kwargs.items():
        group.keywords.append(GroupKeywords(name=name, value=value, priority=priority))


def delete_group_keywords(session, group_name, group_keywords, priority=None):
    """
    Function to delete a list of keyword of a group.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    group_name : str
        group name in the database
    group_keywords : list(str)
        keyword names of group
    priority: int or None
        use session priority if None
    """

    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]
    group_keyword = session.query(GroupKeywords).filter(Groups.name == group_name) \
        .filter(GroupKeywords.name.in_(group_keywords)).all()

    for keyword in group_keyword:
        if priority >= keyword.priority:
            session.delete(keyword)


def delete_all_group_keywords(session, group_name, priority=None):
    """
    Function to delete all keywords of a group.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    group_name : str
        group name in the database
    priority: int or None
        use session priority if None
    """

    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]
    group = session.query(Groups).filter(Groups.name == group_name).first()

    if group is not None:

        for keyword in group.keywords:
            if priority >= keyword.priority:
                session.delete(keyword)

    else:

        raise NoResultFound("group_name = '{}' was not found in database.".format(group_name))


def set_group_keywords(session, group_name, priority=None, **kwargs):
    """
    Function to set group keywords. Overwrites the old!

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    group_name : str
        group_name in the database
    kwargs : dict
        keyword name and value
    priority: int or None
        use session priority if None
    """

    priority = priority if priority is not None else session.info["SIMDB_PRIORITY"]
    delete_all_group_keywords(session, group_name, priority=priority)
    update_group_keywords(session, group_name, priority=priority, **kwargs)




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
    input_kwargs['type'] = input_kwargs.pop('sim_type')
    _main_kwargs = [i for i in vars(Main).keys() if not i.startswith("_")]
    
    main_kwargs = dict( (k,v) for k,v in input_kwargs.items() if k in _main_kwargs and v is not None)
    # update main by mdp parameters
    for k in list(raw_mdp_parameters.keys())[:]:
        if k in _main_kwargs:
            main_kwargs[k] = raw_mdp_parameters[k]
            del raw_mdp_parameters[k]
    
    # update main by mdp_parameters
    for k in list(raw_keywords.keys())[:]:
        if k in _main_kwargs:
            main_kwargs[k] = raw_keywords[k]
            del raw_keywords[k]
    
    keywords = [] if not 'keywords' in kwargs or kwargs['keywords'] is None else  kwargs['keywords']
    keywords.extend([Keywords(name=k,value=v) for k,v in raw_keywords.items()])
    
    # update keywords
    if len(keywords) != 0:
        main_kwargs['keywords'] = keywords 
    

    metagroups = [] if not 'meta' in kwargs or kwargs['meta'] is None else kwargs['meta']
    
    for key in list(raw_mdp_parameters.keys())[:]:
        value = raw_mdp_parameters[key]
        if type(value) == dict:
            metagroups.append(
                MetaGroups(
                    name=key,
                    entries=[MetaEntry(name=k,value=v) for k,v in value.items()],
                          )
            )
        else:
            raise UserWarning("Dictionary is needed but got type={} for {}.".format(type(value), value))
    
    # update meta
    if len(metagroups) != 0:
        main_kwargs['meta'] = metagroups 
        
    # create sim
    sim = Main(**main_kwargs)
    
    return sim


# DEPRICATED
# def selectByKeyword(table, name, value):
#     '''Get mask for selection of entries by keyword.'''
#     return table[name] == value
#
#
# def selectByTag(table, tag):
#     '''Get mask for selection of entries by tag.'''
#     split = table.tags.str.split(",")
#     mask = [True if np.any(np.array(i[1]) == tag) else False for i in split.items()]
#     return pd.Series(mask, index=range(1, len(mask) + 1))