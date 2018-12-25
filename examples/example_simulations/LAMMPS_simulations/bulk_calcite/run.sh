#!/bin/bash

MPIRUN_OPTS=""
LMP_EXE=lmp
# LMP_ACCELRATION="-sf gpu -pk gpu 2"
# LMP_ACCELRATION="-sf omp -pk omp 1"
LMP_OPT_ADD="-echo both"

[[ $1 != '' ]] && LMP_EXE=$1

FLAG_EM=1
FLAG_PROD=1

for arg in $@;do
 case $arg in
   lmp*)
    LMP_EXE=$arg
    echo "CHOSE LAMMPS_EXE = $LMP_EXE"
   ;;
   EM_and_Equilibration)
    FLAG_EM=1
    FLAG_PROD=0
   ;;
   production)
    FLAG_EM=0
    FLAG_PROD=1
   ;;
   -n=*)
    CORES=${arg#*=}
    [[ $CORES == "all" ]] && MPIRUN_OPTS="" || MPIRUN_OPTS="-n ${CORES}"
   ;;
 esac
done

#LMP_EXE=lmp

function get_cmd_lmp {
  run_no=$1
  LMP_SCRIPT=input.${run_no}.lammps
  LMP_OPTS="-var iseed0 $RANDOM -var iseed1 $RANDOM -var iseed2 $RANDOM -var run_no $run_no -log log.${run_no}.lammps"
  CMD_LMP="${LMP_EXE} -in ${LMP_SCRIPT} ${LMP_OPTS} ${LMP_OPT_ADD} ${LMP_ACCELRATION}"   
  echo $CMD_LMP
}


if [[ "$FLAG_EM" == "1" ]]; then
pushd EM_and_Equilibration/
  run_no=0
  CMD="mpirun ${MPIRUN_OPTS} $(get_cmd_lmp ${run_no})"
  echo $CMD
  $CMD
popd
fi

if [[ "$FLAG_PROD" == "1" ]]; then
pushd production
  run_no=1
  echo "TEST: ${MPIRUN_OPTS}"
  CMD="mpirun ${MPIRUN_OPTS} $(get_cmd_lmp ${run_no})"
  echo $CMD
  $CMD
popd
fi

