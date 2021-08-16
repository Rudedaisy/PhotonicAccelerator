import os
import subprocess
import time
import sys
sys.path.append('../')
from MemObj import MemObj

# -------- USER PARAMETERS ---------- #
# Instructions: place all cacti parameters as a list. For visualization, restrict sweeps to 2 dimensions.

cwd = os.getcwd()
os.chdir("../")

golden_config_path = os.path.join(cwd, "../mem_cfgs/SRAM-64MB.cfg")
cacti_path = os.path.join(cwd, "../../cacti/")
dump_path = os.path.join(cwd, "sweep_data/")
summary_path = os.path.join(cwd, "sweep_data/summary.csv")
dump_all = True # generate all cacti config files for this sweep?

size = [67108864] # bytes
#line_size = [1024] # bytes
line_size = range(1, 2048)
associativity = [2]
banks = [1]
technode = [0.065] # um
#temp = range(300, 410, 10) # K
temp = [360]

# ----------------------------------- #

# Create and generate new cacti config
def gen_cfg(golden_config_path, new_config_path, size, line_size, associativity, banks, technode, temp):
    fin = open(golden_config_path, "r")
    towrite = ""
    for line in fin:
        line_split = line.split(' ')
        if len(line) < 3:
            towrite += line
        elif line[0] == '/' and line[1] == '/':
            continue
        elif line[0] == '#':
            towrite += line
        elif line_split[0].strip() == "-size":
            towrite += ("-size (bytes) " + str(size) + "\n")
        elif line_split[0].strip() == "-block":
            towrite += ("-block size (bytes) " + str(line_size) + "\n")
        elif line_split[0].strip() == "-output/input":
            towrite += ("-output/input bus width " + str(line_size * 8) + "\n")
        elif line_split[0].strip() == "-associativity":
            towrite += ("-associativity " + str(associativity) + "\n")
        elif line_split[0].strip() == "-UCA":
            towrite += ("-UCA bank count " + str(banks) + "\n")
        elif line_split[0].strip() == "-technology":
            towrite += ("-technology (u) " + str(technode) + "\n")
        elif line_split[0].strip() == "-operating":
            towrite += ("-operating temperature (K) " + str(temp) + "\n")
        else:
            towrite += line
    fin.close()
    fout = open(new_config_path, "w")
    fout.write(towrite)
    fout.close

# Progress bar function
# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress):
    barLength = 10 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rProgress: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()
    
results = "Size (Bytes),\tLine Size (Bytes),\tAssociativity,\tNum Banks,\tTechnology Node (um),\tOperating Temp (K),\tCycle time (s),\tPer-Byte Read Energy (J),\tPer-Byte Write Energy (J),\tStatic Power (W),\tArea (mm2),\n"
total_progress = len(size)*len(line_size)*len(associativity)*len(banks)*len(technode)*len(temp)
i = 0.0
for s in size:
    for ls in line_size:
        for a in associativity:
            for b in banks:
                for tec in technode:
                    for tem in temp:
                        if dump_all:
                            cur_cfg = os.path.join(cwd, "sweep_data/SRAM_"+str(s)+"_"+str(ls)+"_"+str(a)+"_"+str(b)+"_"+str(tec)+"_"+str(tem)+".cfg")
                        else:
                            cur_cfg = os.path.join(cwd, "sweep_data/SRAM_temp.cfg")
                        gen_cfg(golden_config_path, cur_cfg, s, ls, a, b, tec, tem)
                        i += 1
                        update_progress(i / total_progress)
                        try:
                            # Let MemObj do all the work extracting results
                            memobj = MemObj(os.path.join(cwd, "sweep.cfg"), 1, cacti_path, cur_cfg)
                            results += str(s)+",\t"+str(ls)+",\t"+str(a)+",\t"+str(b)+",\t"+str(tec)+",\t"+str(tem)+",\t"+str(memobj.latency)+",\t"+str(float(memobj.read_energy) / ls)+",\t"+str(float(memobj.write_energy) / ls)+",\t"+str(memobj.static_power)+",\t"+str(memobj.area)+",\n"
                            del memobj
                        except:
                            print("Warn: config size={}/linesize={}/assoc={}/banks={}/technode={}/temp={} invalid. Skipping datapoint".format(s, ls, a, b, tec, tem))
                            continue
                        
fp = open(summary_path, "w")
fp.write(results)
fp.close()

print(results)
