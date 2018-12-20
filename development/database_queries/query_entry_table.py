from __future__ import print_function, nested_scopes, generators
from simdb.databaseModel import *
from sqlalchemy.orm import noload

from pprint import pprint
import simdb.databaseAPI as api
import numpy as np
from collections import Iterable
import pandas as pd

test_sims = dict(
    TEST01=dict(
        path='p1',
        owner='test',
        keywords=dict(a=1,b=2,c=3),
        groups=[(1,'A'),(2,'B')],
    ),
    TEST02=dict(
        path='p2',
        owner='test',
        keywords=dict(a=1,b=2,c=3,d=4),
        groups=[(2,'B')],
    ),
    TEST03=dict(
        path='p3',
        owner='test',
        keywords=dict(a=2,b=3,c=4,e=4),
        groups=[(1,'A')],
    )
)

def test_same_keywords(test_keywords,sim_keywords):
    if len(test_keywords) != len(sim_keywords):
        return False
    return all([test_keywords[k.name] == k.value
                if k.name in test_keywords else False
                for k in sim_keywords])


def setup_testcase(session, test_sims):
    for key in sorted(test_sims.keys()):
        test_sim = test_sims[key]
        sim = Main(entry_id=key,
                   path=test_sim['path'],
                   owner=test_sim['owner'],
                   keywords=[Keywords(name=k, value=v) for k,v in test_sim['keywords'].items()]
                   )
        #[sim.groups.append(Groups(name=name)) for i, name in test_sim['groups']]

        session.add(sim)
    session.commit()





engine = create_engine('sqlite:///:memory:', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

setup_testcase(session, test_sims)

sims = session.query(Main).all()
for sim in sims:
    print(sim)
    print(sim.keywords)


def get_entry_table(session, group_names=None, keyword_names=None, columns=None):
    """Get pandas table of all entries meeting the selection creteria.
    This is maybe a better way to get entries since selection is on SQL level.

    Args:
        db_path: string, path to database
        group_names: list, names of groups, logic for groups is OR
        tags: list, logic for tags is AND
        columns: list, columns which should be displayed
    """
    if columns is None:
        columns = ['entry_id', 'path', 'owner', 'url', 'type', 'description']
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

df = get_entry_table(session)
print(df)

df = get_entry_table(session, keyword_names=['a','b'])
print(df)

df = get_entry_table(session, keyword_names=['a','e'])
print(df)
