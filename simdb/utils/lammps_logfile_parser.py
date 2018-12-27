"""
Scripts to parse and convert LAMMPS log files.
"""

class LogFileReader:
    def __init__(self, filename):
        """

        Attributes
        ----------
        runs :
            List of the run objects

        Todo
        ----
        rigid bodies
            not implemented ridig body integrator
        multiple integrators / thermostat / barostat
            not implemented yet (so we can temp different groups)
        """
        self.filename = filename
        self._run = dict(
            n_steps = 0,             # number of simulation steps
            active_fixes = {},      # dictionary of active fixes
        )

        # list of WARNINGS
        self.WARNINGS = []
        # some defaults
        self.runs = []
        if isinstance(self.filename, str):
            # parse logfile
            self.parse_file(self.filename)
        elif hasattr(self.filename,'__iter__') and hasattr(self.filename, 'read'):
            # parse logfile
            self.parse_file(self.filename, fileobj=self.filename)

    def parse_file(self, filename, fileobj=None):
        """
        Parse a lammps logfile
        """
        if fileobj is None:
            fp = open(filename)
        else:
            fp = fileobj
        for line in fp:
            line_strip = line.strip()
            if len(line_strip) == 0: continue  # empty line
            if line_strip[0] == "#": continue  # comment line
            line_split = line_strip.split()
            if line_strip.find("$") == -1:
                self.interprete_line(line_strip)
        if fileobj is None:
            fp.close()
        self.compile_infos()

    def interprete_line(self, line):
        """
        Function to interprete the line
        """
        line_split = line.split()
        keyword = line_split[0]
        # Handle fixes
        if keyword == 'units':
            self._run['units'] = line_split[1]
        elif keyword == 'timestep':
            self._run['time_step'] = float(line_split[1])
        elif keyword in ['fix', 'unfix']:
            self.handle_fix(line_split)
        elif keyword == 'minimize':
            self.handle_minimize(line_split)
        elif keyword == 'run':
            self.handle_run(line_split)
        elif keyword == 'WARNING:':
            self.WARNINGS.append(line)

    def handle_fix(self, line_split):
        """
        Handle a fix & unfix
        """
        keyword = line_split[0]
        if keyword == 'fix':
            fix_id = line_split[1]  # id
            fix_grp = line_split[2]  # group
            fix_type = line_split[3]  # type
            fix_args = line_split[4:]  # args
            self._run['active_fixes'][fix_id] = [fix_grp, fix_type, fix_args]
        elif keyword == 'unfix':
            del self._run['active_fixes'][line_split[1]]

    def handle_run(self, line_split):
        """
        Add a run
        """

        self.compile_infos()

        run = dict(
            active_fixes={},
        )
        for key in self._run.keys():
            if not key.startswith("_"):
                run[key] = self._run[key]
        run['n_steps'] = int(line_split[1])
        if self._run['n_steps'] is None:
            self._run['n_steps'] = 0
        self._run['n_steps'] += int(line_split[1])
        self.runs.append(run)

    def handle_minimize(self, line_split):
        """
        Add a minimization
        """

        run = dict(
            active_fixes={},
        )
        if 'units' in self._run:
            run['units'] = self._run['units']
        run['integrator'] = 'minimize'
        run['ensemble'] = 'EM'
        run['minimize_prop'] = dict(
            etol=float(line_split[1]),
            ftol=float(line_split[2]),
            maxiter=int(line_split[3]),
            maxeval=int(line_split[4]),
        )
        self.runs.append(run)

    def compile_infos(self):
        """
        Function to compile the infos.
        Finds integrator, thermostat, barostat
        """
        # Todo: add support for multiple thermostat, barostat
        # create dict in advance
        # add thermostat_X
        # add counter X
        # push thermostat at assert statement

        integrator = None
        thermostat = {}
        barostat = {}

        options_thermostat_w_value = [
            'tchain',
            'tloop',
            'drag',
        ]
        options_barostat_w_value = [
            'pchain',
            'ploop',
            'drag',
            'mtk',
        ]
        # go over all fix IDS
        for fixid, (fix_grp, fix_type, fix_args) in self._run['active_fixes'].iteritems():
            # check if have set an integrator
            if fix_type in ['nve', 'nvt', 'npt', 'nph']:
                assert integrator is None, "Multiple Integreators are not implemented"
                integrator = fix_type
            # check for thermostat
            for part in fix_type.split("/"):  # get rid of combinations
                if part in ['nvt', 'npt', 'temp', 'langevin']:
                    assert 'type' not in thermostat , "Multiple Thermostats are not implemented"
                    thermostat['type'] = fix_type
                    if part in ['nvt', 'npt']:
                        i = fix_args.index("temp")
                        thermostat['Tstart'] = fix_args[i + 1]
                        thermostat['Tstop']  = fix_args[i + 2]
                        thermostat['Tdamp'] = fix_args[i + 3]
                        for i, arg in enumerate(fix_args):
                            if arg in options_thermostat_w_value:
                                thermostat[arg] = fix_args[i + 1]

                    else:
                        thermostat['Tstart'] = fix_args[0]
                        thermostat['Tstop']  = fix_args[1]
                        thermostat['Tdamp'] = fix_args[2]

            # check for barostat
            for part in fix_type.split("/"):  # get rid of combinations
                if part in ['nph', 'npt', 'press']:
                    assert 'type' not in barostat, "Multiple Barostats are not implemented"
                    barostat['type'] = fix_type
                    for i, arg in enumerate(fix_args):
                        # default couplings
                        if arg in ['iso', 'aniso', 'tri']:
                            barostat['Pcoupling'] = arg
                            barostat['Pstart'] = fix_args[i + 1]
                            barostat['Pstop'] = fix_args[i + 2]
                            barostat['Pdamp'] = fix_args[i + 3]
                        # if its an individual coupling of dimensions
                        elif arg in ['x', 'y', 'z', 'xy', 'yz', 'xz']:
                            if 'Pcoupling' not in barostat:
                                barostat['Pcoupling'] = []
                                barostat['Pstart'] = []
                                barostat['Pstop'] = []
                                barostat['Pdamp'] = []
                            barostat['Pcoupling'].append(arg)
                            barostat['Pstart'].append(fix_args[i + 1])
                            barostat['Pstop'].append(fix_args[i + 2])
                            barostat['Pdamp'].append(fix_args[i + 3])
                        if arg in options_barostat_w_value:
                            barostat[arg] = fix_args[i + 1]

        # update thermostat and barostat
        self._run['integrator'] = integrator

        if len(thermostat.keys()) != 0:
            self._run['thermostat'] = thermostat

        if len(barostat.keys()) != 0:
            self._run['barostat']   = barostat

        if 'thermostat' in self._run and len(self._run['thermostat']) > 0\
                and 'barostat' in self._run and len(self._run['barostat']) > 0:
            self._run['ensemble'] = 'npt'
        elif 'thermostat' in self._run and len(self._run['thermostat']) > 0:
            self._run['ensemble'] = 'nvt'
        elif 'barostat' in self._run and len(self._run['barostat']) > 0:
            self._run['ensemble'] = 'nph'
        else:
            self._run['ensemble'] = 'nve'


