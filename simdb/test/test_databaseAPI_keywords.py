# coding=utf-8
"""
Test DatabaseAPI
- Test keywords
"""

from contextlib import contextmanager

import simdb.databaseAPI as api
from helperfunctions import check_list_unordered_equal
import pytest

# create test cases
test_sims = dict(
    TEST01=dict(
        keywords=dict(a=1, b=2, c=3),
        groups=[1]
    ),
    TEST02=dict(
        keywords=dict(a=1, b=2, c=3, d=4),
        groups=[1, 2]
    ),
    TEST03=dict(
        keywords=dict(a=2, b=3, c=4, e=4),
        groups=[2, 3]
    )
)

# result dictionary
RESULTS = {
    'get_all_keywords': (
        # get_all_keywords(session, groups=None, count=False)
        'kwargs, result',
        (
            # default ARGS
            ({}, ['a', 'b', 'c', 'd', 'e']),
            # count=True
            ({'count': True}, [('a', 3), ('b', 3), ('c', 3), ('d', 1), ('e', 1)]),
            # groups=['1']
            ({'groups': ['1']}, ['a', 'b', 'c', 'd']),
            # test integer
            ({'groups': [1]}, ['a', 'b', 'c', 'd']),
            # test multiple groups
            ({'groups': [2, 3]}, ['a', 'b', 'c', 'd', 'e']),
            # empty keywords
            ({'groups': [999]}, []),
            # groups + counts
            # ({'groups' : [1], 'count' : True}, [('a', 2), ('b', 2), ('c', 2), ('d', 1)]),
        )
    ),
    'get_all_keyword_values': (
        # get_all_keyword_values(session, keyword_name, groups=None, count=False)
        'keyword_name, kwargs, result',
        (
            # default args
            ('a', {}, ['1', '2']),
            # counts
            ('a', {'count': True}, [('1', 2), ('2', 1)]),
            # one value per group
            ('a', {'groups': ['1']}, ['1']),
            # multiple values per group
            ('a', {'groups': ['2']}, ['1', '2']),
            # not in group
            ('e', {'groups': ['1']}, []),
            # no group
            ('a', {'groups': ['X']}, []),
            # combination of two groups
            ('c', {'groups': ['1', '3']}, ['3', '4']),
            # groups + counts
            ('a', {'groups': ['1'], 'count': True}, [('1', 2), ]),
            # groups + counts; not in group
            ('e', {'groups': ['1'], 'count': True}, []),
            # groups + counts; group not there
            ('e', {'groups': ['X'], 'count': True}, []),
        ),
    ),
    'get_keywords': (
        #  get_keywords(session, entry_id)
        'entry_id, result',
        (
            # test normal
            ('TEST01', dict(a='1', b='2', c='3')),
            # test empty
            ('XXXX', api.NoResultFound('No row was found for one()')),
        )
    ),
    'set_keywords': (
        # set_keywords(session, entry_id, **kwargs)
        'entry_id, keywords, result',
        (
            # first test (change nothing)
            ('TEST01', dict(a=1, b=2, c=3), dict(a='1', b='2', c='3')),
            # change one
            ('TEST01', dict(a=2, b=2, c=3), dict(a='2', b='2', c='3')),
            # replace one
            ('TEST01', dict(X=1, b=2, c=3), dict(X='1', b='2', c='3')),
            # replace to one
            ('TEST01', dict(Y=2), dict(Y='2')),
            # clear
            ('TEST01', dict(), dict()),
            # try to set a non existing entry
            ('XXX', dict(a=2), api.NoResultFound('No row was found for one()')),
        )
    ),
    'update_keywords': (
        # update_keywords(session, entry_id, **kwargs)
        'entry_id, keywords, result',
        (
            # update one
            ('TEST01', dict(a=2), dict(a='2', b='2', c='3')),
            # add something new
            ('TEST01', dict(X=4), dict(a='1', b='2', c='3', X='4')),
            # add nothing
            ('TEST01', dict(), dict(a='1', b='2', c='3')),
            # try to set a non existing entry
            ('XXX', dict(a=1), api.NoResultFound('No row was found for one()')),
        )
    ),
    'delete_keywords': (
        'entry_id, keyword_names, result',
        (
            # delete single keyword
            ('TEST01', ['a'], dict(b='2', c='3')),
            # delete multiple keyword
            ('TEST01', ['a', 'b'], dict(c='3')),
            # delete all keyword
            ('TEST01', ['a', 'b', 'c'], dict()),
            # delete none keyword
            ('TEST01', [], dict(a='1', b='2', c='3')),
            # delete nonexisting entry
            ('XXX', ['a'], dict()),
        )
    ),
    'delete_all_keywords': (
        'entry_id, result',
        (
            # delete single keyword
            ('TEST01', dict()),
            # delete single keyword
            ('XXX', api.NoResultFound('No row was found for one()')),
        )
    )
}


@contextmanager
def context_backup_keywords(entry_id):
    """
    Context manger to back up keywords
    Parameters
    ----------
    entry_id : str
        Entry ID
    """
    exists = session.query(api.exists().where(api.Main.entry_id == entry_id)).scalar()
    if exists:
        # save old
        old_keywords = api.get_keywords(session=session, entry_id=entry_id)

    yield exists

    if exists:
        # reset
        api.set_keywords(session=session, entry_id=entry_id, keywords=old_keywords)


session = api.create_new_database(':memory:')


