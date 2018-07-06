"""
Function Generators
===================

.. module:: function_generators
   :platform: Windows, Linux, OSX
   :synopsis: Python wrappers for function generators

.. moduleauthor:: Jonathan Wheeler <jamwheel@stanford.edu>
.. moduleauthor:: Anjali Thontakudi

This module provides support for controlling function generators with Python.
Arbitrary waveform generators and function generators can be imported by

>>> import hardware
>>> awg = hardware.function_generators.Agilent_33250A('GPIB0:...')

"""

import visa
import numpy as np
import random
import logging

from hardware import u


class MockFunctionGenerator:

    def __init__(self, instr_name = None):
        if not instr_name:
            self.name = "AWG - Agilent_33250A"
        else:
            self.name = instr_name
        self._frequency = 3 * u.hertz
        self._voltage = 1 * u.volt
        self.waveforms = ['SIN', 'SQU', 'RAMP', 'PULS', 'NOIS', 'DC', 'USER']
        self._wf = self.waveforms[random.randint(0, len(self.waveforms))]
        self._phase = 20 * u.degree
        self._duty_cycle = 50  # as a percent
        self.logger = logging.getLogger(__name__)

    def identify(self):
        return self.name

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, val):
        self._frequency = val * u.hertz
        self.logger.info("Frequency set to %f Hz" % val)

    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, val):
        self._voltage = val * u.volt
        self.logger.info("Voltage set to %f V" % val)

    @property
    def waveform_name(self):
        return self._wf

    @property
    def phase(self):
        return self._phase

    @phase.setter
    def phase(self, val):
        self._phase = val * u.degree
        self.logger.info("Phase set to %f degrees" % val)

    @property
    def duty_cycle(self):
        return self._duty_cycle

    @duty_cycle.setter
    def duty_cycle(self, val):
        self._duty_cycle = val
        self.logger.info("Duty cycle set to %f percent" % val)


class FunctionGenerator:
    def __init__(self, visa_search_term):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)

    def identify(self):
        """
        Returns:
            str: the response from the ``*IDN?`` GPIB query.
        """
        return self.inst.query('*IDN?')[:-1]

    # properties are not polymorphic, so they must be redefined in subclasses
    # consider removing frequency/voltage property methods??
    # https://stackoverflow.com/questions/237432/python-properties-and-inheritance

    @property
    def frequency(self):
        f = self.inst.query('FREQ?')
        return float(f) * u.hertz

    # def get_frequency(self):
    #     f = self.inst.query('FREQ?')
    #     return float(f) * u.hertz

    @frequency.setter
    def frequency(self, val):
        self.inst.write("FREQ: %f" % val)
        if(hasattr(self, "logger")):
            self.logger.info("Frequency set to %f Hz" % val)

    @property
    def volt(self):
        return float(self.inst.query("VOLT?")) * u.volt

    @volt.setter
    def volt(self, val):
        self.inst.write('VOLT %i' % val)
        if(hasattr(self, "logger")):
            self.logger.info("Voltage set to %i V" % val)

# gathering up reused code in superclass and making these subclasses of that
# Link to manual: http://www.ece.mtu.edu/labs/EElabs/EE3306/Revisions_2008/agt33250aman.pdf
# Returning just a float vs. returning an actual pint.Quantity

