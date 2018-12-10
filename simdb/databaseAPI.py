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

from simdb.databaseModel import *
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import noload
from sqlalchemy import or_, and_


def listed(alist):
    '''Convert list to comma seperated string.'''
    return ",".join("{}".format(i) for i in alist)


def open_database(db_path):
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
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def get_tags(db_path):
    """
    Function to get all tags used in a database.

    Parameters
    ----------
    db_path : str
        Path to the database

    Returns
    -------
    tags : Tuple[str]
        Unique tag list.
    """

    session = open_database(db_path=db_path)
    query = session.query(distinct(Keywords.name)).select_from(Keywords).filter(Keywords.value.is_(None))
    results = query.all()
    session.close()

    return next(iter(zip(*results)), [])


def get_keywords(db_path):
    """
    Function to get all keywords with their values as list

    Parameters
    ----------
    db_path : str
        Path to the database

    Returns
    -------
    tags : dict[str, list]
        Unique keyword dictonary.
    """

    session = open_database(db_path=db_path)
    query = session.query(Keywords.name, Keywords.value).distinct().filter(not_(Keywords.value.is_(None)))
    keywords = dict((k, list(zip(*v))[1]) for k, v in itertools.groupby(query.all(), lambda x: x[0]))
    session.close()

    return keywords


def get_groups(db_path):
    """
    Get all groups in database.

    Parameters
    ----------
    db_path : str
        Path to the database

    Returns
    -------
    groups : list[str]
        list of all groups.
    """

    session = open_database(db_path=db_path)
    groups = session.query(Groups.name).select_from(Groups).all()
    session.close()
    return groups


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

def get_entry_table(db_path, group_names=None, tags=None, columns=None):
    """Get pandas table of all entries meeting the selection creteria.
    This is maybe a better way to get entries since selection is on SQL level.

    Args:
        db_path: string, path to database
        group_names: list, names of groups, logic for groups is OR
        tags: list, logic for tags is AND
        columns: list, columns which should be displayed
    """

    # open databae
    s = open_database(db_path)
    q = s.query(Main).options(noload(Main.keywords))

    # filter by groups
    if group_names is not None:
        groups = []
        for groupname in group_names:
            try:
                # collect groups
                groups.append(s.query(Groups).filter(Groups.name == groupname).one())
            except NoResultFound:
                print("{} is not a group in selected database.".format(groupname))

        groups = [Main.groups.any(id=group.id) for group in groups]
        q = q.filter(or_(*groups))

    # filter by tags
    if tags is not None:
        tags = [and_(Main.keywords.any(name=tag), Main.keywords.any(value=None)) for tag in tags]

        q = q.filter(and_(*tags))

    # get entries as pandas table
    df = pd.read_sql(q.statement, s.bind, index_col="id")

    s.close()

    # convert output
    if columns is not None:
        df = df[columns]

    return df


def get_entry_details(db_path, entry_id):
    """Get all information about an entry in database.

    Args:
        db_path: path to database file
        entry_id: string

    Return:
        out: dictionary

    """

    s = open_database(db_path)

    # find entry
    try:
        sim = s.query(Main).filter(Main.entry_id == entry_id).one()
    except NoResultFound:
        print("No entry found with entry_id {} in {}.".format(entry_id, db_path))
        return {}

    # details from main table
    out = sim.__dict__

    # groups
    out["groups"] = [g.name for g in sim.groups]

    # tags
    out["tags"] = [t.name for t in sim.keywords if t.value == None]

    # keywords
    out["keywords"] = {k.name: k.value for k in sim.keywords if k.value != None}

    # meta data
    meta = {}
    for meta_group in sim.meta.all():
        meta[meta_group.name] = {m.name: m.value for m in meta_group.entries}
    out["meta"] = meta

    s.close()

    # clean up output
    try:
        del out["_sa_instance_state"]
    except:
        pass

    return out


