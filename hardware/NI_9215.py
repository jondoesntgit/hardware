"""
NI 9215
=======

.. module:: NI_9215
   :platform: Unix, Windows
   :synopsis: NI 9215 DAQ Unit Wrapper

.. moduleauthor:: Jonathan Wheeler <jamwheel@stanford.edu>

This module provides support for the `NI 9215`_ Data Acquisition Unit.
Much of the code base was adapted from examples at <https://pythonhosted.org/PyDAQmx/>.
It is my understanding that the examples make use of C code, so if you have questions
on what specific methods do inside of my code, please search for the documentation
on NI, as they have much more documentation than I do.

.. _NI 9215: https://sine.ni.com/nips/cds/view/p/lang/en/nid/208793

"""

from PyDAQmx import *
import numpy
from hardware import *

class NI_9215:
    def __init__(self, device_name="Dev1"):
        self.device_name = device_name
        self.rate = None
        self.max_voltage = None

    def read(self,seconds=1, rate=None, max_voltage=None,timeout=0, verbose=True):
        """
        Return data from the DAQ.

        Parameters
        ----------
        seconds : int, float
            Sample duration in seconds
        rate : int, float
            Number of samples to collect per second
        max_voltage : float
            Scale factor. The DAQ expects a range of voltages ranging from -10V
            to +10V. The max_voltage tells ``read()`` what to scale a 10V signal
            by.
        timeout : int, float
            Amount of time after which the program should timeout and give up
            on collecting data.

            - 0 (default) - calculate the timeout based on duration and sample rate
            - -1 - do not time out.
            - other - the timeout


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
                max_voltage_string = "%2g uV" % (max_voltage * 1e-6)
            elif max_voltage > 1e-9:
                max_voltage_string = "%2g nV" % (max_voltage * 1e-9)
            if verbose:
                print("Auto-setting max_voltage to %s based on "
                "LIA settings" % max_voltage_string)



        sample_size = int(seconds * rate)
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
            DAQmxCfgSampClkTiming(taskHandle, "", rate, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, sample_size)
            # DAQmx Start Code
            DAQmxStopTask(taskHandle)
            DAQmxStartTask(taskHandle)

            # DAQmx Read Code
            DAQmxReadAnalogF64(taskHandle, sample_size, timeout, DAQmx_Val_GroupByChannel, self.data, sample_size, byref(read), None)

            #print("Acquired %d points" % read.value)
        except DAQError as err:
            print("DAQmx Error: %s" % err)
        finally:
            if taskHandle:
                # DAQmx Stop Code
                DAQmxStopTask(taskHandle)
                DAQmxClearTask(taskHandle)

        #TODO clean this up
        self.data = self.data/10 * max_voltage
        return self.data

    def identify(self):
        buf = ctypes.create_string_buffer(16)
        DAQmxGetDevProductType(self.device_name, buf, 16);
        return "".join([(c).decode() for c in buf][:-1])

    def reset(self):
        DAQmxResetDevice(self.device_name)

"""This example is a PyDAQmx version of the ContAcq_IntClk.c example
It illustrates the use of callback functions

This example demonstrates how to acquire a continuous amount of
data using the DAQ device's internal clock. It incrementally stores the data
in a Python list.
"""

