"""
Data Acquisition Units
======================

.. module:: data_acquisition_units
   :platform: Windows
   :synopsis: DAQ Unit Wrappers

.. moduleauthor:: Jonathan Wheeler <jamwheel@stanford.edu>
"""

try:
    from PyDAQmx import *
except:
    print("It seems that niDAQmx is not installed on this system.")

import numpy
import ctypes
from ctypes import byref
from hardware import *


class NI_9215:
    """
    This class provides support for the `NI 9215`_ Data
    Acquisition Unit. Much of the code base was adapted from examples at
    `<https://pythonhosted.org/PyDAQmx/>`_. It is my understanding that the
    examples make use of C code, so if you have questions on what specific
    methods do inside of my code, please search for the documentation on
    NI, as they have much more documentation than is supplied here.

    .. _NI 9215: https://sine.ni.com/nips/cds/view/p/lang/en/nid/208793

    .. note:: This class will not work unless you have installed ``niDAQmx``
       which is only available on Windows systems.


    """
    def __init__(self, device_name=None):
        if not device_name:
            # Note, this will probably not work if multiple devices exist
            n=1024
            data1 = ctypes.create_string_buffer(n)
            DAQmxGetSysDevNames(data1, n)
            device_name = str(data1.value)

        self.device_name = device_name
        self.rate = None
        self.max_voltage = None

    def read(self, seconds=1, rate=None, max_voltage=None, timeout=0,
             verbose=False, oversampling_ratio=10):
        """
        Parameters
        ----------
        seconds : int, float
            Sample duration in seconds
        rate : int, float
            Number of samples to collect per second. If not specified, will
            default to the maximum of either 2 or the reciprocal of the
            detected lock-in amplifier's time constant.
        max_voltage : float
            Scale factor. The DAQ expects a range of voltages ranging from -10V
            to +10V. The max_voltage tells ``read()`` what to scale a 10V
            signal by. If not specified, will default to the lock-in
            amplifier's sensitivity.
        timeout : int, float
            Amount of time after which the program should timeout and give up
            on collecting data.

            - 0 (default) - calculate the timeout based on duration and
                sample rate
            - -1 - do not time out.
            - other - the timeout
        verbose : bool
            If set to ``True``, this function will output any assumptions made
            about the ``rate`` or ``max_voltage`` parameters.
        oversampling_ratio : int
            If N samples of the same quantity are taken, each with 
            uncorrelated errors, averaging these values will reduce the noise
            by a factor of :math:`\sqrt{N}`. By default, the output rate of 
            the data returned by 'read' is 1/10 the bandwidth of the lock-in
            amplifier. We can reduce our noise to a theoretical limit by sampling
            at the lock-in amplifier bandwidth, and then downsampling via simple
            averages of size N.

        Returns
        -------
        numpy.array
            A one-dimensional numpy array of the data.
        """

        # gather the rate from the inputs
        if rate and rate < 2:
            raise ValueError("Frequency needs to be > 2 Hz. You gave %f" % rate)
        elif rate:
            # use the passed rate
            pass
        elif self.rate:
            rate = self.rate
        else:
            rate = .1/lia.time_constant
            rate = max(2, rate)
            if verbose:
                print("Auto-setting sampling rate to %2g Hz based on "
                "LIA settings" % rate)

        # gather the maximum voltage from the inputs
        if max_voltage is None and self.max_voltage:
            max_voltage = self.max_voltage
        else:
            max_voltage = lia.sensitivity
            max_voltage_string = "%2g V"
            if max_voltage > .001:
                max_voltage_string = "%2g mV" % (max_voltage * 1e3)
            elif max_voltage > 1e-6:
                max_voltage_string = "%2g uV" % (max_voltage * 1e6)
            elif max_voltage > 1e-9:
                max_voltage_string = "%2g nV" % (max_voltage * 1e9)
            if verbose:
                print("Auto-setting max_voltage to %s based on "
                "LIA settings" % max_voltage_string)

        sample_size = int(seconds * rate * oversampling_ratio)
        if timeout == 0:
            timeout = seconds
        # Declaration of variable passed by reference
        taskHandle = TaskHandle()
        read = int32()
        self.data = numpy.zeros((sample_size,), dtype=numpy.float64)

        try:
            # DAQmx Configure Code
            DAQmxCreateTask("", byref(taskHandle))
            DAQmxCreateAIVoltageChan(taskHandle, "%s/ai0" % self.device_name, "", DAQmx_Val_Cfg_Default, -10, 10, DAQmx_Val_Volts,
                                     None)
            DAQmxCfgSampClkTiming(taskHandle, "", rate*oversampling_ratio, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, sample_size)
            # DAQmx Start Code
            DAQmxStopTask(taskHandle)
            DAQmxStartTask(taskHandle)

            # DAQmx Read Code
            DAQmxReadAnalogF64(taskHandle, sample_size, timeout, DAQmx_Val_GroupByChannel, self.data, sample_size, byref(read), None)

            # print("Acquired %d points" % read.value)
        except DAQError as err:
            print("DAQmx Error: %s" % err)
        finally:
            if taskHandle:
                # DAQmx Stop Code
                DAQmxStopTask(taskHandle)
                DAQmxClearTask(taskHandle)

        # TODO clean this up
        self.data = self.data/10 * max_voltage
        return numpy.mean(self.data.reshape(-1, 3), axis=1)

    def identify(self):
        """
        Returns:
           str: response of ``DAQmxGetDevProductType``"""
        buf = ctypes.create_string_buffer(16)
        DAQmxGetDevProductType(self.device_name, buf, 16);
        return "".join([(c).decode() for c in buf][:-1])

    def reset(self):
        """Resets the DAQ to factory settings"""
        DAQmxResetDevice(self.device_name)
