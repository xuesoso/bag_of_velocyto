#!/bin/bash

DIR="$(cd "$(dirname "$0")"/.. && pwd)"
source activate velocyto
module load biology samtools/1.8
python $DIR/scripts/para_velocyto.py --repeat_mask $3 --annotationDir $2 --output $4 --bam_folder $1 
