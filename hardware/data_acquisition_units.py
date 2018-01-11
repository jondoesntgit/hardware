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
import queue
import time


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
    def __init__(self, device_name=None, max_voltage=None, rate=None):
        if not device_name:
            # Note, this will probably not work if multiple devices exist
            n=1024
            data1 = ctypes.create_string_buffer(n)
            DAQmxGetSysDevNames(data1, n)
            device_name = data1.value.decode('utf-8')

        self.device_name = device_name
        self.rate = rate
        self.max_voltage = max_voltage

    def read(self, seconds=1, rate=None, max_voltage=None, timeout=0,
             verbose=False, oversampling_ratio=10, task_name=""):
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
            from hardware import lia
            rate = .1/lia.time_constant
            rate = max(2, rate)
            if verbose:
                print("Auto-setting sampling rate to %2g Hz based on "
                "LIA settings" % rate)

        # gather the maximum voltage from the inputs
        if max_voltage:
            # used the passed max_voltage
            pass
        elif self.max_voltage:
            max_voltage = self.max_voltage
        else:
            from hardware import lia
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
            DAQmxCreateTask(task_name, byref(taskHandle))
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
        return numpy.mean(self.data.reshape(-1, oversampling_ratio), axis=1)

    class CallbackTask(Task):
        def __init__(self, rate, chunk_seconds, oversampling_ratio, max_voltage, device_name, timeout):

            self.timeout = timeout
            self.max_voltage = max_voltage
            self.oversampling_ratio = oversampling_ratio

            Task.__init__(self)

            self.queue = queue.Queue()
            self.chunk_size = int(chunk_seconds * rate * oversampling_ratio)
            self.data = numpy.zeros(self.chunk_size)
            self.CreateAIVoltageChan("%s/ai0" % device_name, "", DAQmx_Val_Diff ,-10, 10, DAQmx_Val_Volts,None)
            self.CfgSampClkTiming("", rate*oversampling_ratio ,DAQmx_Val_Rising,DAQmx_Val_ContSamps, self.chunk_size)

            # Map EveryNCallback and DoneCallback into C callback functions
            self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer,self.chunk_size,0)
            self.AutoRegisterDoneEvent(0)

        def EveryNCallback(self):
            read = int32()
            self.ReadAnalogF64(self.chunk_size,self.timeout,DAQmx_Val_GroupByScanNumber,self.data,self.chunk_size,byref(read),None)
            #self.a.extend(self.data.tolist())
            self.data = self.data/10 * self.max_voltage
            self.queue.put(numpy.mean(self.data.reshape(-1, self.oversampling_ratio), axis=1) / 10 * self.max_voltage)
            return 0 # The function should return an integer
        def DoneCallback(self, status):
            print ("Status",status.value)
            return 0 # The function should return an integer)

        def data_stream(self):
            """A generator that returns chunks of data"""
            while True:
                yield self.queue.get()
            

    def async_read(self, chunk_seconds=1, rate=None, max_voltage=None, timeout=0,
             verbose=False, oversampling_ratio=10, task_name=""):
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
            from hardware import lia
            rate = .1/lia.time_constant
            rate = max(2, rate)
            if verbose:
                print("Auto-setting sampling rate to %2g Hz based on "
                "LIA settings" % rate)

        # gather the maximum voltage from the inputs
        if max_voltage:
            # used the passed max_voltage
            pass
        elif self.max_voltage:
            max_voltage = self.max_voltage
        else:
            from hardware import lia
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

        chunk_sample_size = int(chunk_seconds * rate * oversampling_ratio)

        self.task = self.CallbackTask(rate, chunk_seconds, oversampling_ratio, max_voltage, self.device_name, timeout)
        self.task.StartTask()

    def data_stream(self):
        return self.task.data_stream()

    def stop(self):
        self.task.StopTask()
        self.task.ClearTask()
        

    def identify(self):
        """
        Returns:
           str: response of ``DAQmxGetDevProductType``"""
        buf = ctypes.create_string_buffer(16)
        DAQmxGetDevProductType(self.device_name, buf, 16);
        return "".join([(c).decode() for c in buf][:-1])

    @property
    def tasks(self):
        n=1024
        data1 = ctypes.create_string_buffer(n)
        DAQmxGetSysTasks(data1, n)
        return data1.value.decode('utf-8')

    def reset(self):
        """Resets the DAQ to factory settings"""
        DAQmxResetDevice(self.device_name)
