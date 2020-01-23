#!/oak/stanford/groups/quake/yuanxue/resources/anaconda3/bin/python

'''
    Automatic conversion of gff3 annotation to gtf format for velocyto mapping.
    Will first figure out whehther each feature is part of a transcript/gene.
    Then we will figure out the linkage between each feature and other features
    e.g. who is your parent feature. For each feature, we will build a dict
    object to traverse between each feature to its parent molecule.
    We will also keep track of features which are annotated as repeats, and we
    export them as a separate repeat masker gtf.
    By default, will save the output gtf and repeatmask as infile.gtf and
    infile.repeatmask.gtf

    infile: Argument supplying the location of the input gff3 file.
    chunk_size: number of lines to store on buffer before writing.
'''

import os, sys

infile = sys.argv[1]
assert infile.split('.')[-1] == 'gff3', 'input file must end with .gff3'
chunk_size = 1000
tmpfile = infile.replace('.gff3', '.tmp')
outfile = infile.replace('.gff3', '.gtf')
maskfile = infile.replace('.gff3', '.repeatmask.gtf')

print('Converting %s to gtf file' %infile)

## First walk-through of the genome just to build a
## transcript to gene name dictionary
parent_dict = {}
type_dict = {}

with open(infile, 'r') as f:
    for line in f.readlines():
        curr = line.strip().split('\t')
        if line[0] != '#' and len(curr) > 8:
            feature_type = curr[2]
            key_val = curr[8].split(';')
            ID = ''
            Parent = ''
            for i in key_val:
                if 'ID=' in i:
                    ID = i.replace('ID=', '')
                elif 'Parent=' in i:
                    Parent = i.replace('Parent=', '')
            if Parent != '' and ID not in parent_dict.keys()\
               and ID != Parent:
                parent_dict[ID] = Parent
            if feature_type in ['mRNA', 'tRNA', 'rRNA', 'tRNA_pseudogene']:
                type_dict[ID] = 'transcript'
            else:
                type_dict[ID] = feature_type
transcript_model = {}
exon_to_transcript_model = {}
for key in parent_dict.keys():
    par = parent_dict[key]
    if type_dict[par] == 'transcript' and type_dict[key] == 'exon':
        exon_to_transcript_model[key] = par
        if par in transcript_model.keys():
            transcript_model[par].append(key)
        else:
            transcript_model[par] = [key]

count = 0
converted_lines = []
repeatmasker = []
if tmpfile in os.listdir():
    os.remove(tmpfile)
with open(infile, 'r') as f:
    with open(tmpfile, 'a') as wo:
        for line in f.readlines():
            curr = line.strip().split('\t')
            if len(curr) > 8 and line[0] != '#':
                feature_type = curr[2]
                source = curr[1]
            else:
                feature_type = ''
            if feature_type != '':
                if feature_type == 'exon' and source != 'repeatmasker':
                    key_val = curr[8].split(';')
                    exon_id = 'None'
                    for i in key_val:
                        if 'ID=' in i:
                            exon_id = i.replace('ID=', '')
                    if exon_id != 'None':
                        gene_id = exon_id
                        if exon_id not in exon_to_transcript_model.keys():
                            transcript_id = exon_id
                        else:
                            transcript_id = exon_to_transcript_model[exon_id]
                        while type_dict[gene_id] != 'gene' and \
                              gene_id in parent_dict.keys():
                            gene_id = parent_dict[gene_id]
                        transcript_name = 'transcript_name "'+str(transcript_id)+'"'
                        transcript_id = 'transcript_id "'+str(transcript_id)+'"'
                        gene_name = 'gene_name "'+str(gene_id)+'"'
                        gene_id = 'gene_id "'+str(gene_id)+'"'
                        exon_id = 'exon_id "'+str(exon_id)+'"'
                        convert = '; '.join([transcript_name, transcript_id,\
                                             gene_name, gene_id])
                        convert += '\n'
                        curr[8] = convert
                        curr = '\t'.join(curr)
                        converted_lines.append(curr)
                elif source == 'repeatmasker':
                    repeatmasker.append(line)
                else:
                    converted_lines.append(line)
                count += 1
            if count % chunk_size == 0:
                for outline in converted_lines:
                    wo.write(outline)
                converted_lines = []
        if len(converted_lines) > 0:
            for outline in converted_lines:
                wo.write(outline)
os.rename(tmpfile, outfile)

with open(maskfile, 'w') as mo:
    for line in repeatmasker:
        mo.write(line)
