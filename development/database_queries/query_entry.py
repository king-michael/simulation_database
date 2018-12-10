"""
Example how to query an entry.
"""

from __future__ import print_function, nested_scopes, generators
from pprint import pprint
from simdb.databaseModel import *
import simdb.databaseAPI as api

db_path = 'test.db'
engine = create_engine('sqlite:///./'+db_path, echo=False) #  if we want spam

# Establishing a session
Session = sessionmaker(bind=engine)
session = Session()

index = 1
query = session.query(Main).filter(Main.id == index)
sim = query.one()

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

pprint(sim2dict(sim))
