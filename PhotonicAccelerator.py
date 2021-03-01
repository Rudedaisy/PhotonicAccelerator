"""
File:     PhotonicAccelerator.py
Author:   Edward Hanson (edward.t.hanson@duke.edu)
Desc:     Complete description of photonic accelerator system
"""

from PhotonicSubsys import PhotonicSubsys
from DigitalSubsys import DigitalSubsys
from MemObj import MemObj

class PhotonicAccelerator:

    def __init__(self):
        """
        WORK IN PROGRESS
        TODO:
        - Compute critical path latency and total area
        - Compute cycle-accurate energy costs
        - Implement flexible memory subsystem with handshaking signals
        - Implement updated control flow
        """

        # Default layer stats
        self.in_obj_size = 1024
        self.out_obj_size = 256
        self.in_channels = 3
        self.out_channels = 64
        self.kernel_size = 9
        self.kernels_per_map = 1 ##
        
        # Constants
        self.MS_dim = 1e3
        self.MS_pix = self.MS_dim * self.MS_dim
        
        # Registers for Finite-state-machine
        self.cycle = 0
        self.state = 0
        self.start = False
        self.read_ready = True
        self.curr_out_channel = 0
        self.curr_in_channel = 0

        # Tracking variables
        self.obj_reads = 0
        self.kern_reads = 0
        self.obj_writes = 0
        self.fft_convs = 0
        
        ###### TODO: REPLACE WITH FLEXIBLE MEMORY HIERARCHY SUPERCLASS
        self.kernel_buffer = MemObj(1, "../cacti", "cache.cfg")
        self.object_buffer = MemObj(2, "../cacti", "cache.cfg")
        #self.resid_buffer = MemObj("../cacti", "cache.cfg")
        self.mem_access_width = 1e3
        # Instantiate digital subsys
        self.digital = DigitalSubsys(MS_dim=self.MS_dim, DAC_group_size=1, ADC_group_size=1)
        # Instantiate photonic subsys
        self.photonic = PhotonicSubsys(MS_pix=self.MS_pix, Nb=8)

        # Determine critical path latency
        self.critical_path_latency = max(self.photonic.t, self.digital.latency, self.kernel_buffer.latency, self.object_buffer.latency)
        print("Critical path = {}".format(self.critical_path_latency))
        
    def load_layer(self, in_obj_size, out_obj_size, in_channels, out_channels, kernel_size):
        self.in_obj_size = in_obj_size
        self.out_obj_size = out_obj_size
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.kernels_per_map = 1 ##
        return

    def compute_stats(self):
        """
        WORK IN PROGRESS
        """
        total_latency = self.critical_path_latency * self.cycle
        photonic_energy = self.fft_convs * self.photonic.E
        digital_energy = total_latency * self.digital.avgPower
        obj_energy = (self.obj_reads * self.object_buffer.read_energy) + (self.obj_writes * self.object_buffer.write_energy) + (total_latency * self.object_buffer.static_power)
        kern_energy = (self.kern_reads * self.kernel_buffer.read_energy) + (total_latency * self.kernel_buffer.static_power)

        print("Total latency = {}".format(total_latency))
        print("Photonic energy = {}".format(photonic_energy))
        print("Digital energy = {}".format(digital_energy))
        print("Object buffer energy = {}".format(obj_energy))
        print("Kernel buffer energy = {}".format(kern_energy))
        
        return
    
    def update_state(self, start=False):
        """
        Finite-state-machine
        States:
        0 - wait
        1 - load object from memory --> present to DAC when ready
        2 - IN PARALLEL: take FFT of object and save --> present to next DAC/MS
                         load kernel(s) from memory --> present to DAC when ready
        3 - (optional) wait state in case of long memory access latency
        4 - IN PARALLEL: IF kernels all done, load FFT of object to next MS
                         perform convolution in frequency-domain
                         buffer next load object from memory
                         SHORT CUT: early increment memory write count here!
        *5 - normalization
        *6 - activation
        *7 - pooling --> present to memory hierarchy when ready
        *8 - store results in memory
        * done in parallel (pipelined) with any other state
        """

        self.start = start
        
        # 0
        if self.state == 0:
            if self.start:
                self.done = False
                self.state = 1
                self.obj_reads = 0
                self.kern_reads = 0
                self.obj_writes = 0
                self.cycle = 0
                self.fft_convs = 0
                self.curr_in_channel = 0
                self.curr_out_channel = 0
            else:
                self.state = 0
        # 1
        elif self.state == 1:
            if self.read_ready:
                self.state = 2
            else:
                self.state = 1
        # 2
        elif self.state == 2:
            if self.read_ready:
                self.state = 4
            else:
                self.state = 3
        # 3
        elif self.state == 3:
            if self.read_ready:
                self.state = 4
            else:
                self.state = 3
        # 4
        elif self.state == 4:
            if self.curr_out_channel >= self.out_channels:
                if self.curr_in_channel >= self.in_channels:
                    self.state = 5
                else:
                    if self.read_ready:
                        self.state = 2
                    else:
                        self.state = 1
            else:
                if self.read_ready:
                    self.state = 4
                else:
                    self.state = 3
        # 5
        elif self.state == 5:
            self.state = 6
        # 6
        elif self.state == 6:
            self.state = 7
        # 7
        elif self.state == 7:
            self.state = 8
        # 8
        elif self.state == 8:
            self.state = 0

        return

    def apply_latch(self):
        """
        WORK IN PROGRESS
        TODO: return energy of the given cycle
        """
        self.cycle += 1
        
        # 0
        if self.state == 0:
            self.done = True
            return
        # 1
        elif self.state == 1:
            if self.read_ready:
                self.obj_reads += self.mem_access_width//self.in_obj_size
            return
        # 2
        elif self.state == 2:
            self.fft_convs += 1
            self.curr_in_channel += 1
            self.curr_out_channel = 0
            if self.read_ready:
                self.kern_reads += self.mem_access_width//(self.kernel_size*self.kernels_per_map)
            return
        # 3
        elif self.state == 3:
            if self.read_ready:
                self.kern_reads += self.mem_access_width//(self.kernel_size*self.kernels_per_map)
            return
        # 4
        elif self.state == 4:
            self.fft_convs += 1
            self.obj_writes += self.mem_access_width//self.out_obj_size
            self.curr_out_channel += self.kernels_per_map
            if self.read_ready and self.curr_out_channel < self.out_channels:
                self.kern_reads += self.mem_access_width//(self.kernel_size*self.kernels_per_map)
            if self.read_ready and self.curr_out_channel >= self.out_channels:
                self.obj_reads += self.mem_access_width//self.in_obj_size
            return
        # 5
        elif self.state == 5:
            return
        # 6
        elif self.state == 6:
            return
        # 7
        elif self.state == 7:
            return
        # 8
        elif self.state == 8:
            self.compute_stats()
            return

def main():
    acc = PhotonicAccelerator()

    acc.update_state(True)
    cycle = 0
    while not acc.done:
        acc.apply_latch()
        acc.update_state()
        cycle += 1
    print("Cycle count = {}".format(cycle))

if __name__ == "__main__":
    main()
