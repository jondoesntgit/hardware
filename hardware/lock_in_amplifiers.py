# coding: utf-8
"""
Lock-in Amplifiers
==================

.. module::  lock_in_amplifiers
   :platform: Windows, Linux, OSX
   :synopsis: Python wrappers for lock-in amplifiers

.. moduleauthor:: Jonathan Wheeler <jamwheel@stanford.edu>
.. moduleauthor:: Anjali Thontakudi

This module provides support for controlling lock-in amplifiers with Python.
Lock-in amplifiers can be imported by

>>> import hardware
>>> lia = hardware.function_generators.SRS_SR844('GPIB0:...')

"""

import visa
from hardware import u
import random
import logging

class MockLockInAmplifier:
    """
    This class serves as a dummy lock in amplifier, used for testing.

    Parameters
    ----------------------------------------
        instr_name (str, optional): The name for the amplifier

    Attributes
    ----------------------------------------
        _sensitivity_dict (dict): A shortened dictionary of the sensitivities
                                  the amplifier can be set to
        _time_constant_list (list): A shortened lit of possible time constants
        name (str): The name of the amplifier
        logger (logging): A reference to a logger that prints information
                         statements when a value (i.e. phase) is set
    """

    def __init__(self, instr_name = None):
        if not instr_name:
            self.name = "Lock In Amplifier - SRS_SR844"
        else:
            self.name = instr_name

        self._sensitivity_dict = {
                0: {"Vrms": 100e-9, "dBm": -127},
                1: {"Vrms": 300e-9, "dBm": -117},
                2: {"Vrms": 1e-6, "dBm": -107},
                3: {"Vrms": 3e-6, "dBm": -97},
                4: {"Vrms": 10e-6, "dBm": -87},
                5: {"Vrms": 30e-6, "dBm": -77},
            }

    # see page 115 of manual
        self._time_constant_list = [  # query by index
                100e-6,
                300e-6,
                1e-3,
                3e-3,
                10e-3,
            ]

        self.logger = logging.getLogger(__name__)

        key = random.randint(0, len(self._time_constant_list))
        self._time_constant = self._time_constant_list[key] * u.second
        self._phase = random.randint(1, 361) * u.degree

        key2 = random.randint(0, len(self._sensitivity_dict))
        self._sensitivity = self._sensitivity_dict[key2] * u.volt

    def identify(self):
        return self.name

    @property
    def phase(self):
        return self._phase

    @property
    def time_constant(self):
        return self._time_constant

    @property
    def sensitivity(self):
        self._sensitivity


