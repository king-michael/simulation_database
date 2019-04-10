# -*- coding: utf-8 -*-
"""
Module to process tpr files and get the mdp parameters from it

Attributes
----------
GMXBIN : str
    path to the gmx bin directory
GMX : str
    path to the gmx executable
"""


from subprocess import check_output
import tempfile
import os

# define GMXBIN
if 'GMXBIN' not in os.environ:
    os.environ['GMXBIN'] =  '/home/micha/software/GROMACS/gromacs_2016.3_ompi-1.10.2_gcc-5.4/inst/oldcpu/bin/'

def compare_caseinsensitve(text1, text2):
    # type: (str, str) -> bool
    """
    Function to compare two strings if they are case insensitive the same
    Parameters
    ----------
    text1 : str
    text2 : str

    Returns
    -------
    bool
        If the str are case insensitive the same
    """
    # upper().lower() to make sure we can handle special chars like ss
    return text1.upper().lower() == text2.upper().lower()


def get_mdpparameters(tprfile):
    # type: (str) -> dict
    """
    Function to read the binary tpr file and return the mdp-parameters.

    Uses the command:
        `gmx dump -s tprfile -om tmp.mdp`
    Parameters
    ----------
    tprfile : str
        path to the tprfile

    Returns
    -------
    dict
        Dictionary of mdp-parameters in the tpr file
    """

    # get the folder of the gromacs executa
    GMXBIN = os.environ['GMXBIN']
    # path to gmx executable
    GMX = os.path.join(GMXBIN, 'gmx')
    
    # create a temp dir
    tmp_dir = tempfile.mkdtemp()
    mdpfile = os.path.join(tmp_dir, 'tmp.mdp')

    # run gmx dump
    out = check_output([GMX, "dump", "-s", tprfile, "-om", mdpfile])

    # read-in the file
    out_list = open(mdpfile).read().splitlines()

    # cleanup
    os.remove(mdpfile)
    os.rmdir(tmp_dir)

    # create the dictionary
    keywords = dict()
    for line in out_list:
        if line.find('=') != -1:
            line_split = line.split("=", 1)
            key, value = [l.strip() for l in line_split]
            keywords[key] = value
        else:
            line_split = line.split(":", 1)
            key, value = [l.strip() for l in line_split]
            keywords[key] = value

    return keywords


