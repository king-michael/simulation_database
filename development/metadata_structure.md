main (contained in main table, no MetaEntry requeired)
---
|keyword|content|
|-------|-------|
| owner | me, you |
| path | where to find the simulation |
| url | linked url to the simulation | 
| description | description of the simulation | 
| created_on | creation date | 
| added_on | added to the database | 
| updated_on | last update in the database |
| type | what kind of entry is this | 

simulation (MetaGroup)
---
|keyword|content|
|-------|-------|
| engine | LAMMPS, GROMACS, CHARMM, etc. 
| sim_type | extension, expansion etc. 
| force_field | gromacs55a7, charmm36m
| n_steps | simulated number of steps
| time_step | used timestep | 
| method | additional methods (MetaDynamic, UmberllaSampling, SWARM, Thermodynamic Integration)


system (MetaGroup)
---
|keyword|content|
|-------|-------|
| system_type | protein, mineral, polymere |
| n_atoms | total number of atoms |
| n_solvent | number of solvent atoms
| n_ions | number of ions
| c_ions | concentration of ions


thermostat (MetaGroup)
---
|keyword|content|OpenQuestions| 
|-------|-------|-------------|
| thermostat_type | | sollten das mapping irgendwo speichern
| T_start | start temperature |
| T_end | final temperature |
| T_relax | relaxation time |
| thermostat_info | additional parameter like `nh-chain-length`
| nh-chain-length | Nose-Hoover chain length


barostat (MetaGroup)
---
|keyword|content|OpenQuestions| 
|-------|-------|-------------|
| barostat_type | | sollten das mapping irgendwo speichern
| p_coupling | pressure coupling | 
| p_start | start pressure |
| p_end | final pressure |
| p_relax | relaxation time |
| barostat_info | additional parameter like `compressibility` 
| compressibility | compressibility of the system 

