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
            nsteps = 0,             # number of simulation steps
            active_fixes = {},      # dictionary of active fixes
        )

        # list of WARNINGS
        self.WARNINGS = []
        # some defaults
        self.runs = []
        # parse logfile
        self.parse_file(self.filename)

    def parse_file(self, filename):
        """
        Parse a lammps logfile
        """
        with open(filename) as fp:
            for line in fp:
                line_strip = line.strip()
                if len(line_strip) == 0: continue  # empty line
                if line_strip[0] == "#": continue  # comment line
                line_split = line_strip.split()
                if line_strip.find("$") == -1:
                    self.interprete_line(line_strip)
        self.compile_infos()

    def interprete_line(self, line):
        """
        Function to interprete the line
        """
        line_split = line.split()
        keyword = line_split[0]
        # Handle fixes
        if keyword in ['fix', 'unfix']:
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
        run['nsteps'] = int(line_split[1])
        if self._run['nsteps'] is None:
            self._run['nsteps'] = 0
        self._run['nsteps'] += int(line_split[1])
        self.runs.append(run)

    def handle_minimize(self, line_split):
        """
        Add a minimization
        """

        run = run = dict(
            active_fixes={},
        )
        run['integrator'] = 'minimize'
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
        self._run['integrator'] = None
        self._run['thermostat'] = None
        self._run['barostat'] = None

        # go over all fix IDS
        for fixid, (fix_grp, fix_type, fix_args) in self._run['active_fixes'].iteritems():
            # check if have set an integrator
            if fix_type in ['nve', 'nvt', 'npt', 'nph']:
                assert self._run['integrator'] is None, "Multiple Integreators are not implemented"
                self._run['integrator'] = fix_type
                self._run['_integrator_id'] = fixid
            # check for thermostat
            for part in fix_type.split("/"):  # get rid of combinations
                if part in ['nvt', 'npt', 'temp', 'langevin']:
                    assert self._run['thermostat'] is None, "Multiple Thermostats are not implemented"
                    self._run['thermostat'] = fix_type
                    self._run['_thermostat_id'] = fixid
                    if part in ['nvt', 'npt']:
                        i = fix_args.index("temp")
                        self._run['temp_start'] = fix_args[i + 1]
                        self._run['temp_stop'] = fix_args[i + 2]
                        self._run['temp_relax'] = fix_args[i + 3]
                        # tchain, tloop and drag,

                    else:
                        self._run['temp_start'] = fix_args[0]
                        self._run['temp_stop'] = fix_args[1]
                        self._run['temp_relax'] = fix_args[2]
            # check for barostat
            for part in fix_type.split("/"):  # get rid of combinations
                if part in ['nph', 'npt', 'press']:
                    assert self._run['barostat'] is None, "Multiple Barostats are not implemented"
                    self._run['barostat'] = fix_type
                    self._run['_barostat_id'] = fixid
                    self._run['press_mode'] = None
                    for i, arg in enumerate(fix_args):
                        # default couplings
                        if arg in ['iso', 'aniso', 'tri']:
                            self._run['press_mode'] = arg
                            self._run['press_start'] = fix_args[i + 1]
                            self._run['press_stop'] = fix_args[i + 2]
                            self._run['press_relax'] = fix_args[i + 3]
                        # if its an individual coupling of dimensions
                        elif arg in ['x', 'y', 'z', 'xy', 'yz', 'xz']:
                            if self._run['press_mode'] is None:
                                self._run['press_mode'] = []
                                self._run['press_start'] = []
                                self._run['press_stop'] = []
                                self._run['press_relax'] = []
                            self._run['press_mode'].append(arg)
                            self._run['press_start'].append(fix_args[i + 1])
                            self._run['press_stop'].append(fix_args[i + 2])
                            self._run['press_relax'].append(fix_args[i + 3])
                        elif arg == 'mtk' and fix_args[i+1] == 'yes':
                            self._run['mtk_correction'] = True
                        # pchain, mtk, ploop, nreset, drag, and dilate

#             iso or aniso or tri values = Pstart Pstop Pdamp
#     Pstart,Pstop = scalar external pressure at start/end of run (pressure units)
#     Pdamp = pressure damping parameter (time units)
#   x or y or z or xy or yz or xz
#     def __del__(self):
#         for run in self.runs:
#             del run

if __name__ == '__main__':

    import os
    path = 'files'
    files = os.listdir(path)
    for file in files:
        print '\n', file

        L = LogFileReader(os.path.join(path,file))
        for run in L.runs:
            print run
