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

    sim_dict['meta'] = dict((meta_group.name, dict((m.name, m.value) for m in meta_group.entries))
                            for meta_group in sim.meta.all())


    return sim_dict

pprint(sim2dict(sim))

# meta data

def get_entry_details(session, entry_id):
    """
    Get all information about an entry in database.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        SQL Alchemy session
    entry_id : str
        entry id

    Returns
    -------
    sim_dict : dict
        Simulation object in dictionary form.
    """

    sim = session.query(Main).filter(Main.entry_id == entry_id).one()
    if sim is None:
        return None
    else:
        return sim2dict(sim)
pprint(get_entry_details(session, 'MK0302'))