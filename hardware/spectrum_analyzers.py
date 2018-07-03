# coding: utf-8
"""
Spectrum Analyzers
===================

.. module::  spectrum_analyzers
   :platform: Windows, Linux, OSX
   :synopsis: Python wrappers for lock-in amplifiers

.. moduleauthor:: Jonathan Wheeler <jamwheel@stanford.edu>

This module provides support for controlling spectrum analyzers with Python.
Spectrum analyzers can be imported by

>>> import hardware
>>> lia = hardware.spectrum_analyzers.ANDO_AQ6317B('GPIB0:...')

"""

import visa
import numpy as np
import pint


class ANDO_AQ6317B:
    """
    Hardware wrapper for ANDO AQ6317B Optical Spectrum Analyzer

    Parameters:
        visa_search_term (str): The address that is passed to
            ``visa.ResourceManager().open_resource()``
    """
    def __init__(self, visa_search_term):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)
        self.ureg = pint.UnitRegistry()

    def identify(self):
        """
        Returns:
            str: The response from an ``*IDN?`` GPIB query.
        """
        return self.inst.query('*IDN?')

    def set_timeout(self, milliseconds):
        """
        Sets the timeout of the instrument in milliseconds.

        Args:
            milliseconds(float): The timeout in milliseconds
        """
        self.inst.timeout = milliseconds

    def get_spectrum(self):
        """
        Returns the measured spectrum from a single reading of the instrument.
        Aliases to acquire

        Returns:
            tuple of arrays:
                The first array contains the wavelengths in nanometers.
                The second array contains the optical power in dBm.
        """
        power_string = self.inst.query('LDATB')
        power = np.array(power_string[:-2].split(','))
        power = power.astype(np.float)[2:]

        wavelength_string = self.inst.query('WDATB')
        wavelength = np.array(wavelength_string[:-2].split(','))
        wavelength = wavelength.astype(np.float)[2:]

        return wavelength * ureg.nanometer, power * ureg.watt
        #power can be dBm

    # Alias
    acquire = get_spectrum


class Rohde_Schwarz_FSEA_20:
    """
    Hardware wrapper for Rohde & Schwarz FSEA 20 RF Spectrum Analyzer

    Parameters:
        visa_search_term (str): The address that is passed to
            ``visa.ResourceManager().open_resource()``
    """
    def __init__(self, visa_search_term):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)
        self.ureg = pint.UnitRegistry()

    @property
    def center(self):
        float(self.inst.query('FREQ:CENT?')) * self.ureg.hertz

    @center.setter
    def center(self, Hz):
        self.inst.write('FREQ:CENT %s' % Hz)

    @property
    def span(self):
        return float(self.inst.query('FREQ:SPAN?')) *self.ureg.hertz

    @span.setter
    def span(self, Hz):
        self.inst.write('FREQ:SPAN %s' % Hz)

    @property
    def reference(self):
        return float(self.inst.query('DISPLAY:TRACE:Y:RLEVEL?'))

    @reference.setter
    def reference(self, power):
        self.inst.write("DISPLAY:TRACE:Y:RLEVEL %s" % power)

    @property
    def start(self):
        return float(self.inst.query('FREQ:STAR?')) *self.ureg.hertz

    @start.setter
    def start(self, Hz):
        self.inst.write('FREQ:STAR %s' % Hz)

    @property
    def stop(self):
        return float(self.inst.query('FREQ:STOP?')) * self.ureg.hertz

    @stop.setter
    def stop(self, Hz):
        self.inst.write('FREQ:STOP %s' % Hz)

    @property
    def time(self):
        return float(self.inst.query('SWEEP:TIME?')) * self.ureg.second

    @time.setter
    def time(self, seconds):
        self.inst.write('SWEEP:TIME %fs' % seconds)

    @property
    def vbw(self):
        return float(self.inst.query('BAND:VID?'))

    @vbw.setter
    def vbw(self, Hz):
        self.inst.write('BAND:VID %s' % Hz)

    @property
    def rbw(self):
        return float(self.inst.query('BAND?'))

    @rbw.setter
    def rbw(self, Hz):
        self.inst.write('BAND %s' % Hz)

    @property
    def averages(self):
        return float(self.inst.query('AVER:COUNT?'))

    @averages.setter
    def averages(self, count):
        self.inst.write('AVER:COUNT %i' % count)

    """High level commands..."""
    def acquire(self):
        """Returns a tuple of the frequencies (Hz) and powers of the trace.
        For the resolution bandwidth, use the ``rbw`` property.
        """
        powers = [float(p) for p in self.inst.query('TRAC? TRACE1').split(',')]
        freqs = np.linspace(self.start, self.stop, len(powers))

        return freqs, powers
