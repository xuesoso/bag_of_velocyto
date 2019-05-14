# Bag of Velocyto
Cluster (Slurm) submission of velocyto alignment for RNA velocity analysis.

Inspired by [iosonofabio/Bag of Stars](https://github.com/iosonofabio/bag_of_stars)

Work in progress
----------------
+ Add usage case 

Prerequisites
-------------
+ [Velocyto CLI](http://velocyto.org/)
+ Python 3.6+
+ GFF3 / GTF annotation file

Convert GFF3 to GTF
-------------------
Velocyto requires annotation file in the GTF format. I include a custom python script to convert GFF3 annotation to GTF format suited for Velocyto input. It is recommended that you obtain the GTF annotation whenever possible. My conversion script only converts Exon features to GTF format as they are the only things that Velocyto cares about. Features labeled as repeats will be separately parsed as a repeat_mask file.
