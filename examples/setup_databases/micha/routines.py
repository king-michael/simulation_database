
import logging
import os

from pprint import pformat
from collections import Counter, OrderedDict
from datetime import datetime
from typing import List, Tuple

from simdb.databaseModel import *

logger = logging.getLogger('routine:create_database')


def get_data_from_info_file(fname, list_comments=('#')):
    """
    Function to get data from a `_info_` file.

    Splits after the first occurence of `:`.

    Parameters
    ----------
    fname : str
        File name.
    list_comments : List[str] or Tuple[str]
        List of comment characters.

    Returns
    -------
    data : dict
        dict of file context
    """

    # Create a dict to store data in
    data={}

    with open(fname, 'r') as fp:
        for line in fp:
            line_strip = line.strip()
            if len(line_strip) == 0: continue  # empty lines
            if line_strip[0] in list_comments: continue  # comments
            line_split = line_strip.split(":", 1)  # max split 1
            if len(line_split) == 2:
                data[line_split[0].strip()] = line_split[1].strip()
    return data


def find_simulations(pattern='_info_',
                     root_path='.',
                     dir_ignore=('OLD', 'old', 'Old', 'TMP', 'tmp', 'rm', 'template', 'testcase', 'input_files', 'gits'),
                     ignore_warnings = False,
                     check_for_duplicates=True,
                     ):
    """
    Function to find all simulations for a given `pattern` based on a given `root_path`.

    Parameters
    ----------
    pattern : str
        Pattern for the file name.
    root_path : str
        Root path from where to start the search.
    dir_ignore : Union[List[str], Tuple[str]]
        List of starting strings for directories which should be ignored.
    ignore_warnings : bool
        Switch if warnings should be ignored or a `UserWarning` will be raised.
    check_for_duplicates : bool
        Switch to check for duplicates. Raises a `UserWarning` if duplicates are found.

    Returns
    -------
    list_data : List[dict]

    """

    from simdb.utils.fileFinder import find_files

    list_simids, list_paths, list_data = [], [], []

    logger.info('FIND FILES')
    ERRORS=False
    WARNINGS=False
    files = find_files(pattern=pattern, path=root_path, dir_ignore=dir_ignore)
    logger.info('found {} files'.format(files))
    for fname in files:
        data = get_data_from_info_file(fname)
        data['path']=os.path.dirname(fname)

        try:
            list_simids.append(data['ID']) # throws an ERROR if ID not in data
        except:
            logger.error("ERROR: ID: {}".format(fname))
            ERRORS = True

        if 'MEDIAWIKI' not in data:
            logger.warning("WARNING: NO MEDIAWIKI ENTRY: {}".format(fname))
            WARNINGS = True

            list_data.append(data)
            list_paths.append(fname)

    assert len(list_simids) == len(list_data), "SIM_IDS and DATAS does not have the same lenght." \
                                               "some _info_ file doesn't contain an ID"

    assert not ERRORS, "Error! SIM_IDS are off"
    if not ignore_warnings and WARNINGS:
        raise UserWarning("Warning: something is off")

    if check_for_duplicates:
        logger.info('check for duplicates')
        list_count = Counter(list_simids)
        list_duplicates = [(i for i, entry in enumerate(list_simids) if entry == k)
                           for k, v in list_count.iteritems() if v != 1]
        if list_duplicates > 0:
            for duplicates in list_duplicates:
                logger.error('duplicate found for: simd={}\npaths=\n{}'.format(
                    list_simids[duplicates[0]],
                    '\n'.join(map(list_paths.__getitem__, duplicates))
                ))
            raise UserWarning("Error! Duplicates found.")

    return list_data


def list_guess_folder_type(list_data,
                           dir_ignore = ('analysis'),
                           cases = ('LAMMPS', 'GROMACS'),
                           overwrite=False,
                           ):
    """
    Function to guess the folder type.

    Parameters
    ----------
    list_data : List[dict]
        List of data dictionaries for ever simulation.
    dir_ignore : List[str] or Tuple[str]
        List of folders which should be ignored.
    cases : List[str] or Tuple[str]
        List of cases to consider for guess.
    overwrite : bool
        Switch if `True` the dictionary entry `type` will be overwritten.

    Returns
    -------
    list_data : List[dict]
        Updated dictionaries in `list_data` with `type`.
    """
    from simdb.utils.detect_folder_type import guess_folder_type
    for data in list_data:
        if 'type' not in data or overwrite:
            data['type'] = guess_folder_type(data['path'], cases=cases, dir_ignore=dir_ignore)

    return list_data

def map_data_to_map(data):
    """
    Function to map kwargs to Object.

    Uses `self.mapping` to map kwargs to `self.ATTRIBUTE`.

    Parameters
    ----------
    data : dict
        Dictionary of keyword arguments.

    Returns
    -------
    mapped_data : dict
        Mapped data.
    """
    mapping = {
        'ID': 'entry_id',
        'MEDIAWIKI': 'url',
        'INFO': 'description'
    }
    mapped_data = dict((mapping[k], v) if k in mapping else (k,v)
                       for k,v in data.items())
    return mapped_data

def setup_database(list_data, db, owner=None, recreate=True):

    if owner is None:
        from getpass import getuser
        _owner = getuser()

    logger.info('Create the Database')
    logger.info('store in database : {}'.format(db))

    if recreate and os.path.exists(db):
        os.remove(db)
        logger.info('removed old file: %s', db)

    engine = create_engine('sqlite:///{}'.format(db), echo=False)  # if we want spam

    # Establishing a session
    Session = sessionmaker(bind=engine)
    session = Session()
    setup_database(engine)

    for data in list_data:
        data = map_data_to_map(data)
        data['owner'] = owner if owner is not None else data['owner'] if 'owner' in data else _owner
        sim = Main(
            entry_id=data['entry_id'],
            url=data['url'],
            type=data['type'],
            owner=data['owner'],
            path=data['path'],
            created_on=data['created_on'] if 'created_on' in data.keys() else None,
            description=data['description'] if 'description' in data.keys() else "",
        )
        session.add(sim)
    session.commit()
    session.close()
    logger.info('Created the database: %s', db)




if __name__ == '__main__':
    owner = 'micha'
    db = 'micha.db'
    pattern = '_info_'
    root_path = '/home/micha/SIM-PhD-King/'
    dir_ignore = ('OLD', 'old', 'Old', 'TMP', 'tmp', 'rm', 'template', 'testcase', 'input_files', 'gits')

    # get files
    list_data = find_simulations(pattern=pattern,
                                 root_path=root_path,
                                 dir_ignore=dir_ignore)
    # guess folder type
    list_data = list_guess_folder_type(list_data=list_data,
                                       dir_ignore = ('analysis'),
                                       cases = ('LAMMPS', 'GROMACS'),
                                       overwrite=False)

    # create the database
    setup_database(list_data=list_data,
                   db=db,
                   owner=owner,
                   recreate=True)

    #