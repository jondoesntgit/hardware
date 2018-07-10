# coding: utf-8
"""
Spectrum Analyzers
===================

.. module::  spectrum_analyzers
   :platform: Windows, Linux, OSX
   :synopsis: Python wrappers for lock-in amplifiers

.. moduleauthor:: Jonathan Wheeler <jamwheel@stanford.edu>
.. moduleauthor:: Anjali Thontakudi

This module provides support for controlling spectrum analyzers with Python.
Spectrum analyzers can be imported by

>>> import hardware
>>> lia = hardware.spectrum_analyzers.ANDO_AQ6317B('GPIB0:.. .')

"""

import visa
import numpy as np
from hardware import u
import logging
from hardware import u


class MockSpectrumAnalyzer:
    def __init__(self, instr_name = None):
        if not instr_name:
            self.name = "Spectrum Analyzer - Rohde Schwarz FSEA 20"
        else:
            self.name = instr_name
        self._start = 50 * u.hertz
        self._stop = 100 * u.hertz
        self._center = 75 * u.hertz
        self._span = 50 * u.hertz
        self._sweep_time = 20 * u.second
        self._reference = 5 * u.watt
        self._bandwidth = 2 * u.hertz

        self.logger = logging.getLogger(__name__)

    def identify(self):
        return self.name

    @property
    def start(self):
        return self._start

    @start.setter
    @u.wraps(None, (None, u.hertz))
    def start(self, val):
        self._start = val
        self.logger.info("Start frequency set to %f Hz" % val.to(u.hertz).magnitude)

    @property
    def stop(self):
        return self._stop

    @stop.setter
    @u.wraps(None, (None, u.hertz))
    def stop(self, val):
        self._stop = val
        self.logger.info("Stop frequency set to %f Hz" % val.to(u.hertz).magnitude)

    @property
    def center(self):
        return self._center

    @center.setter
    @u.wraps(None, (None, u.hertz))
    def center(self, val):
        self._center = val
        self.logger.info("Center frequency set to %f Hz" % val.to(u.hertz).magnitude)

    @property
    def span(self):
        return self._span

    @span.setter
    @u.wraps(None, (None, u.hertz))
    def span(self, val):
        self._span = val
        self.logger.info("Span set to %f Hz" % val.to(u.hertz).magnitude)

    @property
    def sweep_time(self):
        return self._sweep_time

    @sweep_time.setter
    @u.wraps(None, (None, u.second))
    def sweep_time(self, val):
        self._sweep_time = val
        self.logger.info("Sweep time set to %f seconds" % val.to(u.second).magnitude)

    @property
    def reference(self):
        return self._reference

    @reference.setter
    @u.wraps(None, (None, u.milliwatt))
    def reference(self, val):
        self._reference = val
        self.logger.info("Reference set to %f watts" % val.to(u.watt).magnitude)

    @property
    def bandwidth(self):
        return self._bandwidth

    @bandwidth.setter
    @u.wraps(None, (None, u.hertz))
    def bandwidth(self, val):
        self._bandwidth = val
        self.logger.info("Bandwidth set to %f Hz" % val.to(u.hertz).magnitude)


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
        self.logger = logging.getLogger(__name__ + ".ANDO AQ6317B")

    def identify(self):
        """
        Returns:
            str: The response from an ``*IDN?`` GPIB query.
        """
        return self.inst.query('*IDN?')

    @u.wraps(None, (None, u.milliseconds))
    def set_timeout(self, milliseconds):
        """
        Sets the timeout of the instrument in milliseconds.

        Args:
            milliseconds(float): The timeout in milliseconds
        """
        self.inst.timeout = milliseconds.to(u.milliseconds).magnitude
        self.logger.info("Timeout set to %f milliseconds"
                         % milliseconds.to(u.milliseconds).magnitude)

    def get_spectrum(self, channel='B'):
        """
        Returns the measured spectrum from a single reading of the instrument.
        Aliases to acquire

        Returns:
            tuple of arrays:
                The first array contains the wavelengths in nanometers.
                The second array contains the optical power in dBm.
        """
        power_string = self.inst.query('LDAT%s' % channel)
        power = np.array(power_string[:-2].split(','))
        power = power.astype(np.float)[2:]

        wavelength_string = self.inst.query('WDAT%s' % channel)
        wavelength = np.array(wavelength_string[:-2].split(','))
        wavelength = wavelength.astype(np.float)[2:]

        return wavelength * u.nanometer, power * u.watt
        # power can be dBm

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
        self.logger = logging.getLogger(__name__ + ".Rhode Schwarz FSEA20")

    @property
    def center(self):
        float(self.inst.query('FREQ:CENT?')) * u.hertz

    @center.setter
    @u.wraps(None, (None, u.hertz))
    def center(self, Hz):
        self.inst.write('FREQ:CENT %s' % Hz.to(u.hertz).magnitude)
        self.logger.info("Center set to %s Hz" % Hz.to(u.hertz).magnitude)

    @property
    def span(self):
        return float(self.inst.query('FREQ:SPAN?')) * u.hertz

    @span.setter
    @u.wraps(None, (None, u.hertz))
    def span(self, Hz):
        self.inst.write('FREQ:SPAN %s' % Hz.to(u.hertz).magnitude)
        self.logger.info("Span set to %s Hz" % Hz.to(u.hertz).magnitude)

    @property
    def reference(self):
        return float(self.inst.query('DISPLAY:TRACE:Y:RLEVEL?')) * u.watt

    @reference.setter
    def reference(self, power):
        self.inst.write("DISPLAY:TRACE:Y:RLEVEL %s" % power)
        self.logger.info("Reference set to %s watt" % power)

    @property
    def start(self):
        return float(self.inst.query('FREQ:STAR?')) * u.hertz

    @start.setter
    @u.wraps(None, (None, u.hertz))
    def start(self, Hz):
        self.inst.write('FREQ:STAR %s' % Hz.to(u.hertz).magnitude)
        self.logger.info("Start set to %s Hz" % Hz.to(u.hertz).magnitude)

    @property
    def stop(self):
        return float(self.inst.query('FREQ:STOP?')) * u.hertz

    @stop.setter
    @u.wraps(None, (None, u.hertz))
    def stop(self, Hz):
        self.inst.write('FREQ:STOP %s' % Hz.to(u.hertz).magnitude)
        self.logger.info("Stop set to %s Hz" % Hz.to(u.hertz).magnitude)

    @property
    def time(self):
        return float(self.inst.query('SWEEP:TIME?')) * u.second

    @time.setter
    @u.wraps(None, (None, u.second))
    def time(self, seconds):
        self.inst.write('SWEEP:TIME %fs' % seconds.to(u.second).magnitude)
        self.logger.info("Sweep time set to %f seconds" % seconds.to(u.second).magnitude)

    @property
    def vbw(self):
        return float(self.inst.query('BAND:VID?')) * u.hertz

    @vbw.setter
    @u.wraps(None, (None, u.hertz))
    def vbw(self, Hz):
        self.inst.write('BAND:VID %s' % Hz.to(u.hertz).magnitude)
        self.logger.info("VBW set to %s Hz" % Hz.to(u.hertz).magnitude)

    @property
    def rbw(self):
        return float(self.inst.query('BAND?')) * u.hertz

    @rbw.setter
    @u.wraps(None, (None, u.hertz))
    def rbw(self, Hz):
        self.inst.write('BAND %s' % Hz.to(u.hertz).magnitude)
        self.logger.info("RBW set to %s Hz" % Hz.to(u.hertz).magnitude)

    @property
    def averages(self):
        return float(self.inst.query('AVER:COUNT?'))

    @averages.setter
    def averages(self, count):
        self.inst.write('AVER:COUNT %i' % count)
        self.logger.info("Average set to %i" % count)

    """High level commands..."""
    def acquire(self):
        """Returns a tuple of the frequencies (Hz) and powers of the trace.
        For the resolution bandwidth, use the ``rbw`` property.
        """
        powers = [float(p) for p in self.inst.query('TRAC? TRACE1').split(',')]
        freqs = np.linspace(self.start, self.stop, len(powers))

        return freqs, powers
