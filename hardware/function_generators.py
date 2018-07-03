"""
Function Generators
===================

.. module:: function_generators
   :platform: Windows, Linux, OSX
   :synopsis: Python wrappers for function generators

.. moduleauthor:: Jonathan Wheeler <jamwheel@stanford.edu>

This module provides support for controlling function generators with Python.
Arbitrary waveform generators and function generators can be imported by

>>> import hardware
>>> awg = hardware.function_generators.Agilent_33250A('GPIB0:...')

"""

import visa
import numpy as np
import from pint import UnitRegistry
import pint

class FunctionGenerator:
    def __init__(self, visa_search_term):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)
        self.ureg = UnitRegistry()

# Link to manual: http://www.ece.mtu.edu/labs/EElabs/EE3306/Revisions_2008/agt33250aman.pdf

# Returning just a float vs. returning an actual pint.Quantity



class Agilent_33250A(): #same
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
         rm = visa.ResourceManager()
         self.inst = rm.open_resource(visa_search_term)
         self.ureg = pint.UnitRegistry()

    @frequency.setter
    def frequency(self, val):

        #max and min values taken from user manual
        if(val<1e-6):
            raise ValueError("Minimum frequency is 1µHz")
        elif((waveform_name == "SIN" or waveform_name=="SQU") and
             value>80e6)
            raise ValueError("Max frequency is 80 MHz for %s waves" % waveform_name)
        elif(waveform_name=="PULS" and (val<500e-6 or val>50e6))
            raise ValueError("Frequency must be between 500 µHz and 50 MHz for pulse waves")
        self.inst.write('FREQ %i' % val)

    @property
    def frequency(self):
        return float(self.inst.query('FREQ?')) * self.ureg.hertz

    # alias
    freq = frequency

    @property
    def volt(self):
        return float(self.inst.query('VOLT?')) * self.ureg.volt

    @volt.setter
    def volt(self, val):
        self.inst.write('VOLT %i' %val)

    # alias
    voltage = volt

    @property
    def phase(self):
        unit = self.inst.query('UNIT:ANGL?')
        if("RAD" in unit):
            return float(self.inst.query('PHAS?')) * self.ureg.radian
        return float(self.inst.query('PHAS?')) * self.ureg.degree

    @phase.setter
    def phase(self, val):
        self.inst.write('PHAS %f' % val)

    @property
    def duty_cycle(self):
        return float(self.inst.query('FUNCtion:SQUare:DCYCLe?'))

    @duty_cycle.setter
    def duty_cycle(self, val):
        self.inst.write('FUNCtion:SQUare:DCYCLe %f' % val)

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
            #don't need returns
            return self.inst.write('FUNC %s' % val)

        elif val.upper()[0:4] == 'USER':
            #don't need return
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
class SRS_DS345():
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
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)
        self.ureg = pint.UnitRegistry()

    def identify(self):
        """
        Returns:
            str: the response from the ``*IDN?`` GPIB query.
        """
        return self.inst.query('*IDN?')[:-1]

    @property
    def frequency(self):
        return float(self.inst.query('FREQ?')) * self.ureg.hertz

    @frequency.setter
    def frequency(self, val):
        if(self.waveform_name == "NOIS"):
            raise ValueError("Frequency must remain at 10 MHz when waveform is 'NOISE'")
        elif(val<1e-6):
            raise ValueError("Minimum frequency is 1 µHz")
        elif((self.waveform_name == "SIN" or self.waveform_name == "SQ") and
              val>30.2e6):
            raise ValueError("Maximum frequency is 30.2 MHz for %s waves" % waveform_name)
        elif(self.waveform_name == "RAMP" and val>1e5):
            raise ValueError("Maximum frequency is 100 KHz for ramp waves")
        self.inst.write('FREQ %i' % val)

    # alias
    freq = frequency

    @property
    def voltage(self):
        return float(self.inst.query('AMPL?')[:-3]) * self.ureg.volt

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

    # alias
    volt = voltage

    @property
    def phase(self):
        return float(self.inst.query('PHSE?')) * self.ureg.degree

    @phase.setter
    def phase(self, val):
        if(self.waveform_name == "NOIS" ):
            raise Exception("Can't set phase when waveform is 'NOISE'")
        self.inst.write('PHSE %f' % val)

class HP_33120A(): #same
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
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)
        self.ureg = pint.UnitRegistry()

    def identify(self):
        """
        Returns:
            str: the response from the ``*IDN?`` GPIB query.
        """
        return self.inst.query('*IDN?')[:-1]

    @property
    def frequency(self):
        return float(self.inst.query('FREQ?')) * self.ureg.hertz

    @frequency.setter
    def frequency(self, val):
        if(val<100e-6):
            raise ValueError("Minimum frequency is 100 µHz")
        elif((waveform_name == "SIN" or waveform_name == "SQU") and val>15e6):
            raise ValueError("Maximum frequency is 15 MHz for %s waves" % waveform_name)
        elif(waveform_name=="RAMP" and val>100e3):
            raise ValueError("Maximum frequency is 100 KHz for ramp waves")

        self.inst.write('FREQ %i' % val)

    # alias
    freq = frequency

    @property
    def volt(self):
        return float(self.inst.query('VOLT?')) * self.ureg.volt

    @volt.setter
    def volt(self, val):
        string = 'VOLT %f' % float(val)
        self.inst.write(string)

    # alias
    voltage = volt

    @property
    def phase(self):
        return float(self.inst.query('PHAS?')) * self.ureg.degree


    @phase.setter
    def phase(self, val):
        self.inst.write('PHAS %f' % val)


    @property
    def duty_cycle(self):
        return float(self.inst.query('FUNCtion:SQUare:DCYCLe?'))

    @duty_cycle.setter
    def duty_cycle(self, val):
        self.inst.write('FUNCtion:SQUare:DCYCLe %f' % val)

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
            return self.inst.write('FUNC %s' % val)

        elif val.upper()[0:4] == 'USER':
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
