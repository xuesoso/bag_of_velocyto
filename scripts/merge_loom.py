#!/oak/stanford/groups/quake/yuanxue/resources/anaconda3/envs/velocyto/bin/python

import sys, glob, loompy

infile = sys.argv[1]
outfile = sys.argv[2]

infile = infile.rstrip('/') + '/'
fn = glob.glob(infile + '*.loom')
print('Merging all files %s' %fn)
if outfile.split('.')[-1] != 'loom':
    outfile = outfile+'.loom'
loompy.combine(fn, outfile)
