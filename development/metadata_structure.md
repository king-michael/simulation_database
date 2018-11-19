main (contained in main table, no MetaEntry requeired)
---
- owner
- path
- url
- description
- created_on
- added_on
- updated_on
- type

simulation (MetaGroup)
---
- engine (LAMMPS, GROMACS, CHARMM, etc.)
- sim_type
- n_steps (targeted vs simulated?)
- simulation_length (time units)
- time_step
- method (metaD, what ever)

system (MetaGroup)
---
- system_type (protein, mineral)
- natoms
- nsolvent
- nsolute

thermostat (MetaGroup)
---
- thermostat type
- T_start
- T_end
- T_relax
- thermostat info ?

barostat (MetaGroup)
---
- barostat type
- p_coupling ?
- p_start
- p_end ?
- p_relax ?
