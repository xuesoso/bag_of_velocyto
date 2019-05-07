#!/bin/bash

DIR="$(cd "$(dirname "$0")"/.. && pwd)"
source activate velocyto
python $DIR/scripts/para_velocyto.py --annotationDir $2 --output $3 --bam_folder $1 
