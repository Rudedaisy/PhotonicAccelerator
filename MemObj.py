"""
File:     MemObj.py
Author:   Edward Hanson (edward.t.hanson@duke.edu)
Desc:     Memory object simulation. Parameters are initialized using integrated CACTI
"""

import os
import subprocess
import configparser as cp

class MemObj:

    def __init__(self, config_path, num_ports, CACTI_path, config_fname, memstats_fname=("CACTI.out")):
        """
        num_ports      - if only 1 port, assume only read OR write each cycle (rd/wr port)
                       - if 2 ports, assume one read & one write port
        CACTI_path     - path to CACTI root directory
        config_fname   - name of local config file for this specific memory object
        memstats_fname - name of the CACTI stats output file
        """

        self.config = cp.ConfigParser()
        self.config.read(config_path)
        
        # These parameters will be initialized using the config file
        self.latency = self.read_energy = self.write_energy = self.static_power = self.area = None
        # Number of ports
        self.num_ports = num_ports
        assert (self.num_ports == 1) or (self.num_ports == 2), "Unsupported port count!"
        # Commands buffered for each update_state()
        self.toread = False
        self.towrite = False
        # Number of ports
        
        # Run CACTI and send results to local file
        cwd = os.getcwd()
        with open(os.path.join(cwd, "out", memstats_fname), 'w') as fout:
            subprocess.run(["./cacti", "-infile", os.path.join(cwd, "mem_cfgs", config_fname)], cwd=CACTI_path, stdout=fout, check=True)
            fout.close()
            
        # Read cacti stats file and import key stats
        fin = open(os.path.join(cwd, "out", memstats_fname), 'r')
        for line in fin:
            if self.latency==None and "Cycle time (ns):" in line:
                self.latency = float(line.split(':')[1].strip()) * 1e-9
            elif self.read_energy==None and (("Total dynamic read energy per access (nJ):" in line) or ("Read Energy (nJ):" in line)):
                self.read_energy = float(line.split(':')[1].strip()) * 1e-9
            elif self.write_energy==None and (("Total dynamic write energy per access (nJ):" in line) or ("Write Energy (nJ):" in line)):
                self.write_energy = float(line.split(':')[1].strip()) * 1e-9
            elif self.static_power==None and (("Total leakage power of a bank (mW):" in line) or ("Leakage Power I/O (mW):" in line)): #("Leakage Power Open Page (mW):" in line):
                self.static_power = float(line.split(':')[1].strip()) * 1e-3
            elif "Data array: Area (mm2):" in line:
                self.area = float(line.split(':')[2].strip())

        assert self.latency != None, "Error obtaining memory latency"
        assert self.read_energy!= None, "Error obtaining memory read energy"
        assert self.write_energy != None, "Error obtaining memory write energy"
        assert self.static_power != None, "Error obtaining memory static power"
        assert self.area != None, "Error obtaining memory area"

        leakage_scale = float(self.config.get("memory", "leakage_scale"))
        self.static_power = self.static_power * leakage_scale

        if not int(self.config.get("general", "en_buffs")):
            self.read_energy = self.write_energy = self.static_power = 0
        
        #print(self.latency, self.read_energy, self.write_energy, self.static_power, self.area)

    def update_state(self, toread=False, towrite=False):
        """
        Buffer read/write commands for this cycle
        """
        assert (self.num_ports == 2) or (not toread) or (not towrite), "Cannot read and write in same cycle with only 1 port!"

        self.toread = toread
        self.towrite = towrite

    def apply_latch(self):
        """
        Return latency and dynamic energy
        """
        return self.latency, self.read_energy, self.write_energy
        
def main():
    mem = MemObj("../cacti", "cache.cfg")
    print("MemObj test done")

if __name__ == "__main__":
    main()
