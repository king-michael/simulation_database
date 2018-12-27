"""
Script to find parent - child relationships based on sim_id
"""

db_raw = 'tmp_database_add_missing.db'
db     = 'tmp_database_add_parents.db'

warn_depth=10
import logging
logger = logging.getLogger('SetupDatabase:create_database:find_parents')

import sys
import os
sys.path.append("../../..")
sys.path.append("../../../..")

from simdb.databaseModel import *
import simdb.databaseAPI as api
from shutil import copy2

logger.info('find parents')
logger.info('use database : {}'.format(db_raw))
logger.info('store in database : {}'.format(db))

if 'OWNER' in os.environ:
  OWNER = os.environ['OWNER']
else:
  OWNER = ""
logger.info('set OWNER = %s', OWNER)

logger.info('copy %s --> %s', db_raw, db)
copy2(db_raw,db)

# connect to database
session = api.connect_database(db_path=db)

rv = session.query(Main.entry_id).all()

SIM_IDS = [sim_id[0] for sim_id in rv]
SIM_ID_MAIN = sorted(list(set([sim_id[0][:6] for sim_id in rv])))
tmp=[len(sim_id) for sim_id in SIM_IDS]
max_depth=max(tmp)
if max_depth > warn_depth:
    logger.warn('depth to long (depth: %d ; exampleID: %s)',
                max_depth, SIM_IDS[tmp.index(max_depth)])

for sim_id in SIM_IDS:
    if   len(sim_id) == 6: # parents
        pass
    elif len(sim_id) == 8: # child
        parent = sim_id[:6]
        sim_child = session.query(Main).filter(Main.entry_id == sim_id).one()
        sim_parent = session.query(Main).filter(Main.entry_id == parent).one()
        ret = session.query(  # check if parent has grandparent
            exists().where(
                and_(
                    AssociationMainMain.parent == sim_parent,
                    AssociationMainMain.child == sim_child
                )
            )).scalar()
        if not ret: # if the releationship is not there yet
            sim_parent.children.append(AssociationMainMain(parent=sim_parent,
                                                           child=sim_child,
                                                           extra_data='SUB'))
            logger.debug('ADDED: parent: %s child: %s',
                        sim_parent.entry_id,
                        sim_child.entry_id)
    elif len(sim_id) == 10: # grandchild
        parent = sim_id[:8]
        grandparent = sim_id[:6]
        sim_child = session.query(Main).filter(Main.entry_id == sim_id).one()
        sim_parent = session.query(Main).filter(Main.entry_id == parent).first()
        if sim_parent is None: # handle if the entry dont exist
            sim_parent = Main(
                entry_id = parent,
                url = grandparent,
                owner = OWNER,
                path = '',
                description = "--------",
            )
            session.add(sim_parent)
        ret = session.query(  # check if parent has grandparent
            exists().where(
                and_(
                    AssociationMainMain.parent == sim_parent,
                    AssociationMainMain.child == sim_child
                )
            )).scalar()
        if not ret:  # if the releationship is not there yet
            sim_parent.children.append(AssociationMainMain(parent=sim_parent,
                                                           child=sim_child,
                                                           extra_data='SUBSUB'))
            logger.debug('ADDED: parent: %s child: %s',
                        sim_parent.entry_id,
                        sim_child.entry_id)
        sim_grandparent = session.query(Main).filter(Main.entry_id == grandparent).one()
        ret = session.query( # check if parent has grandparent
            exists().where(
                and_(
                    AssociationMainMain.parent == sim_grandparent,
                    AssociationMainMain.child == sim_parent
                )
            )).scalar()
        if not ret: # if grandchild relation is not here
            sim_grandparent.children.append(AssociationMainMain(parent=sim_grandparent,
                                                                child=sim_parent,
                                                                extra_data='SUB'))
            logger.debug('ADDED: parent: %s child: %s',
                        sim_grandparent.entry_id,
                        sim_parent.entry_id)
session.commit()
session.close()
logger.info('Created the database: %s', db)
