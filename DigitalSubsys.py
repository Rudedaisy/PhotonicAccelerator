"""
File:     DigitalSubsys.py
Author:   Edward Hanson (edward.t.hanson@duke.edu)
Desc:     Activation, normalization, pooling, control, and peripheral circuits
"""

class DigitalSubsys:

    def __init__(self, MS_dim=1e3, DAC_group_size=1, ADC_group_size=1):
        """
        MS_dim         - metasurface input length (i.e., one side of the MS square)
        DAC_group_size - number of MS rows/columns shared by one DAC
        ADC_group_size - number of MS rows/columns shared by one ADC
        """

        self.MS_dim = MS_dim

        # Stats of one DAC
        self.DAC_latency = 1e-9
        self.DAC_avgPower = 1e-3
        self.DAC_area = 0 ##
        # Stats of one ADC
        self.ADC_latency = 1e-9
        self.ADC_avgPower = 1e-3
        self.ADC_area = 0 ##

        # Stats of DAC row - NEED CHECK
        self.DACrow_latency = self.DAC_latency * MS_dim * DAC_group_size
        self.DACrow_avgPower = self.DAC_avgPower * (MS_dim / DAC_group_size)
        self.DACrow_area = self.DAC_area * (MS_dim / DAC_group_size)
        # Stats of one ADC row - NEED CHECK
        self.ADCrow_latency = self.ADC_latency * MS_dim * ADC_group_size
        self.ADCrow_avgPower = self.ADC_avgPower * (MS_dim / ADC_group_size)
        self.ADCrow_area = self.ADC_area * (MS_dim / ADC_group_size)
        # Stats of total bit-line selector
        self.bls_latency = 1e-9
        self.bls_avgPower = 1e-3
        self.bls_area = 20502 # nm^2
        # Stats of normalization, maxpool, and activation module
        self.nonlinear_latency = 0 ##
        self.nonlinear_avgPower = 0 ##
        self.nonlinear_area = 0 ##
        # Stats of global control circuitry
        self.control_latency = 0 ##
        self.control_avgPower = 0
        self.control_area = 0

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
