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
import os

from simdb.databaseModel import *


def listed(alist):
    '''Convert list to comma seperated string.'''
    return ",".join("{}".format(i) for i in alist)

def openDatabase(db_path):
    '''Open data base and return session.'''
    if not os.path.exists(db_path):
        raise "%s does not exist."
    engine = create_engine('sqlite:///{}'.format(db_path))
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def getTags(db_path):
    '''Get all tags which are used in a database.'''
    s = openDatabase(db_path)
    q = s.query(Keywords).filter(Keywords.value == None)
    s.close()
    return np.unique([e.name for e in q.all()])

def getKeywords(db_path):
    '''Get all keywords with their values which are used in a database.'''
    s = openDatabase(db_path)
    q = s.query(Keywords)
    keywords = [e.name for e in q.filter(Keywords.value != None).all()]
    key_dict = {}
    for k in np.unique(keywords):
        key_dict[k] = np.unique([e.value for e in q.filter(Keywords.value != None, Keywords.name == k).all()])
    s.close()
    return key_dict

def getEntryTable(db_path, columns=["entry_id", "path", "created_on", "added_on", "updated_on", "description"], load_keys=True, load_tags=True):
    '''Get a pandas DataFrame with all entries in a data base and
    keywords and tags.'''
    s = openDatabase(db_path)

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
    s = openDatabase(db_path)

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
    s = openDatabase(db_path)

    sim = s.query(Main).filter(Main.entry_id == entry_id).one()
    keywords = sim.keywords.all()
    keywords = {k.name: k.value for k in keywords if k.value != None}

    s.close()
    return keywords

def getEntryTags(db_path, entry_id):
    s = openDatabase(db_path)

    sim = s.query(Main).filter(Main.entry_id == entry_id).one()
    tags = sim.keywords.all()
    tags = [t.name for t in tags if t.value == None]

    s.close()
    return tags


def getEntryMeta(db_path, entry_id):
    s = openDatabase(db_path)

    sim = s.query(Main).filter(Main.entry_id == entry_id).one()

    out = {}
    for meta_group in sim.meta.all():
        out[meta_group.name] = {meta.name: meta.value for meta in meta_group.entries.all()}

    s.close()
    return out



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