class Agilent_33250A(FunctionGenerator):
    """
    Hardware wrapper for the Agilent 33250A Arbitrary Waveform Generator

    Parameters:
        visa_search_term (str): The address that is passed to
            ``visa.ResourceManager().open_resource()``

    Attributes:
        frequency (float): The frequency in Hz. Also aliases to ``freq``
        voltage (float): The peak-to-peak voltage in volts. Also aliases to
            `volt``
        waveform (str):  A string in the array
            ``['SIN', 'SQU', 'RAMP', 'PULS', 'NOIS', 'DC', 'USER' ]``
        phase (float): The relative phase to other instruments synced through
            the 10 MHz reference clock.
        duty_cycle (float): The duty cycle of the square wave form in percent.
    """

    def __init__(self, visa_search_term):
        super(Agilent_33250A, self).__init__(visa_search_term)
        self.logger = logging.getLogger(__name__ + ".Agilent_33250A")

    # must redefine properties in subclasses
    @property
    def frequency(self):
        f = self.inst.query('FREQ?')
        return float(f) * u.hertz

    @property
    def volt(self):
        return float(self.inst.query("VOLT?")) * u.volt

    @frequency.setter
    def frequency(self, val):

        # max and min values taken from user manual
        if val < 1 * u.microhertz:
            raise ValueError("Minimum frequency is 1µHz")
        elif((self.waveform == "SIN" or self.waveform == "SQU") and
             val > 80 * u.megahertz):
            raise ValueError("Max frequency is 80 MHz for %s waves" % self.waveform)
        elif(self.waveform == "PULS" and (val < 500 * u.microhertz
                                          or val > 50 * u.megahertz)):
            raise ValueError("Frequency must be between 500 µHz and 50 MHz for pulse waves")
        self.inst.write('FREQ %i' % val)
        self.logger.info("Frequency set to %i Hz" % val)

    # alias
    freq = frequency

    # alias
    voltage = volt

    @property
    def phase(self):
        unit = self.inst.query('UNIT:ANGL?')
        if("RAD" in unit):
            return float(self.inst.query('PHAS?')) * u.radian
        return float(self.inst.query('PHAS?')) * u.degree

    @phase.setter
    def phase(self, val):
        self.inst.write('PHAS %f' % val)
        unit = self.inst.query('UNIT:ANGL?')
        self.logger.info("Phase set to %f %s" % (val, unit))

    @property
    def duty_cycle(self):
        return float(self.inst.query('FUNCtion:SQUare:DCYCLe?'))

    @duty_cycle.setter
    def duty_cycle(self, val):
        self.inst.write('FUNCtion:SQUare:DCYCLe %f' % val)
        self.logger.info("Duty cycle set to %i percent" % val)

    @property
    def waveform(self):
        wf = self.inst.query('FUNC?')[:-1]
        if wf == 'USER':
            return 'USER ' + self.inst.query('FUNC:USER?')[:-1]
        return wf

    @waveform.setter
    def waveform(self, val):
        waveform_list = [
            'SIN', 'SQU', 'RAMP', 'PULS', 'NOIS', 'DC', 'USER'
        ]
        if val.upper() in (waveform_list):
            self.inst.write('FUNC %s' % val)
            self.logger.info("Waveform set to %s" % val)

        elif val.upper()[0:4] == 'USER':
            self.inst.write('FUNC:%s' % val)
            self.logger.info("Waveform set to %s" % val)

        else:
            raise Exception('%s is not a recognized waveform' % val)

    def upload(self, points_array):
        """
        Uploads an array of points to the function generator volatile memory.

        Parameters:
            points_array (array-like): The waveform shape
        """
        points_array = np.array(points_array)
        if points_array.dtype not in ['float64', 'int32']:
            raise Exception('Array is not numeric')
        if max(points_array) > 1 or min(points_array) < -1:
            raise Exception('Values should be floats between -1 and +1')
        values = ', '.join(map(str, points_array))
        self.inst.write('DATA VOLATILE, %s' % values)

    def save_as(self, waveform_name):
        """
        Saves the data in volatile memory as ``waveform_name``

        Parameters:
            waveform_name (str): The name of the saved waveform
        """
        self.inst.write('DATA:COPY %s' % waveform_name)
        self.logger.info("Data saved as %s" % waveform_name)

    def upload_as(self, points_array, waveform_name):
        """
        Uploads an array of points to the function generator, and
        saves them by name ``waveform_name``

        Parameters:
            points_array (array-like): The waveform shape
            waveform_name (str): The variable name to store in the waveform
                generator.
        """
        self.upload(points_array)
        self.save_as(waveform_name)

