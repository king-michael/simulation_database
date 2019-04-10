"""
Description:
 - class to find all finds in sub dirs matching a pattern

authors:
  Michael King <michael.king@uni-konstanz.de>

last modified: 09.02.2018
"""
import os,sys
from glob import glob
import logging
logger = logging.getLogger('Simulation_database')

def find_files(pattern, path='.', dir_ignore=[]):
    # type: (str,str,List[str]) -> List[str]

    """
    finds all files matching the pattern from root

    Parameters
    ----------
    pattern : str
        if not defined take the pattern from Settings ['_info_']
    path : str, optional
        root folder where to start the search (default is '.')
    dir_ignore : List[str], optional
        directories to be ignored, or directories start with this patterns

    Returns
    -------
    output : List[str]
        List of path to the found files.
    """

    logger.info('FileFinder: pattern: %s', pattern)
    logger.info('FileFinder: path: %s', os.path.realpath(path))
    logger.info('FileFinder: dir_ignore: %s', dir_ignore)
    
    # make it unique
    exclude = set(dir_ignore)
    # Get files
    output = []
    # walk through all folders
    for root, dirs, files in os.walk(path, topdown=True):
        # remove the files which match with the exclude flags
        [dirs.remove(d) for d in list(dirs) for ex in exclude if d.startswith(ex)]
        # add the founded items to the list
        output.extend(glob(os.path.join(root,pattern)))
    return output
