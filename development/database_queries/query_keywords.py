"""
Example how to query tags and keywords from the database.
"""
from __future__ import print_function, nested_scopes, generators
from simdb.databaseModel import *
import simdb.databaseAPI as api
import collections
import numpy as np

def print_caption(caption, size=80):
    print("#" + "=" * (size - 2) + "#")
    print("#", caption)
    print("#" + "=" * (size - 2) + "#")

def test_list(x, y):
    """Function to check if two list are the same"""
    return collections.Counter(x) == collections.Counter(y)
def test_dict(x, y):
    """
    Function to check if two dicts are the same
    """
    if set(x.keys()) != set(y.keys()):
        return False
    for k in x.keys():
        vx = x[k]
        vy = y[k]
        # if type(x) != type(y):
        #     return False

        if isinstance(vx, (collections.Sequence, np.ndarray)):
            if isinstance(vy, (collections.Sequence, np.ndarray)):
                if test_list(list(vx),list(vy)):
                    continue
                else:
                    return False
            else:
                return False
        if x != y:
            return False
    return True

db_path = 'test.db'
engine = create_engine('sqlite:///./'+db_path, echo=False) #  if we want spam

# Establishing a session
Session = sessionmaker(bind=engine)
session = Session()


query = session.query(Keywords).filter(not_(Keywords.value.is_(None)))
print(query.all())

query = session.query(Keywords.name).filter(Keywords.value.is_(None))
print(query.all())
############################################################################################
# Usefull stuff
############################################################################################

#=============================================================================#
# keywords
#=========================================================#
# all keywords
print_caption("all keywords")

query = session.query(Keywords.name, Keywords.value)\
    .select_from(Keywords)\
    .filter(not_(Keywords.value.is_(None)))
result = query.all()
print(result)
print("len: ", len(result))

#=========================================================#
# unique tags

print_caption("unqiue keywords")
query = session.query(Keywords.name, Keywords.value)\
    .distinct()\
    .filter(not_(Keywords.value.is_(None)))\

result = query.all()
unique_keywords = collections.defaultdict(list)
for k,v in result:
    unique_keywords[k].append(v)
print(unique_keywords)
print("len: ", len(unique_keywords))

import itertools
unique_keywords_v2 = dict((k, list(zip(*v))[1]) for k,v in itertools.groupby(result, lambda x: x[0]))
print(unique_keywords_v2)
print("len: ", len(unique_keywords_v2))
assert test_dict(unique_keywords, unique_keywords_v2)

#=========================================================#
# OLD VERSION
print_caption("OLD api keywords")
q = session.query(Keywords)
keywords = [e.name for e in q.filter(Keywords.value != None).all()]
key_dict = {}
for k in np.unique(keywords):
    key_dict[k] = np.unique([e.value for e in q.filter(Keywords.value != None, Keywords.name == k).all()])
print(key_dict)
print("len: ", len(key_dict))

#=========================================================#
# unique tags per api
print_caption("api keywords")

api_keywords = api.get_keywords(db_path=db_path)
print(api_keywords)
print("len: ", len(api_keywords))

assert test_dict(api_keywords, key_dict)
assert test_dict(api_keywords, unique_keywords)
#=============================================================================#
# tags
#=========================================================#
# all tags
print_caption("all tags")

query = session.query(Keywords.name).select_from(Keywords).filter(Keywords.value.is_(None))
all_tags = query.all()
print(all_tags)
print("len: ", len(all_tags))

#=========================================================#
# unique tags
print_caption("unqiue tags")

query = session.query(distinct(Keywords.name)).select_from(Keywords).filter(Keywords.value.is_(None))
result = query.all()
unique_tags = list(zip(*result))[0]

print(unique_tags)
print("len: ", len(unique_tags))
assert len(unique_tags) == len(list(set(unique_tags))), "tags are not unqiue"

#=========================================================#
# unique tags per api
print_caption("api tags")

api_tags = api.get_tags(db_path=db_path)
print(api_tags)
print("len: ", len(api_tags))
assert test_list(api_tags, unique_tags)

session.close()