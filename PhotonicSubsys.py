"""
File:     PhotonicSubsys.py
Author:   Edward Hanson (edward.t.hanson@duke.edu)

"""

import numpy as np

class PhotonicSubsys:

    def __init__(self, MS_pix=1e6, Nb=8):
        """
        MS_pix      - total number of pixels for a metasurface
        Nb          - precision of each pixel
        """
        
        self.MS_pix = MS_pix
        self.Nb = Nb
        # wavelength of light
        self.lmbda = 905e-9
        # Plank's constant
        self.hbar = 1.05e-34
        # speed of light
        self.c = 2.998e8
        # angular frequency
        self.omega = 2*np.pi*self.c/self.lmbda
        # number of photons (per pixel) required to achieve N_b precision given SNR from shot noise is sqrt(np)
        self.np = (2/3)*2**(2*self.Nb)

        # Total optical energy required to make the measurement
        self.E = self.hbar*self.omega*self.np*self.MS_pix
        # Time to take measurement (determined by LC switching speed)
        self.t = 1e-6
        # Optical power
        self.P = self.E / self.t

    def update_state(self):
        """
        Nothing to do here yet
        IDEA: can we save power by reducing the number of active pixels per run?
        """
        return

    def apply_latch(self):
        """
        Simply return the energy and latency
        """
        return self.t, self.E