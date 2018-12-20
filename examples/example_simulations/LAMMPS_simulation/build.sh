#!/bin/bash

MODE=$1


FILE_START='at_calcite_6x6x2_graf_1961.data'
FILE_FF=( 'ff-ae_caco3.lmp' ) 


FLAG_CLEAN=0
FLAG_EXIT=0
case $MODE in 
  cleanup|clean)
  FLAG_CLEAN=1
  FLAG_EXIT=1
  ;;
  rebuild)
  FLAG_CLEAN=1
  ;;
  *)
  ;;
esac

[[ "${FLAG_CLEAN}" == "1" ]] && rm -rf EM_and_Equilibration production
[[ "${FLAG_CLEAN}" == "1" && -L system_start.data ]] && unlink system_start.data

[[ "${FLAG_EXIT}" == "1" ]] && exit

[[ ! -f system_start.data ]] && ln -s $FILE_START system_start.data

FOLDER=EM_and_Equilibration
[[ ! -d ${FOLDER} ]] && mkdir ${FOLDER}
pushd ${FOLDER}
  ln -s ../system_start.data
  for i in ${FILE_FF[@]}; do ln -s ../$i; done
  ln -s ../input.0.lammps
popd


FOLDER=production
[[ ! -d ${FOLDER} ]] && mkdir ${FOLDER}
pushd ${FOLDER}
  ln -s ../EM_and_Equilibration/final_data.0
  ln -s ../EM_and_Equilibration/final_restart.0
  for i in ${FILE_FF[@]}; do ln -s ../$i; done
  ln -s ../input.1.lammps
popd