class SRS_SR844:
    """
    Hardware wrapper for Stanford Research Systems SR844 Lock-in Amplifier

    Parameters:
        visa_search_term (str): The address that is passed to
            ``visa.ResourceManager().open_resource()``

    Attributes:
        phase (float): The phase between the input and the reference signals in
            degrees.
        sensitivity (float): The sensitivity of the lock-in amplifer in volts.
        time_constant (float): The time constant for the lock-in amplifier
            filter.
    """
    def __init__(self, visa_search_term):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)

        self._sensitivity_dict = {
            0: {"Vrms": 100e-9, "dBm": -127},
            1: {"Vrms": 300e-9, "dBm": -117},
            2: {"Vrms": 1e-6, "dBm": -107},
            3: {"Vrms": 3e-6, "dBm": -97},
            4: {"Vrms": 10e-6, "dBm": -87},
            5: {"Vrms": 30e-6, "dBm": -77},
            6: {"Vrms": 100e-6, "dBm": -67},
            7: {"Vrms": 300e-6, "dBm": -57},
            8: {"Vrms": 1e-3, "dBm": -47},
            9: {"Vrms": 3e-3, "dBm": -37},
            10: {"Vrms": 10e-3, "dBm": -27},
            11: {"Vrms": 30e-3, "dBm": -17},
            12: {"Vrms": 100e-3, "dBm": -7},
            13: {"Vrms": 300e-3, "dBm": 3},
            14: {"Vrms": 1, "dBm": 13},
        }

        # see page 115 of manual
        self._time_constant_list = [  # query by index
            100e-6,
            300e-6,
            1e-3,
            3e-3,
            10e-3,
            30e-3,
            100e-3,
            300e-3,
            1,
            3,
            10,
            30,
            100,
            300,
            1e3,
            3e3,
            10e3,
            30e3
        ]

        # see page 134 of SR844 manual
        self._status_dictionary = {
            0: {"name": "ULK", "set_when": "A reference unlock is detected"},
            1: {"name": "FRQ",
                "set_when": "The reference frequency is out of range"},
            2: {"name": "-", "set_when": "Unused"},
            3: {"name": "TRG", "set_when": "Data storage is triggered"},
            4: {"name": "INP", "set_when": "The signal input overloads"},
            5: {"name": "RSV", "set_when": "The IF amplifier overloads"},
            6: {"name": "FLT", "set_when": "A time constant filter overloads"},
            7: {"name": "CHG",
                "set_when": "Reference frequency changed by more than 1%"},
            8: {"name": "CH1", "set_when":
                "Channel 1 display or output overloads"},
            9: {"name": "CH2", "set_when":
                "Channel 2 display or output overloads"},
            10: {"name": "OAX", "set_when": "Either Aux input overloads"},
            11: {"name": "UAX", "set_when": "Ratio input underflows"},
            12: {"name": "-", "set_when": "Unused"},
            13: {"name": "-", "set_when": "Unused"},
            14: {"name": "-", "set_when": "Unused"},
            15: {"name": "-", "set_when": "Unused"},
        }
        self.logger = logging.getLogger(__name__ + ".SRS SR844")

    def identify(self):
        """
        Returns:
            str: The response from an ``*IDN?`` GPIB query.
        """
        return self.inst.query('*IDN?')[:-1]

    @property
    def phase(self):
        return float(self.inst.query('PHAS?')[:-1]) * u.degree

    @phase.setter
    @u.wraps(None, (None, u.degree))
    def phase(self, val):
        if(val > 180 or val < -180):
            raise ValueError("Phase must be between -180 and 180 degrees")
        self.inst.write('PHAS %f' % val)
        self.logger.info("Phase set to %f degrees." % val)

    @property
    def sensitivity(self):
        key = int(self.inst.query('SENS?'))
        return self._sensitivity_dict[key]['Vrms'] * u.volt

    @sensitivity.setter
    @u.wraps(None, (None, u.volt))
    def sensitivity(self, val):
        key = [d['Vrms'] for d in self._sensitivity_dict.values()].index(val)
        # create array of Vrms values from dictionary by iterating through values
        # from the values we are only looking at those w [Vrms] key
        # if find the Vrms key index, that index is the sensitivity
        if key not in self._sensitivity_dict:
            raise ValueError("Not a valid sensitivity")
        self.inst.write('SENS %i' % key)
        self.logger.info("Sensitivity set to %f V." % val)
        # raise Exception if value isn't in the array (Value Error)

    @property
    def time_constant(self):
        key = int(self.inst.query('OFLT?'))
        return self._time_constant_list[key] * u.second

    @time_constant.setter
    @u.wraps(None, (None, u.second))
    def time_constant(self, val):
        if val not in self._time_constant_list:
            raise ValueError("Not a valid time constant")
        key = self._time_constant_list.index(val)
        self.inst.write('OFLT %i' % key)
        self.logger.info("Time constant set to %f seconds." % val)

    @property
    def x(self):
        return float(self.inst.query('OUTP? 1'))

    @property
    def y(self):
        return float(self.inst.query('OUTP? 2'))

    @property
    def x_offset(self):
        return float(self.inst.query('DOFF? 1,0'))

    @x_offset.setter
    def x_offset(self, val):
        if val > 110 or val < -110:
            raise ValueError('Offset must be between -110% and 110%')
        self.inst.write('DOFF 1,0,%.2f' % val)

    @property
    def y_offset(self):
        return float(self.inst.query('DOFF? 2,0'))

    @y_offset.setter
    def y_offset(self, val):
        if val > 100 or val < -110:
            raise ValueError('Offset must be between -110% and 110%')
        self.inst.write('DOFF 2,0,%2.f' % val)

    def autophase(self):
        """
        Sends the ``APHS`` command to the lock-in over the GPIB bus. This
        performs the Auto Phase function. This command is the same as pressing
        Shift−Phase on the lock-in amplifier front panel. This command adjusts
        the reference phase so that the current measurement has a Y value of
        zero and an X value equal to the signal magnitude, R.
        """
        self.inst.write('APHS')

    def autogain(self):
        """
        Performs the built-in ``AGAN`` function in order to auto-gain the
        lock-in amplifier.
        """
        self.inst.write('AGAN')
        _old_timeout = self.inst.timeout
        self.inst.timeout = 15e3
        while int(self.inst.query('*STB?1')[:-1]):
            # Do nothing until the status bit is clear
            pass
        self.inst.timeout = _old_timeout

    def get_status(self, status=None, verbose=False):
        """
        Gets the status bits using the ``LIAS?`` GPIB query. Optionally, status
        bits can be provided and interpreted.

        Args:
            status (str, optional): Status bits to decode. If not supplied,
                the status bits will be read from the lock-in amplifier.
            verbose (bool): Explains the status bits if `True`

        Returns:
            str: Status bits in binary form.
        """
        if status is None:
            status = int(self.inst.query('LIAS?')[:-1])
        else:
            verbose = True
        status_bits = format(status, '016b')

        if not verbose:
            return status_bits

        for idx in range(len(status_bits)):
            if status_bits[idx] == '0':
                continue
            print("{name}:\t{set_when}".format(**self._status_dictionary[idx]))

        return status_bits