def setup_module():
    """
    Function to setup the test
    """
    for key, details in test_sims.items():
        sim = api.Main(entry_id=key,
                       keywords=[api.Keywords(name=str(k), value=str(v))
                                 for k, v in details.get('keywords', {}).items()],

                       )
        session.add(sim)
        # add groups
        for g in details.get('groups', []):
            group = session.query(api.Groups).filter(api.Groups.name == g).one_or_none()
            if group is None:
                group = api.Groups(name=g)
            group.entries.append(sim)
            session.add(group)

    session.commit()


def teardown_module():
    """
    Function to clean up
    """
    session.close()


@pytest.mark.parametrize(*RESULTS['get_all_keywords'])
def test_get_all_keywords(kwargs, result):
    """
    Test `get_all_keywords`
    Parameters
    ----------
    kwargs : dict
        Dictionary with keyword arguments of `get_all_keywords`.
    result : list
        List of expected results.
    """
    # get result
    res = api.get_all_keywords(session=session, **kwargs)
    # check
    assert check_list_unordered_equal(res, result)


@pytest.mark.xfail(raises=AssertionError)
def test_get_all_keywords_groups_and_counts():
    """FAILS"""
    kwargs, result = ({'groups': [1], 'count': True},
                      [('a', 2), ('b', 2), ('c', 2), ('d', 1)])
    res = api.get_all_keywords(session=session, **kwargs)
    assert check_list_unordered_equal(res, result)


@pytest.mark.parametrize(*RESULTS['get_all_keyword_values'])
def test_get_all_keyword_values(keyword_name, kwargs, result):
    """
    Test `get_all_keyword_values`
    Parameters
    ----------
    keyword_name : str
        Keyword name to test
    kwargs : dict
        Dictionary with keyword arguments of `get_all_keyword_values`.
    result : list
        List of expected results.
    """
    # get result
    res = api.get_all_keyword_values(session=session, keyword_name=keyword_name, **kwargs)
    # check
    assert check_list_unordered_equal(res, result)


@pytest.mark.parametrize(*RESULTS['get_keywords'])
def test_get_keywords(entry_id, result):
    """
    Test `get_keywords`
    Parameters
    ----------
    entry_id : str
        Entry ID
    result : dict or Exception
        List of expected results.
    """
    # get results
    try:
        res = api.get_keywords(session=session, entry_id=entry_id)
    except Exception as e:
        if type(e) == type(result) and e.args == result.args:
            return
        raise e
    # check
    assert type(res) == type(result) and set(res.items()) == set(result.items())


@pytest.mark.parametrize(*RESULTS['set_keywords'])
def test_set_keywords(entry_id, keywords, result):
    """
    Test `set_keywords`
    Parameters
    ----------
    entry_id : str
        Entry ID
    keywords : dict
        Dictionary with keyword arguments of `set_keywords`.
    result : dict or Exception
        List of expected results.
    """

    with context_backup_keywords(entry_id=entry_id):
        try:
            # set keywords
            api.set_keywords(session=session, entry_id=entry_id, keywords=keywords)
        except Exception as e:
            if type(e) == type(result) and e.args == result.args:
                return
            raise e
        # get results
        res = api.get_keywords(session=session, entry_id=entry_id)
        # check
        assert type(res) == type(result) and set(res.items()) == set(result.items())


@pytest.mark.parametrize(*RESULTS['update_keywords'])
def test_update_keywords(entry_id, keywords, result):
    """
    Test `update_keywords`
    Parameters
    ----------
    entry_id : str
        Keyword name to test
    keywords : dict
        Dictionary with keyword arguments of `update_keywords`.
    result : dict or Exception
        List of expected results.
    """

    with context_backup_keywords(entry_id=entry_id):
        try:
            # update
            api.update_keywords(session=session, entry_id=entry_id, keywords=keywords)
        except Exception as e:
            if type(e) == type(result) and e.args == result.args:
                return
            raise e

        # get results
        res = api.get_keywords(session=session, entry_id=entry_id)
        # check
        assert type(res) == type(result) and set(res.items()) == set(result.items())


@pytest.mark.parametrize(*RESULTS['delete_keywords'])
def test_delete_keywords(entry_id, keyword_names, result):
    """
    Test `delete_keywords`
    Parameters
    ----------
    entry_id : str
        Keyword name to test
    keyword_names : list
        Dictionary with keyword arguments of `delete_keywords`.
    result : dict or Exception
        List of expected results.
    """
    with context_backup_keywords(entry_id=entry_id) as exists:
        try:
            # delete
            api.delete_keywords(session=session, entry_id=entry_id, keyword_names=keyword_names)
        except Exception as e:
            print("DASDASDAS")
            if type(e) == type(result) and e.args == result.args:
                return
            raise e

        if exists:
            # get results
            res = api.get_keywords(session=session, entry_id=entry_id)
            # check
            assert type(res) == type(result) and set(res.items()) == set(result.items())


@pytest.mark.parametrize(*RESULTS['delete_all_keywords'])
def test_delete_all_keywords(entry_id, result):
    """
    Test `delete_all_keywords`
    Parameters
    ----------
    entry_id : str
        Keyword name to test
    result : dict or Exception
        List of expected results.
    """

    with context_backup_keywords(entry_id=entry_id) as exists:
        try:

            # delete
            api.delete_all_keywords(session=session, entry_id=entry_id)
        except Exception as e:
            if type(e) == type(result) and e.args == result.args:
                return
            raise e

        if exists:
            # get results
            res = api.get_keywords(session=session, entry_id=entry_id)
            # check
            assert type(res) == type(result) and set(res.items()) == set(result.items())
