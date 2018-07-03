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


class Agilent_33250A():
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

    def identify(self):
        """
        Returns:
            str: the response from the ``*IDN?`` GPIB query.
        """
        return self.inst.query('*IDN?')[:-1]

    @property
    def frequency(self):
        f = self.inst.query('FREQ?')
        return float(f)

    @frequency.setter
    def frequency(self, val):
        self.inst.write('FREQ %i' % val)

    # alias
    freq = frequency

    @property
    def volt(self):
        return float(self.inst.query('VOLT?'))

    @volt.setter
    def volt(self, val):
        string = 'VOLT %f' % float(val)
        self.inst.write(string)

    # alias
    voltage = volt

    @property
    def phase(self):
        return float(self.inst.query('PHAS?'))

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

    def set_duty_cycle(self, r, rise_time_over_cycle_time=0, fall_time_over_cycle_time=0):
        from pyfog.waveforms import square_pulse
        signal = square_pulse(
            4e3,
            duty_cycle = r,
            rise_time_over_cycle_time = rise_time_over_cycle_time,
            fall_time_over_cycle_time = fall_time_over_cycle_time,
        )

        __timeout = self.inst.timeout
        self.inst.timeout = 10e3
        self.upload_as(signal, 'PULSEWAVEFORM')
        self.waveform = 'USER'
        self.waveform = 'USER PULSEWAVEFORM'
        self.inst.timeout = __timeout

    def set_double_gate(self, r1, r2, duty_cycle=.50, rise_time_over_cycle_time=0, fall_time_over_cycle_time=0):
        from pyfog.waveforms import square_pulse
        signal1 = square_pulse(
            2e3,
            duty_cycle = r1,
            rise_time_over_cycle_time = rise_time_over_cycle_time,
            fall_time_over_cycle_time = fall_time_over_cycle_time,
        )

        signal2 = square_pulse(
            2e3,
            duty_cycle = r2,
            rise_time_over_cycle_time = rise_time_over_cycle_time,
            fall_time_over_cycle_time = fall_time_over_cycle_time,
        )

        signal1=np.roll(signal1, -int(2e3*r1/2))
        signal2=np.roll(signal2, -int(2e3*r2/2))

        signal = np.concatenate([signal1, signal2])

        __timeout = self.inst.timeout
        self.inst.timeout = 10e3
        self.upload_as(signal, 'PULSEWAVEFORM')
        self.waveform = 'USER'
#        self.waveform = 'USER PULSEWAVEFORM'
        self.inst.timeout = __timeout

    def set_double_gate_no_roll(self, r1, r2, rise_time_over_cycle_time=0, fall_time_over_cycle_time=0):
        from pyfog.waveforms import square_pulse
        signal1 = square_pulse(
            2e3,
            duty_cycle = r1,
            rise_time_over_cycle_time = rise_time_over_cycle_time,
            fall_time_over_cycle_time = fall_time_over_cycle_time,
        )

        signal2 = square_pulse(
            2e3,
            duty_cycle = r2,
            rise_time_over_cycle_time = rise_time_over_cycle_time,
            fall_time_over_cycle_time = fall_time_over_cycle_time,
        )
        signal = np.concatenate([signal1, signal2])

        __timeout = self.inst.timeout
        self.inst.timeout = 10e3
        self.upload_as(signal, 'PULSEWAVEFORM')
        self.waveform = 'USER'
#        self.waveform = 'USER PULSEWAVEFORM'
        self.inst.timeout = __timeout

    def set_double_gate_and_notch(self, r1, r2, r3, phase,  rise_time_over_cycle_time=0, fall_time_over_cycle_time=0):
        from pyfog.waveforms import square_pulse
        signal1 = square_pulse(
            2e3,
            duty_cycle = r1,
            rise_time_over_cycle_time = rise_time_over_cycle_time,
            fall_time_over_cycle_time = fall_time_over_cycle_time,
        )

        signal2 = square_pulse(
            2e3,
            duty_cycle = r2,
            rise_time_over_cycle_time = rise_time_over_cycle_time,
            fall_time_over_cycle_time = fall_time_over_cycle_time,
        )

        signal1=np.roll(signal1, -int(2e3*r1/2))
        signal2=np.roll(signal2, -int(2e3*r2/2))

        signal = np.concatenate([signal1, signal2])

        signal3 = square_pulse(
            4e3, duty_cycle=r3
        )
        signal3 = -np.roll(signal3, int(phase/360*4e3))

        __timeout = self.inst.timeout
        self.inst.timeout = 10e3
        self.upload_as(signal * signal3, 'PULSEWAVEFORM')
        self.waveform = 'USER'
#        self.waveform = 'USER PULSEWAVEFORM'
        self.inst.timeout = __timeout

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
        ``volt`` waveform (str):  A string in the array
            ``['SIN', 'SQU', 'RAMP', 'PULS', 'NOIS', 'DC', 'USER' ]``
        phase (float): The relative phase to other instruments synced through
        the 10 MHz reference clock.
        duty_cycle (float): The duty cycle of the square wave form in percent.
    """
    def __init__(self, visa_search_term):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)

    def identify(self):
        """
        Returns:
            str: the response from the ``*IDN?`` GPIB query.
        """
        return self.inst.query('*IDN?')[:-1]

    @property
    def frequency(self):
        f = self.inst.query('FREQ?')

        return float(f)

    @frequency.setter
    def frequency(self, val):
        self.inst.write('FREQ %i' % val)

    # alias
    freq = frequency

    @property
    def voltage(self):
        return float(self.inst.query('AMPL?')[:-3])

    @voltage.setter
    def voltage(self, val):
        self.inst.write('AMPL %f' % val)

    # alias
    volt = voltage

    @property
    def phase(self):
        return float(self.inst.query('PHSE?'))

    @phase.setter
    def phase(self, val):
        self.inst.write('PHSE %f' % val)

class HP_33120A():
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

    def identify(self):
        """
        Returns:
            str: the response from the ``*IDN?`` GPIB query.
        """
        return self.inst.query('*IDN?')[:-1]

    @property
    def frequency(self):
        f = self.inst.query('FREQ?')
        return float(f)

    @frequency.setter
    def frequency(self, val):
        self.inst.write('FREQ %i' % val)

    # alias
    freq = frequency

    @property
    def volt(self):
        return float(self.inst.query('VOLT?'))

    @volt.setter
    def volt(self, val):
        string = 'VOLT %f' % float(val)
        self.inst.write(string)

    # alias
    voltage = volt

    @property
    def phase(self):
        return float(self.inst.query('PHAS?'))

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