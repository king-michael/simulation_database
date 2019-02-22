# coding=utf-8
"""
Module to detect the folder type.
"""

import os
import re
import configparser


def get_files(path, exclude=(), ignore_symlinks=True):
    """
    Function to get files

    Parameters
    ----------
    path : str
        Path walk through.
    exclude : List[str] or Tuple[str]
        List of files/folders to exclude. Default is ``[]``.
    ignore_symlinks : bool
        Switch to ignore simlinks. Default is ``True``.

    Returns
    -------
    files : List[str]
        List of files in the folder and subfolders.
    """

    # make it unique
    exclude = set(exclude)
    # Get files
    output = []
    # walk through all folders
    for root, dirs, files in os.walk(path, topdown=True):
        # remove the files which match with the exclude flags
        [dirs.remove(d) for d in list(dirs) for ex in exclude if re.match(ex, d)]

        if ignore_symlinks:
            # remove symlinks
            [files.remove(f) for f in list(files)
             if os.path.islink(os.path.join(root, f))]

        # add the founded items to the list
        output.extend(files)
    return output


def _get_dict_cases(config_file, cases=('LAMMPS', 'GROMACS')):
    """
    Function to return a dictionary with regex patterns for the given cases and a rating of those.
    Reads in the config_file.

    Parameters
    ----------
    config_file : str or List[str]
        File path to the config file or a List of config files.
    cases : List[str] or Tuple[str]
        List of cases. Default is ``('LAMMPS', 'GROMACS')``.

    Returns
    -------
    dict_cases : dict[dict[unicode]]
        Dictionary of regex patterns for the different cases and a rating of those.
    """

    dict_cases = dict((case, dict()) for case in cases)

    if isinstance(config_file, (tuple, list)):
        for cfile in config_file:
            dict_cases.update(_get_dict_cases(cfile, cases=cases))
        return dict_cases

    # readin the config file
    config = configparser.ConfigParser(inline_comment_prefixes=';')
    config.SECTCRE = re.compile(r"\[ *(?P<header>[^]]+?) *\]")
    config.read(config_file)

    for section in config.sections():
        for case in cases:
            if section.startswith(case):
                for key, value in config[section].items():
                    if key not in dict_cases[case]:
                        dict_cases[case][key] = int(value)
                    elif dict_cases[case][key] < value:
                        dict_cases[case][key] = int(value)

    return dict_cases


def _get_rating_for_regex_dict(fname, regex_dictionary):
    """
    iterate check if fname match to any item of regexlist,
    returns raiting for the best hit

    Parameters
    ----------
    fname : str
        File name.
    regex_dictionary : dict
        Dictionary of (regex, rating).

    Returns
    -------
    best_rating : int or None
        Returns the found raiting. None if no matching regex pattern was found.
    """
    best_rating = 0
    for reg, rating in regex_dictionary.items():
        if re.match(str(reg), fname) and rating > best_rating:
            best_rating = rating
    return best_rating


def _compare_with_dict_cases(fname, dict_cases, ignore_warning=False):
    """
    Iterate over dict_cases, and checks for every case if the filename matches.
    Then returns the raiting for the case.

    Parameters
    ----------
    fname : str
        File name.
    dict_cases  : dict[dict[unicode]]
        Dictionary of regex patterns for the different cases and a rating of those.
    ignore_warning : bool
        Switch if UserWarning should be ignored. Default is ``False``.

    Returns
    -------
    best_rating : int or None
        Best found raiting.
    best_case : str .
        Best found case in dict_cases.
    """

    best_rating, cases = 0, []
    for key, regex_dict in dict_cases.items():
        rating = _get_rating_for_regex_dict(fname, regex_dict)
        if rating == 0:
            continue
        elif rating > best_rating:
            best_rating = rating
            cases = [key]
        elif rating == best_rating:
            cases.append(key)
    if not ignore_warning and len(cases) > 1:
        raise UserWarning("Could not decide decide about the folder structure."
                          "\ncases: {}".format(cases))
    best_case = cases.pop(0) if len(cases) > 0 else ""
    return best_case, best_rating


def guess_folder_type_from_files(files, dict_cases, ignore_warning=True):
    """
    Function to guess the folder type from a list of file names.
    Parameters
    ----------
    files : List[str]
        List of file names.
    dict_cases  : dict[dict[unicode]]
        Dictionary of regex patterns for the different cases and a rating of those.
    ignore_warning : bool
        Switch if UserWarning should be ignored. Default is ``False``.

    Returns
    -------
    folder_type : str
        Guessed folder type.
    """

    file_ratings = sorted([_compare_with_dict_cases(fname, dict_cases=dict_cases, ignore_warning=ignore_warning)
                           for fname in files],
                          key=lambda x: x[1],
                          reverse=True)
    folder_type = file_ratings[0][0]
    if file_ratings[0][1] <= 0:
        folder_type = None
    return folder_type


def guess_folder_type(path, cases=('LAMMPS', 'GROMACS'), dir_ignore=(), config_file=None, ignore_warning=True):
    """
    Guess the folder_type
    Parameters
    ----------
    path : str
        Path to guess the folder structure from.
    cases : List[str]
        List of cases to use. Default is ``['LAMMPS', 'GROMACS']``.
    dir_ignore : List[str]
        Folders to ignore. Default is ``[]``.
    config_file : str or None
        Config files to use. If ``None`` the 'regex_weights.ini' in the module will be used.
        Default is ``None``.
    ignore_warning : bool
        Switch if UserWarning should be ignored. Default is ``False``.

    Returns
    -------
    folder_type : str
        Guessed folder type.
    """
    if config_file is None:
        config_file = os.path.join(os.path.dirname(__file__), 'regex_weights.ini')
    dict_cases = _get_dict_cases(config_file=config_file, cases=cases)
    files = get_files(path, exclude=dir_ignore)
    folder_type = guess_folder_type_from_files(files, dict_cases=dict_cases, ignore_warning=ignore_warning)

    return folder_type
