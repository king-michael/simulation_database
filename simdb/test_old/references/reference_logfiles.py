reference_logfiles = {
 'in.lj': [{'active_fixes': {'1': ['all', 'nve', []]},
            'integrator': 'nve',
            'nsteps': 100,
            'units': 'lj'}],
 'in.lj.em': [{'active_fixes': {},
               'integrator': 'minimize',
               'minimize_prop': {'etol': 0.0001,
                                 'ftol': 1e-06,
                                 'maxeval': 1000,
                                 'maxiter': 100}}],
 'in.lj.nve': [{'active_fixes': {'1': ['all', 'nve', []]},
                'integrator': 'nve',
                'nsteps': 100,
                'units': 'lj'}],
 'in.lj.nvt': [{'active_fixes': {'1': ['all',
                                       'nvt',
                                       ['temp', '1', '1', '1']]},
                'integrator': 'nvt',
                'nsteps': 100,
                'thermostat': {'Tdamp': '1',
                               'Tstart': '1',
                               'Tstop': '1',
                               'type': 'nvt'},
                'units': 'lj'}],
 'in.lj.nvt.sub_vars': [],
 'in.lj.nvt_npt': [{'active_fixes': {'1': ['all',
                                           'npt',
                                           ['temp',
                                            '1',
                                            '1',
                                            '1',
                                            'iso',
                                            '1',
                                            '1',
                                            '10']]},
                    'integrator': 'nvt',
                    'nsteps': 100,
                    'thermostat': {'Tdamp': '1',
                                   'Tstart': '1',
                                   'Tstop': '1',
                                   'type': 'nvt'},
                    'units': 'lj'},
                   {'active_fixes': {'1': ['all',
                                           'npt',
                                           ['temp',
                                            '1',
                                            '1',
                                            '1',
                                            'iso',
                                            '1',
                                            '1',
                                            '10']]},
                    'barostat': {'Pcoupling': 'iso',
                                 'Pdamp': '10',
                                 'Pstart': '1',
                                 'Pstop': '1',
                                 'type': 'npt'},
                    'integrator': 'npt',
                    'nsteps': 100,
                    'thermostat': {'Tdamp': '1',
                                   'Tstart': '1',
                                   'Tstop': '1',
                                   'type': 'npt'},
                    'units': 'lj'}],
 'in.lj.nvt_nvt': [{'active_fixes': {'1': ['all',
                                           'nvt',
                                           ['temp', '1', '1', '1']]},
                    'integrator': 'nvt',
                    'nsteps': 100,
                    'thermostat': {'Tdamp': '1',
                                   'Tstart': '1',
                                   'Tstop': '1',
                                   'type': 'nvt'},
                    'units': 'lj'},
                   {'active_fixes': {'1': ['all',
                                           'nvt',
                                           ['temp', '1', '1', '1']]},
                    'integrator': 'nvt',
                    'nsteps': 1000,
                    'thermostat': {'Tdamp': '1',
                                   'Tstart': '1',
                                   'Tstop': '1',
                                   'type': 'nvt'},
                    'units': 'lj'}],
 'log.0.lammps': [{'active_fixes': {},
                   'integrator': 'minimize',
                   'minimize_prop': {'etol': 1e-06,
                                     'ftol': 1e-06,
                                     'maxeval': 100,
                                     'maxiter': 100}},
                  {'active_fixes': {'com': ['free',
                                            'momentum',
                                            ['1000',
                                             'linear',
                                             '1',
                                             '1',
                                             '1']]},
                   'integrator': 'nve',
                   'nsteps': 10000,
                   'thermostat': {'Tdamp': '0.1',
                                  'Tstart': '300',
                                  'Tstop': '300',
                                  'type': 'temp/csvr'},
                   'timestep': 0.001,
                   'units': 'metal'},
                  {'active_fixes': {'com': ['free',
                                            'momentum',
                                            ['1000',
                                             'linear',
                                             '1',
                                             '1',
                                             '1']]},
                   'barostat': {'Pcoupling': 'tri',
                                'Pdamp': '1',
                                'Pstart': '1.01325',
                                'Pstop': '1.01325',
                                'mtk': 'yes',
                                'pchain': '5',
                                'type': 'npt'},
                   'integrator': 'npt',
                   'nsteps': 10000,
                   'thermostat': {'Tdamp': '0.1',
                                  'Tstart': '300',
                                  'Tstop': '300',
                                  'tchain': '5',
                                  'type': 'npt'},
                   'timestep': 0.001,
                   'units': 'metal'}],
 'log.1.lammps': [{'active_fixes': {'com': ['free',
                                            'momentum',
                                            ['1000',
                                             'linear',
                                             '1',
                                             '1',
                                             '1']],
                                    'md': ['free',
                                           'npt',
                                           ['temp',
                                            '300',
                                            '300',
                                            '0.1',
                                            'tri',
                                            '1.01325',
                                            '1.01325',
                                            '1',
                                            'tchain',
                                            '5',
                                            'pchain',
                                            '5',
                                            'mtk',
                                            'yes']]},
                   'barostat': {'Pcoupling': 'tri',
                                'Pdamp': '1',
                                'Pstart': '1.01325',
                                'Pstop': '1.01325',
                                'mtk': 'yes',
                                'pchain': '5',
                                'type': 'npt'},
                   'integrator': 'npt',
                   'nsteps': 10000000,
                   'thermostat': {'Tdamp': '0.1',
                                  'Tstart': '300',
                                  'Tstop': '300',
                                  'tchain': '5',
                                  'type': 'npt'},
                   'timestep': 0.001,
                   'units': 'metal'}],
 'log.em.lammps': [{'active_fixes': {},
                    'integrator': 'minimize',
                    'minimize_prop': {'etol': 0.0001,
                                      'ftol': 1e-06,
                                      'maxeval': 1000,
                                      'maxiter': 100}}],
 'log.nve.lammps': [{'active_fixes': {'1': ['all', 'nve', []]},
                     'integrator': 'nve',
                     'nsteps': 100,
                     'units': 'lj'}],
 'log.nvt.lammps': [{'active_fixes': {'1': ['all',
                                            'nvt',
                                            ['temp', '1', '1', '1']]},
                     'integrator': 'nvt',
                     'nsteps': 100,
                     'thermostat': {'Tdamp': '1',
                                    'Tstart': '1',
                                    'Tstop': '1',
                                    'type': 'nvt'},
                     'units': 'lj'}],
 'log.nvt.sub_vars.lammps': [{'active_fixes': {'1': ['all',
                                                     'nvt',
                                                     ['temp',
                                                      '1',
                                                      '1',
                                                      '1']]},
                              'integrator': 'nvt',
                              'nsteps': 100,
                              'thermostat': {'Tdamp': '1',
                                             'Tstart': '1',
                                             'Tstop': '1',
                                             'type': 'nvt'},
                              'units': 'lj'}],
 'log.nvt_npt.lammps': [{'active_fixes': {'1': ['all',
                                                'npt',
                                                ['temp',
                                                 '1',
                                                 '1',
                                                 '1',
                                                 'iso',
                                                 '1',
                                                 '1',
                                                 '10']]},
                         'integrator': 'nvt',
                         'nsteps': 100,
                         'thermostat': {'Tdamp': '1',
                                        'Tstart': '1',
                                        'Tstop': '1',
                                        'type': 'nvt'},
                         'units': 'lj'},
                        {'active_fixes': {'1': ['all',
                                                'npt',
                                                ['temp',
                                                 '1',
                                                 '1',
                                                 '1',
                                                 'iso',
                                                 '1',
                                                 '1',
                                                 '10']]},
                         'barostat': {'Pcoupling': 'iso',
                                      'Pdamp': '10',
                                      'Pstart': '1',
                                      'Pstop': '1',
                                      'type': 'npt'},
                         'integrator': 'npt',
                         'nsteps': 100,
                         'thermostat': {'Tdamp': '1',
                                        'Tstart': '1',
                                        'Tstop': '1',
                                        'type': 'npt'},
                         'units': 'lj'}],
 'log.nvt_nvt.lammps': [{'active_fixes': {'1': ['all',
                                                'nvt',
                                                ['temp', '1', '1', '1']]},
                         'integrator': 'nvt',
                         'nsteps': 100,
                         'thermostat': {'Tdamp': '1',
                                        'Tstart': '1',
                                        'Tstop': '1',
                                        'type': 'nvt'},
                         'units': 'lj'},
                        {'active_fixes': {'1': ['all',
                                                'nvt',
                                                ['temp', '1', '1', '1']]},
                         'integrator': 'nvt',
                         'nsteps': 1000,
                         'thermostat': {'Tdamp': '1',
                                        'Tstart': '1',
                                        'Tstop': '1',
                                        'type': 'nvt'},
                         'units': 'lj'}]
}