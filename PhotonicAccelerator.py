"""
File:     PhotonicAccelerator.py
Author:   Edward Hanson (edward.t.hanson@duke.edu)
Desc:     Complete description of photonic accelerator system
"""

from PhotonicSubsys import PhotonicSubsys
from DigitalSubsys import DigitalSubsys
from MemObj import MemObj
import math
import numpy as np

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

        # Constants
        self.MS_dim = 3238 #1e3
        self.MS_pix = self.MS_dim * self.MS_dim
        
        # Default layer stats
        self.in_obj_size = 1024
        self.out_obj_size = 256
        self.in_channels = 3
        self.out_channels = 64
        self.kernel_size = 9
        self.stride = 1
        self.channels_per_map = max(1, min(self.MS_pix // self.in_obj_size, self.MS_pix // self.kernel_size))
        self.filters_per_map = 1 
        
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
        self.ops = 0
        
        ###### TODO: REPLACE WITH FLEXIBLE MEMORY HIERARCHY SUPERCLASS
        self.kernel_buffer = MemObj(1, "../cacti", "eDRAM-32MB-25w.cfg")
        self.object_buffer = MemObj(2, "../cacti", "eDRAM-64MB-25w.cfg")
        #self.resid_buffer = MemObj("../cacti", "cache.cfg")
        self.mem_access_width = 1 ##16
        self.banks = 1024
        # Instantiate digital subsys
        self.digital = DigitalSubsys(MS_dim=self.MS_dim, DAC_group_size=1, ADC_group_size=1)
        # Instantiate photonic subsys
        self.photonic = PhotonicSubsys(MS_pix=self.MS_pix, Nb=8)

        # Determine critical path latency
        #self.critical_path_latency = max(self.photonic.t, self.digital.latency, self.kernel_buffer.latency*self.MS_pix/self.mem_access_width/self.banks, self.object_buffer.latency*self.MS_pix/self.mem_access_width/self.banks)
        self.critical_path_latency = 1e-6 ######
        print("Critical path = {}".format(self.critical_path_latency))
        
        # Lifetime summary variables
        self.total_latency = []
        self.total_cycle = []
        self.photonic_energy = []
        self.digital_energy = []
        self.obj_energy = []
        self.kern_energy = []
        self.total_fft_convs = []
        self.total_ops = []
        self.layerwise_MS_util = []
        # buffer width inefficiency
        self.obj_inef = []
        self.obj_write_inef = []
        self.kern_inef = []
        
    def load_layer(self, in_obj_size, out_obj_size, in_channels, out_channels, kernel_size, stride):
        self.in_obj_size = in_obj_size
        self.out_obj_size = out_obj_size
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        
        self.channels_per_map = max(1, min(min(self.MS_pix // in_obj_size, self.MS_pix // kernel_size), self.in_channels))
        # prefer to limit 1 filter at a time --> directly accumulate partial sums
        self.filters_per_map = 1

        # we can directly count the number of OPs (MACs * 2) here
        window_ops = self.kernel_size * self.in_channels * self.out_channels
        #self.ops = window_ops * (self.out_obj_size / self.stride / self.stride) * 2
        self.ops = window_ops * self.out_obj_size

        return

    def compute_stats(self):
        """
        WORK IN PROGRESS
        """
        total_latency = self.critical_path_latency * self.cycle
        photonic_energy = self.fft_convs * self.photonic.E 
        #digital_energy = total_latency * self.digital.avgPower
        #obj_energy = (self.obj_reads * self.object_buffer.read_energy) + (self.obj_writes * self.object_buffer.write_energy) + (total_latency * self.object_buffer.static_power)
        #kern_energy = (self.kern_reads * self.kernel_buffer.read_energy) + (total_latency * self.kernel_buffer.static_power)
        #"""
        # --- Alternative calculation using unit costs
        E_adc = 1.2e-12
        E_dac = 0.3e-12
        E_read = 3.5e-12
        E_write = 3.5e-12
        digital_energy = (self.obj_reads + (self.kern_reads*2)) * self.mem_access_width * E_dac
        digital_energy += (self.obj_writes*2) * self.mem_access_width * E_adc
        obj_energy = (self.obj_reads * self.mem_access_width * E_read) + (self.obj_writes * self.mem_access_width * E_write)
        kern_energy = self.kern_reads * self.mem_access_width * E_read
        #"""
        self.total_latency.append(total_latency)
        self.total_cycle.append(self.cycle)
        self.photonic_energy.append(photonic_energy)
        self.digital_energy.append(digital_energy)
        self.obj_energy.append(obj_energy)
        self.kern_energy.append(kern_energy)
        self.total_fft_convs.append(self.fft_convs)
        self.total_ops.append(self.ops)
        self.layerwise_MS_util.append(float(self.in_obj_size * self.channels_per_map) / self.MS_pix)
        
        print("Total latency \t\t= {}".format(total_latency))
        print("Photonic energy \t= {}".format(photonic_energy))
        print("Digital energy \t\t= {}".format(digital_energy))
        print("Object buffer energy \t= {}".format(obj_energy))
        print("Kernel buffer energy \t= {}".format(kern_energy))

        print("Total energy \t\t= {}".format(photonic_energy + digital_energy + obj_energy + kern_energy))
        print("Avg power \t\t= {}".format((photonic_energy + digital_energy + obj_energy + kern_energy) / total_latency))
        #print(self.obj_reads * self.mem_access_width)
        #print((self.kern_reads*2)* self.mem_access_width)
        #print((self.obj_writes*2) * self.mem_access_width)
        
        return

    def summary(self):
        """ Print lifetime summary """
        print(" --- Total Summary --- ")
        print("CNN latency: \t\t{} s".format(sum(self.total_latency)))
        print("CNN cycle count: \t{}".format(sum(self.total_cycle)))
        total_energy = sum(self.photonic_energy) + sum(self.digital_energy) + sum(self.obj_energy) + sum(self.kern_energy)
        #total_energy = sum(self.digital_energy) + sum(self.obj_energy) + sum(self.kern_energy)
        print("Total energy: \t\t{} J".format(total_energy))
        print("\tPhotonic: \t{:%}".format(sum(self.photonic_energy) / total_energy))
        print("\tDigital: \t{:%}".format(sum(self.digital_energy) / total_energy))
        print("\tObj buffer: \t{:%}\tRead inefficiency: \t{}\tWrite ineffciency: \t{}".format(sum(self.obj_energy) / total_energy, sum(self.obj_inef) / len(self.obj_inef), sum(self.obj_write_inef) / len(self.obj_write_inef)))
        print("\tKern buffer: \t{:%}\tRead inefficiency: \t{}".format(sum(self.kern_energy) / total_energy, sum(self.kern_inef) / len(self.kern_inef)))
        print("Average power: \t\t{} W".format(total_energy / sum(self.total_latency)))
        print("Energy efficiency: \t{} imgs/J".format(1 / total_energy))

        scaled_util = [self.layerwise_MS_util[i]*self.total_fft_convs[i] / sum(self.total_fft_convs) for i in range(len(self.layerwise_MS_util))]
        print("Avg utilization: {}".format(sum(scaled_util)))
        print("TOPS/W: {}".format(sum(self.total_ops) * 1e-12 / total_energy))
        print(" --------------------- ")

        #total_energies = np.sum([self.photonic_energy, self.digital_energy, self.obj_energy, self.kern_energy], axis=0)
        #print(list(list(np.array(self.total_ops) * 1e-12) / total_energies))
        #print(list(list(np.array(self.total_ops) * 1e-12) / np.array(self.total_latency)))
        #accumulated = []
        #for i in range(len(self.total_latency)):
        #    accumulated.append(sum(self.total_latency[:i+1]))
        #print(accumulated)
        #times = [i*self.critical_path_latency for i in self.total_cycle]
        #for i in range(1,len(times)):
        #    times[i] += times[i-1]
        #print(times)
        #print(self.total_ops)
        
        print("--Critical paths--")
        print("Photonic: {}".format(self.photonic.t))
        print("Digital: {}".format(self.digital.latency))
        print("Kernel read: {}".format(self.kernel_buffer.latency*self.MS_pix/self.mem_access_width/self.banks))
        print("OBJ read: {}".format(self.object_buffer.latency*self.MS_pix/self.mem_access_width/self.banks))

        return self.total_cycle
        
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
                self.obj_reads += math.ceil(float(self.in_obj_size*self.channels_per_map) / self.mem_access_width)
                self.obj_inef.append(float(math.ceil(float(self.in_obj_size*self.channels_per_map) / self.mem_access_width)) / (float(self.in_obj_size*self.channels_per_map) / self.mem_access_width))
            return
        # 2
        elif self.state == 2:
            self.fft_convs += 2
            self.curr_in_channel += self.channels_per_map
            self.curr_out_channel = 0
            if self.read_ready:
                self.kern_reads += math.ceil(float(self.kernel_size*self.channels_per_map*self.filters_per_map)/self.mem_access_width)
                self.kern_inef.append(float(math.ceil(float(self.kernel_size*self.channels_per_map*self.filters_per_map)/self.mem_access_width)) / (float(self.kernel_size*self.channels_per_map*self.filters_per_map)/self.mem_access_width))
            return
        # 3
        elif self.state == 3:
            if self.read_ready:
                self.kern_reads += math.ceil(float(self.kernel_size*self.channels_per_map*self.filters_per_map)/self.mem_access_width)
                self.kern_inef.append(float(math.ceil(float(self.kernel_size*self.channels_per_map*self.filters_per_map)/self.mem_access_width)) / (float(self.kernel_size*self.channels_per_map*self.filters_per_map)/self.mem_access_width))
            return
        # 4
        elif self.state == 4:
            # 2 fft_convs to compensate for complex number computation
            self.cycle += 3
            self.fft_convs += 2
            #self.obj_writes += math.ceil(float(self.out_obj_size*self.filters_per_map) / self.mem_access_width)
            self.obj_writes += math.ceil(float(self.out_obj_size) / self.mem_access_width)
            self.obj_write_inef.append(float(math.ceil(float(self.out_obj_size*self.filters_per_map) / self.mem_access_width)) / (float(self.out_obj_size*self.filters_per_map) / self.mem_access_width))
            self.curr_out_channel += self.filters_per_map
            if self.read_ready and self.curr_out_channel < self.out_channels:
                self.kern_reads += math.ceil(float(self.kernel_size*self.channels_per_map*self.filters_per_map)/self.mem_access_width)
                self.kern_inef.append(float(math.ceil(float(self.kernel_size*self.channels_per_map*self.filters_per_map)/self.mem_access_width)) / (float(self.kernel_size*self.channels_per_map*self.filters_per_map)/self.mem_access_width))
            if self.read_ready and self.curr_out_channel >= self.out_channels:
                self.obj_reads += math.ceil(float(self.in_obj_size*self.channels_per_map) / self.mem_access_width)
                self.obj_inef.append(float(math.ceil(float(self.in_obj_size*self.channels_per_map) / self.mem_access_width)) / (float(self.in_obj_size*self.channels_per_map) / self.mem_access_width))
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

def read_config(path):
    """ input filter/IFM/OFM dimensions """
    
    layer_name = []
    in_obj_size = []
    out_obj_size = []
    in_channels = []
    out_channels = []
    kernel_size = []
    stride = []
    
    f = open(path, "r")
    next(f) # skip header line
    for line in f:
        line = line.strip()
        line = line.split(',')
        # We support only CONV-type laters. "WA" is 1x1 pointwise CONV
        if len(line) >= 7 and ("Conv" in line[0] or "WA" in line[0]):
            print(line)
            layer_name.append(line[0])
            kernel_height = int(line[3])
            kernel_width = int(line[4])
            kernel_size.append(kernel_height * kernel_width)
            # assuming padded inputs
            padding_height = (kernel_height // 2) * 2
            padding_width = (kernel_width // 2) * 2
            input_height = int(line[1])
            input_width = int(line[2])
            in_obj_size.append(input_height * input_width)
            s = int(line[7])
            out_obj_size.append(((input_height - padding_height)/s) * ((input_width - padding_width)/s))
            in_channels.append(int(line[5]))
            out_channels.append(int(line[6]))
            stride.append(int(line[7]))
        else:
            print("Skipping: {}".format(line[0]))
    f.close()
    
    return layer_name, in_obj_size, out_obj_size, in_channels, out_channels, kernel_size, stride
        
def main():
    
    acc = PhotonicAccelerator()

    # load CNN dimensions
    layer_name, in_obj_size, out_obj_size, in_channels, out_channels, kernel_size, stride = read_config("./model_cfgs/YOLOv3.csv")

    for layer_idx in range(len(layer_name)):
        print()
        print("Processing layer: {}".format(layer_name[layer_idx]))

        # configure accelerator with current layer dimensions
        acc.load_layer(in_obj_size[layer_idx], out_obj_size[layer_idx], in_channels[layer_idx], out_channels[layer_idx], kernel_size[layer_idx], stride[layer_idx])

        # update and apply FSM state until 'done' signal is reached
        acc.update_state(True)
        cycle = 0
        while not acc.done:
            acc.apply_latch()
            acc.update_state()
            cycle += 1
        print("Cycle count = {}".format(cycle))

    print()
    cycles = acc.summary()

    #print(layer_name)
    ## input object size
    #print([in_obj_size[i] * in_channels[i] for i in range(len(in_obj_size))])
    #print(out_channels)
    #print(cycles)
    
if __name__ == "__main__":
    main()
