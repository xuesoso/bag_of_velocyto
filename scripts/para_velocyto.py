#!/oak/stanford/groups/quake/yuanxue/resources/anaconda3/envs/velocyto/bin/python
# vim: fdm=indent
'''
author:     YSX
date:       20/01/19
content:    Call Velocyto on a list of SmartSeq2 bam files
'''
import os
import sys
import glob
import argparse
import subprocess as sp
from pathlib import Path
import pysam


if __name__ == '__main__':

    pa = argparse.ArgumentParser(description='Velocyto mapping in parallel')
    pa.add_argument(
        '--bam_folder',
        help='Parent folder of subfolders with 1 bam in each.')
    pa.add_argument(
        '--dry',
        action='store_true',
        help='Dry run')
    pa.add_argument(
        '--output',
        required=True,
        help='Parent folder for the output. For each input subfolder, an output subfolder will be made')
    pa.add_argument(
            '-n',
            type=int,
            default=100,
            help='Number of samples per para_velocyto call')
    pa.add_argument(
            '--annotationDir',
            required=True,
            help='Path to the genome annotation .gtf')
    pa.add_argument(
            '--repeat_mask',
            type=str,
            default=None,
            help='Path to the repeat mask .gtf')
    pa.add_argument(
            '--local',
            action='store_true',
            help='Do not send to cluster, do everything locally')
    pa.add_argument(
            '--cpus-per-task', type=int, default=6,
            help='Number of CPUs for each velocyto call',
            )
    pa.add_argument(
            '--mem', type=int, default=8000,
            help='RAM memory in MB for each velocyto call',
            )
    pa.add_argument(
            '--time', default='10:00:00',
            help='Time limit on each group of velocyto jobs (see slurm docs for format info)',
            )
    pa.add_argument(
            '--sort',
            action='store_true',
            help='Sort all the bam files first with samtools.'
            )
    args = pa.parse_args()

    print('Find velo_job.py')
    job_fn = os.path.dirname(os.path.abspath(__file__))+'/velo_job.py'
    if not os.path.isfile(job_fn):
        raise IOError('velo_job.py not found')

    print('Make output root folder')
    args.output = args.output.rstrip('/')+'/'
    if not args.dry:
        os.makedirs(args.output, exist_ok=True)

    if not args.local:
        print('Make job log folder')
        log_fdn = args.output+'logs/'
        if not args.dry:
            os.makedirs(log_fdn, exist_ok=True)

    print('Scan input folder')
    args.bam_folder = args.bam_folder.rstrip('/')+'/'
    samplenames = [x for x in os.listdir(args.bam_folder) if len(glob.glob(args.bam_folder+x+'/*.bam')) > 0]
    if len(samplenames) == 0:
        raise IOError('No input subfolders')
    fn_bams = []
    for sn in samplenames:
        fn = glob.glob(args.bam_folder+sn+'/*.bam')
        if len(fn) == 0:
            print(sn)
            raise IOError('Sample does not have at least one bam in the folder: {:}'.format(sn))
        elif len(fn) > 1:
            print(sn)
            raise IOError('Sample has more than one bam in the folder: {:}'.format(sn))
        '''
        Here we rename "Aligned.out.bam" as "SAMPLE_ID.bam"
        because otherwise Velocyto cannot assign a the sample name
        '''
        desired_name = fn[0].split('/')
        if desired_name[-1] == 'Aligned.out.bam':
            desired_name[-1] = desired_name[-2] + '.bam'
            desired_name = '/'.join(desired_name)
            os.rename(fn[0], desired_name)
        else:
            desired_name = fn[0]
        desired_name = os.path.abspath(desired_name)
        fn_bams.append(desired_name)
    print('Split input samples into batches of {:} samples each'.format(args.n))
    n = args.n
    n_samples = len(samplenames)
    n_groups = ((n_samples - 1) // args.n) + 1
    groups = [samplenames[i * n: (i+1) * n] for i in range(n_groups)]
    group_bams = [fn_bams[i * n: (i+1) * n] for i in range(n_groups)]
    print('{:} groups'.format(n_groups))
    print('Run Velocyto')
    for ig, (group, group_bam) in enumerate(zip(groups, group_bams)):
        groupname = 'group_{:}'.format(ig+1)
        job_out_fn = log_fdn+'{:}.out'.format(groupname)
        job_err_fn = log_fdn+'{:}.err'.format(groupname)
        bams = group_bam
        if args.repeat_mask:
            call = [
                'sbatch',
                '-o', job_out_fn,
                '-e', job_err_fn,
                '-N', '1',
                '--job-name', 'pv-{:}'.format(groupname),
                '--cpus-per-task={:}'.format(args.cpus_per_task),
                '--mem={:}'.format(args.mem),
                '--time={:}'.format(args.time),
                '--partition=quake,normal', job_fn,
                '--group-name', str(ig+1),
                '--output', args.output,
                '--repeat_mask', args.repeat_mask,
                '--bams', ' '.join(bams),
                '--annotationDir', args.annotationDir,
                ]
        else:
            call = [
                'sbatch',
                '-o', job_out_fn,
                '-e', job_err_fn,
                '-N', '1',
                '--job-name', 'pv-{:}'.format(groupname),
                '--cpus-per-task={:}'.format(args.cpus_per_task),
                '--mem={:}'.format(args.mem),
                '--time={:}'.format(args.time),
                '--partition=quake,normal', job_fn,
                '--group-name', str(ig+1),
                '--output', args.output,
                '--bams', ' '.join(bams),
                '--annotationDir', args.annotationDir,
                ]
        if args.sort:
            call.append('--sort')
        if args.dry:
            call.append('--dry')
        print(' '.join(call))
        if not args.dry:
            sp.run(call, check=True)