# link to user manual: http://www.thinksrs.com/downloads/pdfs/manuals/DS345m.pdf


class SRS_DS345(FunctionGenerator):
    """
    Hardware wrapper for the Stanford Research Systems DS345
    Arbitrary Waveform Generator

    Parameters:
        visa_search_term (str): The address that is passed to
            ``visa.ResourceManager().open_resource()``

    Attributes:
        frequency (float): The frequency in Hz. Also aliases to ``freq``
        voltage (float): The peak-to-peak voltage in volts. Also aliases to
        ``volt``
        waveform (str):  A string in the array
            ``['SIN', 'SQU', 'RAMP', 'PULS', 'NOIS', 'DC', 'USER' ]``

        phase (float): The relative phase to other instruments synced through
        the 10 MHz reference clock.
        duty_cycle (float): The duty cycle of the square wave form in percent.
    """
    def __init__(self, visa_search_term):
        super(SRS_DS345, self).__init__(visa_search_term)
        self.logger = logging.getLogger(__name__ + ".SRS DS345")

    @property
    def frequency(self):
        f = self.inst.query('FREQ?')
        return float(f) * u.hertz

    @frequency.setter
    def frequency(self, val):
        if(self.waveform == "NOIS"):
            raise ValueError("Frequency must remain at 10 MHz when waveform is 'NOISE'")
        elif(val < 1 * u.microhertz):
            raise ValueError("Minimum frequency is 1 µHz")
        elif((self.waveform == "SIN" or self.waveform == "SQ") and
             val > 30.2 * u.megahertz):
            raise ValueError("Maximum frequency is 30.2 MHz for %s waves" % self.waveform)
        elif(self.waveform == "RAMP" and val > 100 * u.kilohertz):
            raise ValueError("Maximum frequency is 100 KHz for ramp waves")
        self.inst.write('FREQ %i' % val)
        self.logger.info("Frequency set to %f Hz" % val)

    # alias
    freq = frequency

    @property
    def voltage(self):
        return float(self.inst.query('AMPL?')[:-3]) * u.volt

    @voltage.setter
    def voltage(self, val):
# list of the max and mins of all the voltages you can have based on the waves
# set boundaries on voltage inputs
#             Vpp        Vrms            dBm (50Ω)
# Function Max. Min.   Max.   Min.     Max.     Min.
# Sine     10V  10 mV  3.54V  3.54 mV  +23.98  -36.02
# Square   10V  10 mV  5V     5 mV     +26.99   -33.0
# Triangle 10V  10 mV  2.89V  2.89 mV  +22.22  -37.78
# Ramp    10V   10 mV  2.89V  2.89 mV  +22.22  -37.78
# Noise   10V   10 mV  2.09V  2.09 mV  +19.41 -40.59
# Arbitrary 10V 10 mV  n.a.  n.a.      n.a.   n.a.

        self.inst.write('AMPL %f' % val)
        self.logger.info("Voltage set to %i V" % val)

    # alias
    volt = voltage

    @property
    def phase(self):
        return float(self.inst.query('PHSE?')) * u.degree

    @phase.setter
    def phase(self, val):
        if(self.waveform == "NOIS"):
            raise Exception("Can't set phase when waveform is 'NOISE'")
        self.inst.write('PHSE %f' % val)
        self.logger.info("Phase set to %f" % val)