def add_tag(db_path, entry_id, tag_name):
    """
    Add tag to entry.

    Parameters
    ----------
    db_path : str
        Path to the database
    entry_id : str
        Entry ID in database
    tag_name : str
        Tag name

    Returns
    -------
    True if tag was added, otherwise False
    """

    s = open_database(db_path)
    status = False

    entry = s.query(Main).filter(Main.entry_id == entry_id).first()
    if entry:

        # tag already there
        if entry.keywords_query.filter_by(name=tag_name, value=None).first():
            print("Tag already assigned to entry")

        # tagname used for keyword
        elif entry.keywords_query.filter_by(name=tag_name).first():
            print("Tag is already used for keyword. You can't add this tag. One could say that this problem might be avoided if one would use two separate tables for tags and keywords.")

        # add tag
        else:
            tag = Keywords(name=tag_name)
            entry.keywords.append(tag)
            s.commit()
            status = True

    s.close()

    return status


def remove_tag(db_path, entry_id, tag_name):
    """
    Remove tag from entry.

    Parameters
    ----------
    db_path : str
        Path to the database
    entry_id : str
        Entry ID in database
    tag_name : str
        Tag name

    Returns
    -------
    True if tag was removed otherwise False
    """

    s = open_database(db_path)
    status = False

    entry = s.query(Main).filter(Main.entry_id == entry_id).first()
    tag = entry.keywords_query.filter_by(name=tag_name, value=None).first()
    if entry and tag:
        entry.keywords.remove(tag)
        s.commit()
        status = True

    s.close()

    return status


def add_keyword(db_path, entry_id, **kwargs):
    """
    Add keywords to entry.

    Parameters
    ----------
    db_path : str
        Path to the database
    entry_id : str
        Entry ID in database
    **kwargs : kwargs
        keyword1="value1", keyword2="value2"

    Returns
    -------
    True
    """

    s = open_database(db_path)
    status = False

    entry = s.query(Main).filter(Main.entry_id == entry_id).first()
    if entry:
        status = []
        for name, value in kwargs.items():

            # keyword is already there but might be a tag or might have a different value
            if entry.keywords_query.filter_by(name=name).first():

                # keyword is already there but a tag
                if entry.keywords_query.filter_by(name=name, value=None).first():
                    print(
                        "You are trying to assing a keyword which is already used for a tag. One could say that this problem might be avoided if one would use two separate tables for tags and keywords.")
                    status.append(False)

                # keyword is already there
                else:
                    keyword = entry.keywords_query.filter_by(name=name).first()
                    print("Keyword already there: {} = {}".format(keyword.name, keyword.value))
                    status.append(False)

            # keyword is not there
            else:
                entry.keywords.append(Keywords(name=name, value=value))
                s.commit()
                status.append(True)

        status = np.any(status)

    s.close()

    return status


def alter_keyword(db_path, entry_id, **kwargs):
    """
    Alter existing keywords of entry.

    Parameters
    ----------
    db_path : str
        Path to the database
    entry_id : str
        Entry ID in database
    **kwargs : kwargs
        keyword = "value": Alter keyword to value

    Returns
    -------
    True
    """

    s = open_database(db_path)
    status = False

    entry = s.query(Main).filter(Main.entry_id == entry_id).first()
    if entry:
        status = []
        for name, value in kwargs.items():

            # keyword is there
            keyword = entry.keywords_query.filter_by(name=name).first()
            if keyword and keyword.value is not None:

                keyword.value = value
                s.commit()
                status.append(True)

            # keyword is not there
            else:
                status.append(False)

        status = np.any(status)

    s.close()

    return status


def remove_keyword(db_path, entry_id, **kwargs):
    """
    Remove keywords from entry.

    Parameters
    ----------
    db_path : str
        Path to the database
    entry_id : str
        Entry ID in database
    **kwargs : kwargs
        keyword = "value": Keyword is given, remove if entry has given value
        keyword = None : Remove keyword independent of value

    Returns
    -------
    True
    """

    s = open_database(db_path)
    status = False

    entry = s.query(Main).filter(Main.entry_id == entry_id).first()
    if entry:
        status = []
        for name, value in kwargs.items():

            # keyword is there
            keyword = entry.keywords_query.filter_by(name=name).first()
            if keyword:

                # keyword might be a tag
                if keyword.value is not None and (value == None or value == keyword.value):
                    entry.keywords.remove(keyword)
                    s.commit()
                    status.append(True)

            # keyword is not there
            else:
                status.append(False)

        status = np.any(status)

    s.close()

    return status


