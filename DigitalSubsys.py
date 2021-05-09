"""
File:     DigitalSubsys.py
Author:   Edward Hanson (edward.t.hanson@duke.edu)
Desc:     Activation, normalization, pooling, control, and peripheral circuits
"""

import configparser as cp

class DigitalSubsys:

    def __init__(self, config_path, MS_dim=1e3, DAC_group_size=1, ADC_group_size=1):
        """
        MS_dim         - metasurface input length (i.e., one side of the MS square)
        DAC_group_size - number of MS rows/columns shared by one DAC
        ADC_group_size - number of MS rows/columns shared by one ADC
        """

        self.config = cp.ConfigParser()
        self.config.read(config_path)
        
        self.MS_dim = MS_dim

        # Stats of one DAC
        self.DAC_latency = float(self.config.get("digital", "DAC_latency"))
        self.DAC_avgPower = float(self.config.get("digital", "DAC_avgPower"))
        self.DAC_area = float(self.config.get("digital", "DAC_area"))
        # Stats of one ADC
        self.ADC_latency = float(self.config.get("digital", "ADC_latency"))
        self.ADC_avgPower = float(self.config.get("digital", "ADC_avgPower"))
        self.ADC_area = float(self.config.get("digital", "ADC_area"))

        # Stats of DAC row
        self.DACrow_latency = self.DAC_latency * MS_dim * DAC_group_size
        self.DACrow_avgPower = self.DAC_avgPower * (MS_dim / DAC_group_size)
        self.DACrow_area = self.DAC_area * (MS_dim / DAC_group_size)
        # Stats of one ADC row
        self.ADCrow_latency = self.ADC_latency * MS_dim * ADC_group_size
        self.ADCrow_avgPower = self.ADC_avgPower * (MS_dim / ADC_group_size)
        self.ADCrow_area = self.ADC_area * (MS_dim / ADC_group_size)
        # Stats of total bit-line selector
        self.bls_latency = float(self.config.get("digital", "bls_latency"))
        self.bls_avgPower = float(self.config.get("digital", "bls_avgPower"))
        self.bls_area = float(self.config.get("digital", "bls_area"))
        # Stats of normalization, maxpool, and activation module
        self.nonlinear_latency = float(self.config.get("digital", "nonlin_latency"))
        self.nonlinear_avgPower = float(self.config.get("digital", "nonlin_avgPower"))
        self.nonlinear_area = float(self.config.get("digital", "nonlin_area"))
        # Stats of global control circuitry
        self.control_latency = float(self.config.get("digital", "control_latency"))
        self.control_avgPower = float(self.config.get("digital", "control_avgPower"))
        self.control_area = float(self.config.get("digital", "control_area"))

        # -------- Summary of DiginalSubsys ------------ #
        self.latency = max([self.DACrow_latency + 2*self.ADCrow_latency, self.bls_latency, self.nonlinear_latency, self.control_latency])
        self.avgPower = self.DACrow_avgPower + self.ADCrow_avgPower + self.bls_avgPower + self.nonlinear_avgPower + self.control_avgPower
        self.area = self.DACrow_area + self.ADCrow_area + self.bls_area + self.nonlinear_area + self.control_area

    def update_state(self):
        """
        Do nothing here
        """
        return

    def apply_latency(self):
        """
        Simply return the latency
        """
        return self.latency