class HP_33120A(FunctionGenerator):
    """
    Hardware wrapper for the HP 33120A Arbitrary Waveform Generator

    Parameters:
        visa_search_term (str): The address that is passed to
            ``visa.ResourceManager().open_resource()``

    Attributes:
        frequency (float): The frequency in Hz. Also aliases to ``freq``
        voltage (float): The peak-to-peak voltage in volts. Also aliases to
            `volt``
        waveform (str):  A string in the array
            ``['SIN', 'SQU', 'RAMP', 'PULS', 'NOIS', 'DC', 'USER' ]``

        phase (float): The relative phase to other instruments synced through
            the 10 MHz reference clock.
        duty_cycle (float): The duty cycle of the square wave form in percent.
    """
    def __init__(self, visa_search_term):
        super(HP_33120A, self).__init__(visa_search_term)
        self.logger = logging.getLogger(__name__ + ".HP 33120A")

    @property
    def frequency(self):
        f = self.inst.query('FREQ?')
        return float(f) * u.hertz

    @property
    def volt(self):
        return float(self.inst.query("VOLT?")) * u.volt

    @frequency.setter
    def frequency(self, val):
        if(val < 100 * u.microhertz):
            raise ValueError("Minimum frequency is 100 µHz")
        elif((self.waveform == "SIN" or self.waveform == "SQU")
                and val > 15 * u.megahertz):
            raise ValueError("Maximum frequency is 15 MHz for %s waves" % self.waveform)
        elif(self.waveform == "RAMP" and val > 100 * u.kilohertz):
            raise ValueError("Maximum frequency is 100 KHz for ramp waves")

        self.inst.write('FREQ %i' % val)
        self.logger.info("Frequency set to %f Hz" % val)

    # alias
    freq = frequency
    # alias
    voltage = volt

    @property
    def phase(self):
        return float(self.inst.query('PHAS?')) * u.degree

    @phase.setter
    def phase(self, val):
        self.inst.write('PHAS %f' % val)
        self.logger.info("Phase set to %f" % val)

    @property
    def duty_cycle(self):
        return float(self.inst.query('FUNCtion:SQUare:DCYCLe?'))

    @duty_cycle.setter
    def duty_cycle(self, val):
        self.inst.write('FUNCtion:SQUare:DCYCLe %f' % val)
        self.logger.info("Duty cycle set to %f percent" % val)

    @property
    def waveform(self):
        wf = self.inst.query('FUNC?')[:-1]
        if wf == 'USER':
            return 'USER ' + self.inst.query('FUNC:USER?')[:-1]
        return wf

    @waveform.setter
    def waveform(self, val):
        waveform_list = [
            'SIN', 'SQU', 'RAMP', 'PULS', 'NOIS', 'DC', 'USER'
        ]
        if val.upper() in (waveform_list):
            self.logger.info("Waveform set to %s" % val)

            return self.inst.write('FUNC %s' % val)

        elif val.upper()[0:4] == 'USER':
            self.logger.info("Waveform set to %s" % val)

            return self.inst.write('FUNC:%s' % val)

        else:
            raise Exception('%s is not a recognized waveform' % val)

    def upload(self, points_array):
        """
        Uploads an array of points to the function generator volatile memory.

        Parameters:
            points_array (array-like): The waveform shape
        """
        points_array = np.array(points_array)
        if points_array.dtype not in ['float64', 'int32']:
            raise Exception('Array is not numeric')
        if max(points_array) > 1 or min(points_array) < -1:
            raise Exception('Values should be floats between -1 and +1')
        values = ', '.join(map(str, points_array))
        self.inst.write('DATA VOLATILE, %s' % values)

    def save_as(self, waveform_name):
        """
        Saves the data in volatile memory as ``waveform_name``

        Parameters:
            waveform_name (str): The name of the saved waveform
        """
        self.inst.write('DATA:COPY %s' % waveform_name)
        self.logger.info("Waveform saved %s" % waveform_name)

    def upload_as(self, points_array, waveform_name):
        """
        Uploads an array of points to the function generator, and
        saves them by name ``waveform_name``

        Parameters:
            points_array (array-like): The waveform shape
            waveform_name (str): The variable name to store in the waveform
                generator.
        """
        self.upload(points_array)
        self.save_as(waveform_name)