def map_lammps_to_database(keywords):
    # type: (dict) -> dict
    """
    Takes a dictionary of mdp-parameters
    and converts it to the keywords used in the database.

    Parameters
    ----------
    keywords : dict
        dictionary from LogFileReader

    Returns
    -------
    dict
        dictionary of mapped parameters to be feed in the database
    """

    master_dict = dict()
    rv = dict()



    # handling units
    if 'units' in keywords.keys():
        if keywords['units'] == 'metal':
            conv_time = 1
            conv_press = 1
        elif keywords['units'] == 'real':
            conv_time = 0.001
            conv_press = 1.01325
    else:
        keywords['units'] = 'lj'
        conv_time = 0.005
        conv_press = 1

    rv['units'] = keywords['units']

    # handling timestep
    if 'time_step' in keywords.keys():
        # get the conversion factor for time
        dt = float(keywords['time_step'])*conv_time
        rv['time_step'] = dt
    else:
        dt = conv_time

    # mapping general stuff
    if 'n_steps' in keywords.keys():
        rv['n_steps'] = int(keywords['n_steps'])
    if 'ensemble' in keywords.keys():
        rv['ensemble'] = keywords['ensemble']

    master_dict.update(rv)
    # mapping barostats
    rv = dict()
    if 'barostat' in keywords:
        barostat = keywords['barostat']
        if barostat['type'] in ['npt', 'nph']:
            rv['type'] = 'Parrinello-Rahman'
        elif barostat['type'] == 'press/berendsen':
            rv['type'] = 'Berendsen'
        else:
            rv['type'] = barostat['type']
        # remove type from here
        del barostat['type']

        mapping = {
            'Pstart': ['p_init', lambda x: str(float(x) * conv_press)],
            'Pstop': ['p_target', lambda x: str(float(x) * conv_press)],
            'Pdamp': ['p_rel', lambda x: str(float(x) * conv_press)],
            'Pcoupling': ['p_coupling', None],
            'mtk': ['mtk', None],
            'modulus': ['p_compressibility', lambda x: str(1. / (float(x) * conv_press))]
        }

        for name_lammps,(name_db, fun) in mapping.iteritems():
            if name_lammps in barostat.keys():
                value = barostat[name_lammps]
                # if we have to do conversion
                if fun is not None:
                    value = fun(value)
                # add the value to the dict
                rv[name_db] = value
                # remove the entry
                del  barostat[name_lammps]

        # add the rest unconverted
        for key, value in barostat.iteritems():
            rv[key] = value
    master_dict['barostat'] = rv

    # mapping barostats
    rv = dict()
    if 'thermostat' in keywords:
        thermostat = keywords['thermostat']
        if thermostat['type'] in ['nvt', 'npt']:
            rv['type'] = 'Nose-Hoover'
        elif thermostat['type'] == 'temp/berendsen':
            rv['type'] = 'Berendsen'
        elif thermostat['type'] == 'temp/csvr':
            rv['type'] = 'v-rescale'
        else:
            rv['type'] = thermostat['type']
        # remove type from here
        del thermostat['type']

        mapping = {
            'Tstart': ['T_init', None],
            'Tstop' : ['T_target', None],
            'Tdamp':  ['T_rel', None],
        }


        for name_lammps, (name_db, fun) in mapping.iteritems():
            if name_lammps in thermostat.keys():
                value = thermostat[name_lammps]
                # if we have to do conversion
                if fun is not None:
                    value = fun(value)
                # add the value to the dict
                rv[name_db] = value
                # remove the entry
                del thermostat[name_lammps]

        # add the rest unconverted
        for key, value in thermostat.iteritems():
            rv[key] = value
    master_dict['thermostat'] = rv

    return master_dict


