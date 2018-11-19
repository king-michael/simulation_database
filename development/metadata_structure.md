main (contained in main table, no MetaEntry requeired)
---
|keyword|content|OpenQuestions| 
|-------|-------|-------------|
| owner | me, you |
| path | where to find the simulation | ?
| url | linked url to the simulation | 
| description | description of the simulation | 
| created_on | creation date | |
| added_on | added to the database | 
| updated_on | last update in the database |
| type | what kind of entry is this | 

simulation (MetaGroup)
---
|keyword|content|OpenQuestions| 
|-------|-------|-------------|
| engine | LAMMPS, GROMACS, CHARMM, etc. |
| sim_type |  | ?
| n_steps | | (targeted vs simulated?)
| simulation_length | time units | brauchen wir das? Kann das nicht beim rauslesen berechnet werden?
| time_step | | |
| method | | unterschied zu sim_type? |


system (MetaGroup)
---
|keyword|content|OpenQuestions| 
|-------|-------|-------------|
| system_type | protein, mineral, polymere |
| n_atoms | total number of atoms |
| n_solvent | number of solvent atoms | or molecules???
| n_solute | number of solute atoms | 


thermostat (MetaGroup)
---
|keyword|content|OpenQuestions| 
|-------|-------|-------------|
| thermostat_type | | sollten das mapping irgendwo speichern
| T_start | start temperature |
| T_end | final temperature |
| T_relax | relaxation time |
| thermostat_info | additional parameter | how should we do this? a list of keywords and then seperate keywords into the group? a string?

barostat (MetaGroup)
---
|keyword|content|OpenQuestions| 
|-------|-------|-------------|
| barostat_type | | sollten das mapping irgendwo speichern
| p_coupling | pressure coupling | 
| p_start | start pressure |
| p_end | final pressure |
| p_relax | relaxation time |
| barostat_info | additional parameter | how should we do this? a list? a string?

