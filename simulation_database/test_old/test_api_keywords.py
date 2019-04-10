from __future__ import absolute_import, generators, nested_scopes, division
import pytest
from simdb.databaseModel import *
import simdb.databaseAPI as api



# ======================================================= #
# setup

test_sims = dict(
    TEST01=dict(
        path='p1',
        owner='test',
        keywords=dict(a=1,b=2,c=3),
    ),
    TEST02=dict(
        path='p2',
        owner='test',
        keywords=dict(a=1,b=2,c=3,d=4),
    ),
    TEST03=dict(
        path='p3',
        owner='test',
        keywords=dict(a=2,b=3,c=4,e=4),
    )
)


engine = create_engine('sqlite:///:memory:', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def setup_module():
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

def teardown_module():
    "function called to clean up"
    session.close()

def teardown_function(function):
    session.rollback()

# ======================================================= #
# utility functions

def map_obj_to_string(obj):
    if isinstance(obj, list):
        rv = list(map_obj_to_string(i) for i in obj)
    elif isinstance(obj, tuple):
        rv = tuple(map_obj_to_string(i) for i in obj)
    elif isinstance(obj, dict):
        rv = dict((k,map_obj_to_string(v)) for k,v in obj.items())
    else:
        rv = str(obj)
    return rv


# ======================================================= #
# test: get_keywords
@pytest.mark.parametrize('entry_id, expected_keywords',
              tuple((key, map_obj_to_string(sim['keywords'])) for key, sim in test_sims.items()))
def test_get_keywords(entry_id, expected_keywords):
    """test: get_keywords"""
    keywords = api.get_keywords(session=session, entry_id=entry_id)
    assert keywords == expected_keywords


# ======================================================= #
# test: add_single_keyword
@pytest.mark.parametrize('entry_id, name, value, unique',
     tuple([
         ('TEST01', 'x', 99, True),
     ])
     )
def test_add_single_keywords(entry_id, name, value, unique):
    """test: add_single_keyword"""
    old_keywords = api.get_keywords(session=session, entry_id=entry_id)
    api.add_single_keyword(session=session, entry_id=entry_id,
                           name=name, value=value, unique=unique)
    new_keywords = api.get_keywords(session=session, entry_id=entry_id)
    expected_keywords = dict([(name, value)] + list(old_keywords.items()))
    assert new_keywords == map_obj_to_string(expected_keywords)


# ======================================================= #
# test: update_keywords
@pytest.mark.parametrize('entry_id, added_keywords',
     tuple([
         ('TEST01', dict(a=-10,b=0)),
         ('TEST01', dict(a=4,x=2,z=3)),
         ('TEST01', dict(x=2,z=3)),
     ])
     )
def test_update_keywords(entry_id, added_keywords):
    """test: update_keywords"""
    old_keywords = api.get_keywords(session=session, entry_id=entry_id)
    api.update_keywords(session=session, entry_id=entry_id, **added_keywords)
    new_keywords = api.get_keywords(session=session, entry_id=entry_id)
    expected_keywords = old_keywords
    expected_keywords.update(added_keywords)
    assert new_keywords == map_obj_to_string(expected_keywords)


# ======================================================= #
# test: set_keywords
@pytest.mark.parametrize('entry_id, added_keywords',
     tuple([
         ('TEST01', dict(a=-10,b=0)),
         ('TEST01', dict(a=4,x=2,z=3)),
         ('TEST01', dict(x=2,z=3)),
     ])
     )
def test_set_keywords(entry_id, added_keywords):
    """test: set_keywords"""
    api.set_keywords(session=session, entry_id=entry_id, **added_keywords)
    new_keywords = api.get_keywords(session=session, entry_id=entry_id)
    assert new_keywords == map_obj_to_string(added_keywords)



# ======================================================= #
# test: delete_keywords
@pytest.mark.parametrize('entry_id, delete_keywords',
     tuple([
         ('TEST01', ['a', 'b']),
         ('TEST01', ['a', 'x', 'z']),
         ('TEST01', dict(a=4, x=2, z=3).keys()),
         ('TEST01', ('x', 'z')),
     ])
     )
def test_delete_keywords(entry_id, delete_keywords):
    """test: delete_keywords"""
    old_keywords = api.get_keywords(session=session, entry_id=entry_id)
    api.delete_keywords(session, entry_id, *delete_keywords)
    new_keywords = api.get_keywords(session=session, entry_id=entry_id)
    [old_keywords.pop(k) for k in delete_keywords if k in old_keywords]
    assert new_keywords == old_keywords


# ======================================================= #
# test: delete_all_keywords
@pytest.mark.parametrize('entry_id',
     tuple([
         'TEST01',
     ])
     )
def test_delete_all_keywords(entry_id):
    """test: delete_all_keywords"""
    api.delete_all_keywords(session, entry_id)
    new_keywords = api.get_keywords(session=session, entry_id=entry_id)
    assert new_keywords == {}


if __name__ == '__main__':
    setup_module()
    test_add_single_keywords('TEST01', 'x', 99, True)
    test_delete_keywords('TEST01', ('a', 'b'))
    test_delete_all_keywords('TEST01')
    teardown_module()
