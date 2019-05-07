#!/usr/bin/env python
# vim: fdm=indent
'''
author:     YSX
date:       20/01/19
content:    Call Velocyto on a list of SmartSeq2 bam files (cluster job)
'''
import os
import sys
import argparse
import numpy as np
import pandas as pd
import subprocess as sp
from pathlib import Path
import time
import pysam


def printfl(*args):
    '''Flushed printing to stdout'''
    return print(*args, flush=True)


if __name__ == '__main__':
    pa = argparse.ArgumentParser(description='Parallel velocyto')
    pa.add_argument(
            '--group-name',
            required=True,
            help='Name of the group')
    pa.add_argument(
            '--bams',
            required=True,
            help='The filenames of the bams')
    pa.add_argument(
        '--dry',
        action='store_true',
        help='Dry run')
    pa.add_argument(
        '--output',
        required=True,
        help='Parent folder for the output.')
    pa.add_argument(
            '--annotationDir',
            default=None,
            help='Path to the annotation .gtf')
    pa.add_argument(
            '--repeat_mask',
            default=None,
            help='Path to the repeat mask .gtf')
    pa.add_argument(
            '--sort',
            action='store_true',
            help='Sort the bam files first with samtools.')
    args = pa.parse_args()

    args.output = args.output.rstrip('/')+'/'
    output_tmp_velocyto = args.output+'velocyto_TMP_group_{:}/'.format(args.group_name)

    printfl('Mapping group {:}'.format(args.group_name))
    flag_fn = args.output+'/group_'+str(args.group_name)+'.done'
    args.sample_name = 'group_'+str(args.group_name)
    if os.path.isfile(flag_fn):
        printfl('Flag file found, skipping sample')
    else:
        if args.sort:
            for f in (args.bams).split(' '):
                call = ['samtools',
                        'sort', f,
                        '-o', f
                       ]
                printfl(' '.join(call))
                if not args.dry:
                    sp.run(call, check=True)
        if args.repeat_mask:
            call = [
                os.getenv('velocyto', 'velocyto'),
                'run-smartseq2',
                '-e', args.sample_name,
                '-o', args.output,
                '-m', args.repeat_mask,
            ]
        else:
            call = [
                os.getenv('velocyto', 'velocyto'),
                'run-smartseq2',
                '-e', args.sample_name,
                '-o', args.output,
            ]
        for f in (args.bams).split(' '):
            call.append(f)
        call.append(args.annotationDir)
        printfl(' '.join(call))
        if not args.dry:
            sp.run(call, check=True)
            Path(flag_fn).touch()
