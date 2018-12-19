"""
Example how to query tags and keywords from the database.
"""
from __future__ import print_function, nested_scopes, generators
from simdb.databaseModel import *
import simdb.databaseAPI as api
import numpy as np

def test_same_keywords(test_keywords,sim_keywords):
    if len(test_keywords) != len(sim_keywords):
        return False
    return all([test_keywords[k.name] == k.value
                if k.name in test_keywords else False
                for k in sim_keywords])

engine = create_engine('sqlite:///:memory:', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


test_sims = dict(
    TEST01=dict(
        keywords=dict(a=1,b=2,c=3)
    ),
    TEST02=dict(
        keywords=dict(a=1,b=2,c=3)
    ),
    TEST03=dict(
        keywords=dict(a=2,b=3,c=4)
    )
)

for key in sorted(test_sims.keys()):
    sim = Main(entry_id=key,
               keywords=[Keywords(name=k, value=v) for k,v in test_sims[key]['keywords'].items()])
    session.add(sim)
query = session.query(Main)
sims = query.all()
assert len(sims) == len(test_sims)

for sim in sims:
    assert test_same_keywords(test_sims[sim.entry_id]['keywords'], sim.keywords)


print()
query = session.query(Keywords.name,Keywords.value).join(Main).filter(Main.entry_id == 'TEST01')
print(dict(query.all()))
#print(sim.keywords)

query = session.query(Keywords.name, Keywords.value).join(Main).filter(Keywords.main_id == 'TEST04')
print(dict(query.all()))

print(api.get_keywords(session, 'TEST01'))

def add_keyword(session, entry_id, name, value=None):
    main_id = None
    query = session.query(Keywords).join(Main).filter(Keywords.name == name).filter(Main.entry_id == entry_id)
    keyword = query.one_or_none()
    if keyword is None:
        if main_id is None:
            main_id = session.query(Main.id).filter(Main.entry_id == entry_id).one()[0]
        keyword = Keywords(name=name, value=value, main_id=main_id)
    else:
        keyword.value = value
    session.add(keyword)

print("\n# add_keyword(session, 'TEST01', 'a', 99999)")
print("# add_keyword(session, 'TEST01', 'q', 234)")
add_keyword(session, 'TEST01', 'a', 99999)
add_keyword(session, 'TEST01', 'q', 234)
print(api.get_keywords(session, 'TEST01'))

query = session.query(Keywords).join(Main).filter(Main.entry_id == 'TEST01').filter(Keywords.name.in_(['a','c','d']))
print(query.all())

def update_keywords(session, entry_id, **kwargs):
    keywords = session.query(Keywords).join(Main)\
                .filter(Main.entry_id == entry_id)\
                .filter(Keywords.name.in_(kwargs.keys())).all()
    for keyword in keywords:
        keyword.value = kwargs.pop(keyword.name)
    if len(keywords) != 0:
        main_id = keywords[0].main_id
    else:
        main_id = session.query(Main.id).filter(Main.entry_id == entry_id).one()[0]
        keywords = []
    for name, value in kwargs.items():
        keywords.append(Keywords(name=name, value=value, main_id=main_id))
    session.add_all(keywords)

print("\n# update_keywords(session, 'TEST01', a=1,b=4,d=8)")
update_keywords(session, 'TEST01', a=1,b=4,d=8)
print(api.get_keywords(session, 'TEST01'))

def delete_keywords(session, entry_id, *args):
    keywords = session.query(Keywords).join(Main)\
                .filter(Main.entry_id == entry_id)\
                .filter(Keywords.name.in_(args)).all()
    for keyword in keywords:
        session.delete(keyword)

print("\n# delete_keywords(session, 'TEST01', 'a', 'b')")
delete_keywords(session, 'TEST01', 'a', 'b')
print(api.get_keywords(session, 'TEST01'))

def set_keywords(session, entry_id, **kwargs):
    main_id = session.query(Main.id).filter(Main.entry_id == entry_id).one()[0]
    session.query(Keywords).filter(Keywords.main_id == main_id).delete()
    for name, value in kwargs.items():
        session.add(Keywords(name=name, value=value, main_id=main_id))


print("\n# delete_keywords(session, 'TEST01', 'a', 'b')")
set_keywords(session, 'TEST01', hallo=1, beta=2)
print(api.get_keywords(session, 'TEST01'))