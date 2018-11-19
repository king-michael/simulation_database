__main__ (contained in main table, no MetaEntry requeired)
---
- owner
- path
- url
- description
- created_on
- added_on
- updated_on
- type

__simulation__ (MetaGroup)
- engine (LAMMPS, GROMACS, CHARMM, etc.)
- sim_type
- n_steps (targeted vs simulated?)
- simulation_length (time units)
- time_step
- method (metaD, what ever)

__system__ (MetaGroup)
---
- system_type (protein, mineral)
- natoms
- nsolvent
- nsolute

__thermostat__ (MetaGroup)
---
- thermostat type
- T_start
- T_end
- T_relax
- thermostat info ?

__barostat__ (MetaGroup)
---
- barostat type
- p_coupling ?
- p_start
- p_end ?
- p_relax ?
