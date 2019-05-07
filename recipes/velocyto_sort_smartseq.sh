#!/bin/bash

DIR="$(cd "$(dirname "$0")"/.. && pwd)"
source activate velocyto
module load biology samtools/1.8
python $DIR/scripts/para_velocyto.py --sort --annotationDir $2 --output $3 --bam_folder $1 