def check_combinable_runs(run1, run2):
    """
    Checks if two runs are combinable.

    pops items that are additive, then checks the rest

    Parameters
    ----------
    run1 : LogFileReader.run
    run2 : LogFileReader.run

    Returns
    -------
    bool
        True if combinable, False if not.
    """
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
    runs : List[LogFileReader.run]
        List of runs.

    Returns
    -------
    List[LogFileReader.run]
        List of combined runs if they could be combined.
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
    """
    Function to combine multiple metagroups be renaming them.
    So they can be added into the database with different names.

    A `suffix` is appended going ``1 .. n_metagroups`` with a padding zero if needed.

    Parameters
    ----------
    list_meta_groups : List[dict]

    Returns
    -------
    combined_meta_groups : dict
        Renamed list of metagroups
    """
    combined_meta_groups = dict()

    n_runs = len(list_meta_groups)
    if n_runs > 1:
        suffix_pattern = '{{:0{:d}d}}'.format(len(str(n_runs)))
        for i in range(n_runs):
            meta_groups = list_meta_groups[i]
            # add suffix_pattern at the end of the runs
            combined_meta_groups.update(dict((k+suffix_pattern.format(i+1),v) for k,v in meta_groups.items()))
    else:
        combined_meta_groups.update(list_meta_groups[0])
    return combined_meta_groups


def convert_run_to_metagroups(run):
    """
    Function to convert runs to metagroups like dictionaries.

    Parameters
    ----------
    run : LogFileReader.run
        Run dictionary.

    Returns
    -------
    meta_groups : dict
        Dictionary of metagroups.
    """
    meta_groups = dict(
        simulation=dict(engine='LAMMPS'),
        thermostat=dict(),
        barostat=dict(),
    )

    simulation_keywords = ['n_steps', 'time_step', 'units']
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


def logfile_to_metagroups(logfiles,
                          combine=True,
                          sort=False,
                          sort_key=None,
                          ):
    """
    Function to convert a LAMMPS logfile to metagroups
    Parameters
    ----------
    logfiles : str or List[str]
        List of paths to logfiles or single path.
    combine : bool
        Switch if to combine consecutive runs if they are additive. (Default is ``True``.)
    sort : bool
        Switch if the logfiles should be sorted. (Default is ``True``.)
    sort_key : function
        Function used to sort the logfiles. Default is sort logfiles of the pattern `log.*.lammps`

    Returns
    -------

    """

    if not isinstance(logfiles, str):
        if sort:
            logfiles.sort(key=sort_key)

        # get the different runs from the logfiles
        list_runs = [map_lammps_to_database(run)
                     for logfile in logfiles
                     for run in LogFileReader(logfile).runs]
    else:
        # get the different runs from the logfiles
        list_runs = [map_lammps_to_database(run)
                     for run in LogFileReader(logfiles).runs]

    # combine additive runs
    if combine:
        list_runs = combine_runs(list_runs)


    # transform it to metagroups
    list_metagroups = [convert_run_to_metagroups(run)
                       for run in list_runs]

    # rename if needed
    dict_metagroups = combine_metagroups(list_metagroups)

    return dict_metagroups