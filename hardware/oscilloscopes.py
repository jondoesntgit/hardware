# coding: utf-8
"""
Oscilloscopes
=============

.. module:: oscilloscopes
   :platform: Windows, Linux, OSX
   :synopsis: Python wrappers for oscilloscopes

.. moduleauthor:: Jonathan Wheeler <jamwheel@stanford.edu>
.. moduleauthor:: Anjali Thontakudi

This module provides support for controlling oscilloscopes with Python.
Oscilloscopes can be imported by

>>> import hardware
>>> osc = hardware.function_generators.Agilent_DSO1024A('USB:...')

"""

import visa
from numpy import array, arange
import time
from hardware import u

class MockOscilloscope:
    def __init__(self, instr_name = None):
        if not instr_name:
            self.name = "Oscilloscope - Agilent DSO1024A "
        else:
            self.name = instr_name

    def identify(self):
        return self.name

    def set_timeout(self, val):
        self.timeout = val * u.milliseconds

    def stop(self):
        print("Stopped")

    def start(self):
        print("Started")

    def run(self):
        print("Running")

class Agilent_DSO1024A:
    """
    Hardware wrapper for Agilent DSO1024A digital oscilloscopes.

    Parameters:
        visa_search_term (str): The address that is passed to
            ``visa.ResourceManager().open_resource()``
    """
    def __init__(self, visa_search_term):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)

    def identify(self):
        """
        Returns:
            str: The response of a ``*IDN?`` GPIB query
        """
        return self.inst.query('*IDN?')

    def set_timeout(self, milliseconds):
        """
        Sets the instrument timeout in milliseconds

        Args:
            milliseconds (float): The amount of time to wait before timing out
        """
        self.inst.timeout = milliseconds

    def single(self):
        """
        Simulates pressing the `Single` button on the front panel.
        """
        self.inst.write(':SINGLE')

    def run(self):
        """
        Simulates pressing the `Run` button on the front panel
        """
        self.inst.write(':RUN')

    def stop(self):
        """
        Simulates pressing the `Stop` button on the front panel
        """
        self.inst.write(':STOP')

    def acquire(self, channel=1):
        """
        Retrieves a time trace from a single acquisition.

        Args:
            channel (int, optional): The channel to be read

        Returns:
            tuple of arrays: The first array contains the times in nanoseconds,
            and the second contains voltages in volts.
        """
        self.inst.write('ACQuire:TYPE NORMAL')
        self.inst.write('SINGLE')
        self.inst.write('WAVeform:SOURce CHAN%i' % channel)
        self.inst.write('WAVeform:FORMat ASCII')
        time.sleep(2)

        # yref = float(self.inst.query('WAVeform:YREF?'))
        # yinc = float(self.inst.query('WAVeform:YINC?'))
        # yor = float(self.inst.query('WAVeform:YOR?'))

        xinc = float(self.inst.query('WAV:XINC?'))
        xor = float(self.inst.query('WAV:XOR?'))

        data = self.inst.query('WAVeform:DATA?')
        #  data_values = array([int.from_bytes(val.encode(), 'big')
        #   for val in data[12:]])
        data_values = array(data[12:].split(',')).astype(float)
        self.inst.write('RUN')

        y = data_values  # (yref + data_values) * yinc - yor
        x = xor + (arange(len(y)) * xinc)

        return x, y