def add_to_group(db_path, entry_id, groupname):
    """Add all simulations in entry_id to group.

    Args:
        db_path: string, path to database
        entry_id: list, entry IDs of simulations which
                  should be added to group
        groupname: string, name of group
    """
    # check input
    if len(entry_id) == 0:
        print("No entries selected in entry_id.")
        return False
    if not hasattr(entry_id, "__iter__"):
        print("entry_id is not iterable.")
        return False

    # open databae
    s = open_database(db_path)

    # get group if already in DB or create new group
    try:
        group = s.query(Groups).filter(Groups.name == groupname).one()
    except NoResultFound:
        group = Groups(name=groupname)
        s.add(group)
        s.commit()

    entries = s.query(Main).filter(Main.entry_id.in_(entry_id)).all()

    # add
    for entry in entries:
        group.entries.append(entry)

    # commit and close
    s.commit()
    s.close()

    return True


def remove_from_group(db_path, entry_id, group_name):
    """Remove all simulations in entry_id from group.

    Args:
        db_path: string, path to database
        entry_id: list, entry IDs of simulations which
                  should be added to group
        group_name: string, name of group
    """
    # check input
    if len(entry_id) == 0:
        print("No entries selected in entry_id.")
        return False
    if not hasattr(entry_id, "__iter__"):
        print("entry_id is not iterable.")
        return False

    # open databae
    s = open_database(db_path)

    # get group if in DB
    try:
        group = s.query(Groups).filter(Groups.name == group_name).one()
    except NoResultFound:
        print("Group {} was not found in DB".format())

    # get only those entries which are in group
    entries = s.query(Main).filter(Main.groups.any(id=group.id)).filter(Main.entry_id.in_(entry_id)).all()

    # remove
    for entry in entries:
        group.entries.remove(entry)

    # commit and close
    s.commit()
    s.close()

    return True


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


#### deprecated #####
# functions below are deprecated and will be removed
# after checking that they are not used any more
# Micha: please do not remove them. get_entry_keywords / tags could be usefull
# used in app.py !

def getEntryTable(db_path, columns=["entry_id", "path", "created_on", "added_on", "updated_on", "description"], load_keys=True, load_tags=True):
    '''Get a pandas DataFrame with all entries in a data base and
    keywords and tags.'''
    s = open_database(db_path)

    # get DB tables as pandas DataFrames
    main = pd.read_sql_table("main", s.bind)[["id"] + columns].set_index('id')
    keywords_raw = pd.read_sql_table("keywords", s.bind)

    if load_keys:
        keywords = keywords_raw[keywords_raw['value'].notna()]
        if keywords.size != 0:
            # inner join to get the connection between entries and keywords
            #m = pd.merge(main, keywords, right_on="main_id", how="inner")
            # pivot table reduces it to columns
            p = keywords.pivot(index='main_id', columns='name')["value"]
            main = pd.concat([main, p], axis=1)

    if load_tags:
        tags = keywords_raw[~keywords_raw['value'].notna()]
        if tags.notna().size != 0:
            tags = tags.drop('value', axis=1).groupby("main_id").agg({"name": listed}).rename(index=int, columns={"name": "tags"})
            main = pd.concat([main, tags], axis=1)

    s.close()

    return main


def getEntryDetails(db_path, entry_id):
    s = open_database(db_path)

    sim = s.query(Main).filter(Main.entry_id == entry_id).one()
    d = sim.__dict__
    try:
        del d["_sa_instance_state"]
    except:
        pass
    out = sim.__dict__

    s.close()
    return out


def getEntryKeywords(db_path, entry_id):
    s = open_database(db_path)

    sim = s.query(Main).filter(Main.entry_id == entry_id).one()
    keywords = dict((k.name, k.value) for k in sim.keywords
                    if k.value != 'None' and k is not None)

    s.close()
    return keywords

def getEntryTags(db_path, entry_id):
    s = open_database(db_path)

    sim = s.query(Main).filter(Main.entry_id == entry_id).one()
    tags = [t.name for t in sim.keywords if t.value == "None" or t.value is None]

    s.close()
    return tags


def getEntryMeta(db_path, entry_id):
    s = open_database(db_path)

    sim = s.query(Main).filter(Main.entry_id == entry_id).one()

    out = {}
    for meta_group in sim.meta.all():
        out[meta_group.name] = {meta.name: meta.value for meta in meta_group.entries.all()}

    s.close()
    return out