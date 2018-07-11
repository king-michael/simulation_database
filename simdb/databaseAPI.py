#!/usr/bin/env python
"""
# Details:
#   Database API
#   Used to access database more easily.
# Authors:
#   Andrej Berg
# History:
#   -
# Last modified: 17.04.2018
# ToDo:
#   -
# Bugs:
#   -
"""

__author__ = ["Andrej Berg"]
__date__ = "17.04.2018"

import pandas as pd
import numpy as np
import os

from databaseModel import *


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

def getEntryTable(db_path):
    '''Get a pandas DataFrame with all entries in a data base and
    keywords and tags.'''
    s = openDatabase(db_path)

    # get DB tables as pandas DataFrames
    main = pd.read_sql_table("main", s.bind)[["id", "entry_id", "path"]]
    keywords_raw = pd.read_sql_table("keywords", s.bind)
    keywords = keywords_raw[keywords_raw['value'].notna()]

    tags = keywords_raw[~keywords_raw['value'].notna()]
    tags = tags.drop('value', axis=1).groupby("main_id").agg({"name": listed}).rename(index=int,
                                                                                      columns={"name": "tags"})
    s.close()

    # inner join to get the connection between entries and keywords
    m = pd.merge(main, keywords, left_on='id', right_on="main_id", how="inner")
    # pivot table reduces it to columns
    p = m.pivot(index='id_x', columns='name')["value"]
    # DataFrame where one can search by keyword and tags
    main_out = pd.concat([main.set_index('id'), p, tags], axis=1)
    return main_out

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
#                id = None,
               owner = None,
               url = None,
               sim_type = None,
               description = None,
               created_on = None,
#                added_on = None,
#                updated_on = None,
               n_atoms = None,
               n_steps = None,
               time_step = None,
               raw_keywords = {},
               raw_mdp_parameters = {},
               raw_thermostat = {},
               raw_barostat = {},
               **kwargs
              ):
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