#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os, sys
import shutil
import re


# In[75]:


class Detector():
    regexdict={
                'STRUCTURES' : [
                    ['^.*.pdb',          10],  # pdb file
                    ['^.*.gro',          10],  # gro file
                    ['^.*.psf',          10],  # psf file
                    ['^.*.data',          6],  # LAMMPSDATA file
                ],
                'LAMMPS_INPUT'      : [ ## LAMMPS input scripts
                    ['^input.*.lammps$', 10],  # 10 input.0.lammps input.lammps input_script.lammps input.lammps
                    ['^input.*.lmp$',    10],  # 10 input.lmp 
                    ['^in.init..*$',      7],  #  7 moltemplate files
                    ['^in.settings..*$',  7],  #  7 moltemplate files
                    ['^script.*.lammps$', 4],  #  4 could also be an analysis script
                    ['^in..*$', 2],            #  2 if its nothing else, then maybelammps
                ],
                'LAMMPS_FF'         : [ ## LAMMPS forcefield files
                    ['^forcefield.*.lammps$', 10],  # 10 forcefield.X.lammps forcefield_X.lammps
                    ['^forcefield.*.lmp$',    10],  # 10 forcefield.X.lmp forcefield_X.lmp
                    ['^ff.*.lammps$',         10],  # 10 ff.X.lammps ff_X.lammps ff-X.lammps
                    ['^ff.*.lmp$',            10],  # 10 ff.X.lmp ff_X.lmp ff-X.lmp
                    ['^in..*.sw$',            10],  # 10 sw potentials
                    ['^system..*.sw$',        10],  # 10 sw potentials
                    ['^.*.poly$',               2],  # 2 polymorphic potentials
                    ['^.*.eam$',                2],  # 2 eam potentials
                    ['^.*.eam.fs$',             2],  # 2 eam/fs potentials
                ],
                'LAMMPS_LOG'        : [ ## LAMMPS logfiles
                    ['^log.*.lammps$',        10],  # 10 log.lammps log.X.lammps
                    ['^lammps.*.log$',        10],  # 10 lammps.log
                ],
                'GROMACS' : [
                    ['^.*.tpr',               10],  # 10 tpr file
                    ['^.*.mdp',               10],  # 10 mdp file
                    ['topol.top',             10],  # 10 topol file
                    ['^.*.itp',                6],  #  6 topol file
                ],
                'PYTHON'            : [ ## PYTHON scripts
                    ['^.*.py$',               10],  # 10 python files
                ],
                'JUPYTER-NOTEBOOK'  : [ ## JUPTYTER-NOTEBOOK
                    ['^.*.ipynb$',            10],  # 10 jupter-notebook files
                ],
            }
        
    def compare_with_regex(self,inp,regexlist,rate=True):
        '''iterate check if inp match to anyitem of regexlist, returns raiting for the best hit'''
        if type(inp) == type(str()): 
            res, best_rating = False, 0
            for reg, rating in regexlist:
                res_ = bool(re.match(reg,inp))
                if res_:
                    if rating > best_rating:
                        best_rating=rating
                        res=res_
            return res, best_rating
        elif type(inp) == type(list([])): return [self.compare_with_regexlist(i,regexlist) for i in inp]
        else: raise TypeError('Not str nor list(str,)')
    
    def compare_with_regexdict(self,inp):
        '''iterate over all keys of regexdict, return the best fitting type + raiting'''
        res, best_rating, best_key = False, 0, None
        for key in self.regexdict.keys():
            res_, rating = self.compare_with_regex(inp,self.regexdict[key])
            if res_:
                if rating > best_rating:
                    best_rating=rating
                    res=res_
                    best_key=key
        return res, best_rating,best_key
        # except: raise TypeError("regexlist should be a dict with key = FILETYPE and dict[FILETYPE] = [ ['regexstring']]")


# In[78]:


# TESTLISTS LAMMPS
testlist_str_LAMMPS_INPUT=[
    ['input.0.lammps', True, 'LAMMPS_INPUT'],
    ['input.2.lammps', True, 'LAMMPS_INPUT'],
    ['input.lammps',   True, 'LAMMPS_INPUT'],
    ['input.1.lmp',    True, 'LAMMPS_INPUT'],
    ['input.lmp',      True, 'LAMMPS_INPUT'],
    ['in.lj',          True, 'LAMMPS_INPUT'],
                    ]
testlist_str_LAMMPS_FF=[
    ['in.test.sw',     True, 'LAMMPS_FF'],
]
testlist_str_LAMMPS_LOG=[
    ['log.lammps',     True, 'LAMMPS_LOG'],
    ['log.1.lammps',   True, 'LAMMPS_LOG'],
    ['log.X.lammps',   True, 'LAMMPS_LOG'],
    ['lammps.1.log',   True, 'LAMMPS_LOG'],
]
testlist_str_LAMMPS=testlist_str_LAMMPS_INPUT+testlist_str_LAMMPS_FF+testlist_str_LAMMPS_LOG
# TESTLITS PYTHON
testlist_str_PYTHON=[
    ['input.py',       True, 'PYTHON'],
]
# TESTLISTS UNKNOWN
testlist_str_UNKNOWN=[
    ['inp.lj',        False, 'UNKNOWN'],
    ['input.dat',     False, 'UNKNOWN'],
]


# In[79]:


detector=Detector()
# TESTLAMMPS
testlist_str_TEST=[i for i in testlist_str_LAMMPS]
testlist_str_TEST+=[[f,False,t] for f,_,t in testlist_str_PYTHON]
testlist_str_TEST+=[[f,False,t] for f,_,t in testlist_str_UNKNOWN]
for f,b,t in testlist_str_TEST:
    res = detector.compare_with_regexdict(f)
    print res
    if t != res[2] and b != res[1]: print('Failed: %s --> %s' % (f,t))


# In[ ]:





# In[ ]:





# In[ ]:




