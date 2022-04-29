#!/bin/bash
#
#SBATCH --job-name=Test
#SBATCH --partition=compute
#SBATCH --output=out.txt
#SBATCH --error=err.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1024
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=hudson.borja-da-rocha@college-de-france.fr
#SBATCH --time=02:00:00

## To load spack environment
source /share/softs/spack/share/spack/setup-env.sh

# source /lustre/home/hudson.borja/.venv/with_meshio/bin/activate

#scl enable devtoolset-9 bash

## To load fenics and dependencies
spack load fenics
spack load py-h5py%gcc@9.3.1
spack load gmsh%gcc@9.3.1


## For remeshin with mmg
spack load mmg%gcc@9.3.1
export MMG="/share/softs/spack/opt/spack/linux-centos7-skylake_avx512/gcc-9.3.1/gcc-9.3.1/mmg-5.6.0-7gqt2uvbe3abajuuarwupr324psm6hur/bin"

## For meshio that was installed locally with py-pip
export PATH="/lustre/home/hudson.borja/.local/bin:$PATH"

python /lustre/home/hudson.borja/Nematic/main.py config.conf
 
