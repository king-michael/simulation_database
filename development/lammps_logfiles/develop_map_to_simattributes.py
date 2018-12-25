import sys
import os
sys.path.insert(0,'../..')
from simdb.utils import lammps_logfile_parser as llp
from pprint import pprint, pformat



# path = 'files'
# file = "log.0.lammps"
# L = llp.LogFileReader(os.path.join(path, file))
# for i,run in enumerate(L.runs):
#     print("run {}".format(i))
#     print pformat(llp.map_lammps_to_database(run))
# storage = {
#         'simulation' if count is None else 'simulation_{}'.format(count) : dict(engine='LAMMPS'),
#         'thermostat' if count is None else 'thermostat_{}'.format(count) : dict(),
#         'barostat' if count is None else 'barostat_{}'.format(count) : dict(),
#     }

def check_combinable_runs(run1, run2):
    """pops items that are additive, then checks the rest"""
    if 'n_steps' in run1 and 'n_steps' in run2:
        run1 = dict((k,v) for k,v in run1.items() if k != 'n_steps')
        run2 = dict((k, v) for k, v in run2.items() if k != 'n_steps')
    elif 'n_steps' in run1 and not 'n_steps' in run2\
        or  'n_steps' in run2 and not 'n_steps' in run1:
        return False
    return run1 == run2

def combine_runs(runs):
    """
    Function to combine a list of runs.

    Parameters
    ----------
    runs

    Returns
    -------

    """
    n_runs = len(runs)
    if n_runs < 2:
        return runs
    s = 1
    previous_run, current_run = runs[0], runs[s]

    rv = []
    for i in range(n_runs):
        if check_combinable_runs(previous_run, current_run):
            previous_run['n_steps']+= current_run['n_steps']
            s+=1
            if s == n_runs:
                rv.append(previous_run)
                break
            previous_run, current_run = previous_run, runs[s]
        else:
            rv.append(previous_run)
            s+=1
            if s == n_runs:
                rv.append(current_run)
                break
            previous_run, current_run = current_run, runs[s]

    return rv


def combine_metagroups(list_meta_groups):
    combined_meta_groups = dict()

    n_runs = len(list_meta_groups)
    if n_runs > 1:
        suffix_pattern = '{{:0{:d}d}}'.format(len(str(n_runs)))
        for i in range(n_runs):
            meta_groups = list_meta_groups[i]
            # add suffix_pattern at the end of the runs
            combined_meta_groups.update(dict((k+suffix_pattern.format(i),v) for k,v in meta_groups.items()))
    else:
        combined_meta_groups.update(list_meta_groups[0])
    return combined_meta_groups

def convert_run_to_metagroups(run):

    meta_groups = dict(
        simulation=dict(engine='LAMMPS'),
        thermostat=dict(),
        barostat=dict(),
    )

    simulation_keywords = ['n_steps', 'time_step', 'units']
    print(run.keys())
    for keyword in simulation_keywords:
        if keyword in run:
            meta_groups['simulation'][keyword] = run[keyword]
    if 'thermostat' in run:
        meta_groups['thermostat'].update(run['thermostat'])

    if 'barostat' in run:
        meta_groups['barostat'].update(run['barostat'])

    for key in list(meta_groups.keys()):
        if len(meta_groups[key]) == 0:
            meta_groups.pop(key)
    return meta_groups

list_runs = []
for i in range(2):
    L = llp.LogFileReader(os.path.join('files',"log.1.lammps"))
    for i,run in enumerate(L.runs):
        list_runs.append(llp.map_lammps_to_database(run))

L = llp.LogFileReader(os.path.join('files',"log.0.lammps"))
for i,run in enumerate(L.runs):
    list_runs.append(llp.map_lammps_to_database(run))

for i in range(3):
    L = llp.LogFileReader(os.path.join('files',"log.1.lammps"))
    for i,run in enumerate(L.runs):
        list_runs.append(llp.map_lammps_to_database(run))

pprint(combine_runs(list_runs))

list_metagroups = [convert_run_to_metagroups(run)
                   for run in llp.LogFileReader(os.path.join('files',"log.0.lammps")).runs]

print("\nlist_metagroups")
pprint(list_metagroups)

print("\ncombine_metagroups(list_metagroups)")
pprint(combine_metagroups(list_metagroups))