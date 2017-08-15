import os
import time
from diagnostic_module import *

threads = "4"
file1 = "/home/ae42909/synthetic_RNAseq/mappingRNAseq/concatenated_fastaFiles/Potato_withViruses_1.fastq"
file2 = "/home/ae42909/synthetic_RNAseq/mappingRNAseq/concatenated_fastaFiles/Potato_withViruses_2.fastq"
#file1 = "/home/ae42909/Scratch/100_Potato_withViruses_1.fastq"
#file2 = "/home/ae42909/Scratch/100_Potato_withViruses_2.fastq"
user_format = "fastq"
out_dir = "/home/ae42909/Scratch/synthPotato_krakenDB_viral"
#out_dir = "/home/ae42909/Scratch/100Seq_krakenDB_viral"
trimlen = "50"
kraken_db = "/home/ae42909/Scratch/krakenDB_viral/"
kaiju_nodes = "/mnt/shared/scratch/ae42909/201609_BBSRC_Diagnostics/kaiju/kaijudb/nodes.dmp"
kaiju_names = "/mnt/shared/scratch/ae42909/201609_BBSRC_Diagnostics/kaiju/kaijudb/names.dmp"
kaiju_fmi = "/mnt/shared/scratch/ae42909/201609_BBSRC_Diagnostics/kaiju/kaijudb/kaiju_db.fmi"
kaiju_missmatch = "5"

# Check that out_dir has "/" at the end
if out_dir[-1] != "/":
    out_dir = out_dir + "/"

# Check out_dir exits else make dir
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

os.chdir(out_dir)

t0 = time.time()
# Test data format - fasta or fastq
test_format(file1, user_format)
t1 = time.time()

# QC and trim data
fastqc_trim(out_dir, file1, trimlen, threads, file2)
t2 = time.time()

# Order and replace names
if file2:
    rename_seq("PE_trimmed_data_1P", out_dir, user_format, paired = "1")
    rename_seq("PE_trimmed_data_2P", out_dir, user_format, paired = "2")
else:
    rename_seq("SE_trimmed_data", out_dir, user_format, paired = False)
t3 = time.time()

# Kraken classification
if file2:
    kraken_class("renamed_file1.fastq", threads, user_format, kraken_db, "renamed_file2.fastq")
else:
    kraken_class("rename_file.fastq", threads, kraken_db, user_format)
t4 = time.time()

# Subset viral and unclassified sequences
seq_reanalysis("kraken_table.txt", "kraken_labels.txt", out_dir, user_format, "renamed_file1.fastq", "renamed_file2.fastq")
t5 = time.time()

# Kaiju classification of subset sequences
kaiju_class("subset_file1.fastq", threads, kaiju_nodes, kaiju_fmi, kaiju_names, kaiju_missmatch, kraken_db, "subset_file2.fastq")
t6 = time.time()

# Merege results
result_analysis(out_dir, "kraken_FormattedTable.txt", "kaiju_table.txt", "kaiju_labels.txt", "ID1.txt", "ID2.txt")
t7 = time.time()

print "testing format = " + str((t1-t0)/3600)
print "fastq and trim = " + str((t2-t1)/3600)
print "rename sequences = " + str((t3-t2)/3600)
print "kraken classification = " + str((t4-t3)/3600)
print "subset vrl and unclas sequences = " + str((t5-t4)/3600)
print "kaiju classification = " + str((t6-t5)/3600)
print "Results = " + str((t7-t6)/3600)
print "total = " + str((t7-t0)/3600)

