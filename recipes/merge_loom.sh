#!/bin/bash
#
#SBATCH --job-name=merge_counts
#
#SBATCH --time=0:20:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=2G
#SBATCH --partition=quake,normal

DIR="$(cd "$(dirname "$0")"/.. && pwd)"
source activate velocyto
python $DIR/scripts/merge_loom.py $1 $2