def map_gromacs_to_database(keywords):
    # type: (dict) -> dict
    """
    Takes a dictionary of mdp-parameters
    and converts it to the keywords used in the database.

    Parameters
    ----------
    keywords : dict
        Dictionary of mdp-parameters in gromacs syntax (2018)

    Notes
    -----
        syntax recognition based on gromacs 2018

    Returns
    -------
    dict
        dictionary of mapped parameters to be feed in the database
    """

    master_dict = dict()
    # rv = dict()
    #
    # # mapping general stuff
    # if 'dt' in keywords.keys():
    #     rv['time_step'] = float(keywords['dt'])
    #     rv['n_steps'] = int(keywords['nsteps'])
    #
    # master_dict.update(rv)
    
    
    # mapping barostats
    rv = dict()
    if 'pcoupl' in keywords.keys():
        if compare_caseinsensitve(keywords['pcoupl'], 'Berendsen'):
            rv['type'] = 'Berendsen'
        elif compare_caseinsensitve(keywords['pcoupl'], 'Parrinello-Rahman'):
            rv['type'] = 'Parrinello-Rahman'
        elif compare_caseinsensitve(keywords['pcoupl'], 'MTTK'):
            rv['type'] = 'Parrinello-Rahman'
            rv['MKT'] = True

        if keywords['pcoupl'] != 'no':
            # barostat coupling
            if compare_caseinsensitve(keywords['pcoupltype'], 'isotropic'):
                rv['p_coupling'] = 'iso'
                n_p = 1
            elif compare_caseinsensitve(keywords['pcoupltype'], 'semiisotropic'):
                rv['p_coupling'] = 'xy'
                n_p = 2
            elif compare_caseinsensitve(keywords['pcoupltype'], 'anisotropic'):
                rv['p_coupling'] = 'aniso'
                n_p = 6
            elif compare_caseinsensitve(keywords['pcoupltype'], 'surface-tension'):
                rv['p_coupling'] = 'surface-tension'
                n_p = 33

            # general informations about the barostat
            rv['p_rel'] = keywords['tau-p']
            rv['p_target'] = " ".join(keywords['ref-p'].split()[:n_p])
            rv['p_compressibility'] = " ".join(keywords['compressibility'].split()[:n_p])
    master_dict['barostat'] = rv
    
    # mapping thermostat
    rv = dict()
    if 'tcoupl' in keywords.keys():
        if compare_caseinsensitve(keywords['tcoupl'], 'berendsen'):
            rv['type'] = 'Berendsen'
        elif compare_caseinsensitve(keywords['tcoupl'], 'nose-hoover'):
            rv['type'] = 'Nose-Hoover'
            rv['tchain'] = keywords['nh-chain-length']
        elif compare_caseinsensitve(keywords['tcoupl'], 'andersen'):
            rv['type'] = 'Andersen'
        elif compare_caseinsensitve(keywords['tcoupl'], 'andersen-massive'):
            rv['type'] = 'Andersen-massive'
        elif compare_caseinsensitve(keywords['tcoupl'], 'v-rescale'):
            rv['type'] = 'v-rescale'

        if keywords['tcoupl'] != 'no':
            t_relax = list(set(keywords['tau-t'].split()))
            assert len(t_relax) == 1, 'Not implemented different groups'
            rv['T_rel'] = t_relax[0]
            t_target = list(set(keywords['ref-t'].split()))
            assert len(t_target) == 1, 'Not implemented different groups'
            rv['T_target'] = t_target[0]
    master_dict['thermostat'] = rv

    # mapping simulation setup
    rv = {
        "engine" : "GROMACS",
        "n_steps" : keywords["nsteps"],
        "time_step" : keywords["dt"],
        "integrator" : keywords["integrator"]
    }
    master_dict['simulation'] = rv

    # mapping non-bonded interaction options
    rv = {
        "cutoff_scheme" : keywords["cutoff-scheme"],
        "cut_off_vdw": keywords["rvdw"],
        "vdw_type": keywords["vdw-type"],
        "vdw_modifier": keywords["vdw-modifier"],
        "coulombtype": keywords["coulombtype"],
        "cut_off_coulomb" : keywords["rcoulomb"]
    }
    if compare_caseinsensitve(keywords["coulombtype"], "pme"):
        rv["pme_order"] = keywords["pme-order"]
        rv["fourierspacing"] = keywords["fourierspacing"]
    elif compare_caseinsensitve(keywords["coulombtype"], "reaction-field"):
        rv["epsilon_r"] = keywords["epsilon-r"]
        rv["epsilon_rf"] = keywords["epsilon-rf"]
    master_dict["non-bonded"] = rv
    
    return master_dict

def main(tprfile):
    """
    Function to get the mdp-parameters for the database from a tpr file.

    Parameters
    ----------
    tprfile : str
        path to the tpr file

    Returns
    -------
    dict
        Dictionary of keywords for the database
    """

    keywords = get_mdpparameters(tprfile)
    mapped_keywords = map_gromacs_to_database(keywords)

    return mapped_keywords

#####################################################################
# # CODE to readin binary file without saving mdp file (more complicated)
#
# GMX='/home/micha/software/GROMACS/gromacs_2016.3_ompi-1.10.2_gcc-5.4/inst/oldcpu/bin/gmx'
# out = check_output([GMX, "dump", "-s", "topol.tpr", "-om", mdpfile])
#
# out_list = out.splitlines()
#
# # get a list of the index where a section starts
# dict_sections = dict()
# old_i = 0
# section_name = None
#
# for i, line in enumerate(out_list):
#     # find the sections
#     if not line.startswith('  ') and line.endswith(":"):
#         # handle first entry
#         if section_name is not None:
#             # add entry if we found a new section
#             dict_sections[section_name] = [old_i,i]
#
#         # update variables
#
#         # remove the ":" and only take the first word from the row
#         section_name = line[:-1].split()[0]
#         old_i = i
# # add final entry
# dict_sections[section_name] = [old_i,i]
#
# # get section information
# section = out_list[slice(*dict_sections['inputrec'])]
# section = section[1:] # remove section name
#
# keywords = dict()
# for line in section:
#     line_strip = line.strip()
#     line_split = line_strip.split("=",1)
#     if len(line_split) == 2:
#         key, value = line_split[0].strip(), line_split[1].strip()
#         keywords[key] = value
