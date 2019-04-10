"""
Test DatabaseAPI
- Test keywords
"""

import simdb.databaseAPI as api
from helperfunctions import check_list_unordered_equal

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

# List of all keyword names
list_keywords = [keyword for entry_id, details in test_sims.items()
                 for keyword in details.get('keywords', {}).keys()]
# list of all keywords (unique)
list_uniq_keywords = list(set(list_keywords))
# list of counts machting list_uniq
list_counts_keywords = [list_keywords.count(k) for k in list_uniq_keywords]
# list of tuples (keyword, count)
list_keywords_with_counts = list(zip(list_uniq_keywords, list_counts_keywords))

session = api.create_new_database(':memory:')


def setup_module():
    """
    Function to setup the test
    """
    for key, details in test_sims.items():
        sim = api.Main(entry_id=key,
                       keywords=[api.Keywords(name=k, value=v)
                                 for k,v in details.get('keywords', {}).items()]
                   )
        session.add(sim)
    session.commit()


def teardown_module():
    """
    Function to clean up
    """
    session.close()


def test_get_all_keywords_default():
    keywords = api.get_all_keywords(session=session)
    assert check_list_unordered_equal(keywords, list_uniq_keywords)

def test_get_all_keywords_count():
    res = api.get_all_keywords(session=session, count=True)
    assert check_list_unordered_equal(res, list_keywords_with_counts)

if __name__ == '__main__':
    setup_module()
    test_get_all_keywords_default()
    test_get_all_keywords_count()
    teardown_module()
