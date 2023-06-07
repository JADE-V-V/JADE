#!/bin/bash

# modules
module purge
module load standard/2014-08-12            
module load dot  
module load gcc/11.2.0
module load openmpi/4.1.4
module load cmake/3.21.0
module load python/3.7
export CC=/usr/local/depot/openmpi-4.1.4-gcc-11.2.0/bin/mpicc
export CXX=/usr/local/depot/openmpi-4.1.4-gcc-11.2.0/bin/mpic++

# workdir
export WORKDIR=/home/sbradnam/Software/freia/OPENMC_311022

# hdf5
export HDF5_ROOT=$WORKDIR/hdf5/hdf5-1.8.16/build/hdf5
export PATH=$HDF5_ROOT/bin:$PATH
export LD_LIBRARY_PATH=$HDF5_ROOT/lib:$LD_LIBRARY_PATH

# openmc
export OPENMC_DIR=$WORKDIR/openmc/build/openmc
export LD_LIBRARY_PATH=$OPENMC_DIR/lib64:$LD_LIBRARY_PATH
