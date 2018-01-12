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
        self.task = None

    def read(self, seconds, rate=None, max_voltage=None, timeout=0,
             verbose=False, oversampling_ratio=10, task_name="", 
             asynchronous=False):
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
        task_name : str
            A name for the task in the NI system
        asynchronous : bool
            Default set to false. However, if true, will allow user to perform
            other tasks while the read runs in the background. Data can
            be fetched in groups of chunk_sizes (specified by seconds and
            rate) by using the ``next(g)`` syntax. This function will return
            a generator instead of an array.

        Returns
        -------
        numpy.array
            A one-dimensional numpy array of the data.
        generator
            If asynchronous is set to true, a generator will be returned.
            Using the ``next(g)`` syntax will yield a chunk of data of size
            rate * seconds
        """
        rate = self._get_rate(rate, oversampling_ratio)
        max_voltage = self._get_max_voltage(max_voltage)
 

        self.task = self.FOG_DAQ_Task(
            self, seconds, rate, oversampling_ratio, max_voltage, asynchronous)

        if asynchronous:
            self.queue = queue.Queue()
            self.task.StartTask()
            def gen(q):
                while True:
                    yield q.get()

            return gen(self.queue)

        if not asynchronous:
            self.task.StartTask()
            self.task.run()
            self.task.StopTask()
            self.task.ClearTask()
            self.task = None
            return self.data

    class FOG_DAQ_Task(Task):
        def __init__(self, daq, seconds, rate, oversampling_ratio, max_voltage, asynchronous):

            Task.__init__(self)

            self.daq = daq
            self.max_voltage = max_voltage
            self.oversampling_ratio = oversampling_ratio
            self.asynchronous = asynchronous

            sample_size = int(seconds * rate * oversampling_ratio)
            self.raw_data = numpy.zeros((sample_size,), dtype=numpy.float64)

            ##############################
            # Setup for CfgSampClkTiming #
            ##############################

            # the source terminal of the Sample Clock. 
            # To use the internal clock, of the device, set to Null
            source = ""

            # the sampling rate in samples per second per channel. If you use 
            # an external source for the Sample Clock, set this value to the
            # maximum expected rate of that clock
            sampling_rate = rate * oversampling_ratio

            # Specifies on which edge of the clock to acquire or generate 
            # samples
            active_edge = DAQmx_Val_Rising

            # Specifies whether the task acquires or generates samples 
            # continuously or if it acquires or generates a finite number of
            # samples.
            if asynchronous:
                sample_mode = DAQmx_Val_ContSamps
            else:
                sample_mode = DAQmx_Val_FiniteSamps

            # The number of samples to acquire for each channel in the task.
            # If sample mode is finite, this is the total number of samples.
            # If sample is continuous, this is the buffer size. 
            samps_per_channel_to_acquire = sample_size

            #################################
            # Setup for CreateAIVoltageChan #
            #################################

            # You can specify a list or range of channels
            physical_channel = "%s/ai0" % daq.device_name

            # The name(s) to assign the created virtual channel(s). 
            # If you do not specify a name NI-DAQmx uses the physical channel
            # name as the virtual channel name.
            name_to_assign_channel = ""

            # The input terminal configuration for the channel. For the 
            # NI9215, this defaults to differential between the coax wire and 
            # sheath.
            terminal_config = DAQmx_Val_Cfg_Default

            # The minimum and maximum values you expect to detect in `units`.
            # The lock-in-amplifier has an output range of -10 to 10 Volts, 
            # corresponding to max and min values at its sensitivity. 

            min_val = -10
            max_val = 10

            # The units to used to return voltage measurements
            units = DAQmx_Val_Volts

            # If you're using voltage as your units, this should be set to
            # None.
            custom_scale_name = None

            #########################
            # Configure #
            #########################

            self.CreateAIVoltageChan(
                    physical_channel, name_to_assign_channel, terminal_config,
                    min_val, max_val, units, custom_scale_name)

            self.CfgSampClkTiming(
                    source, sampling_rate, active_edge, sample_mode, 
                    sample_size)

            if asynchronous:
                # Map EveryNCallback and DoneCallback into C callback functions
                self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer,sample_size,0, name='run')
                self.AutoRegisterDoneEvent(0, name='finish')

        def run(self):
            ###########################
            # Setup for ReadAnalogF64 #
            ###########################

            # The number of samples, per channel, to read. If read_array does
            # not contain enough space, ReadAnalogF64 returns as many samples 
            # as fit in read_array
            num_samps_per_channel = len(self.raw_data)

            # The amount of time, in seconds, to wait for the function to read
            # the samples. An infinite wait is specified by -1. The 
            # ReadAnalogF64 function returns an error if the timeout elapses
            timeout = -1

            # Specifies whether or not the samples are interleaved
            fill_mode = DAQmx_Val_GroupByChannel

            # The array to read samples into, organized according to the 
            # filling mode
            read_array = self.raw_data

            # The size of the array, in samples, into which samples are read
            array_size_in_samps = len(self.raw_data)

            # The actual number of samples read from each channel
            samples_per_channel_read = byref(int32())

            # Reserved for future use. Pass NULL to this parameter
            reserved = None

            self.ReadAnalogF64(
                    num_samps_per_channel, timeout, fill_mode, read_array, 
                    array_size_in_samps, samples_per_channel_read, reserved)

            # Scale
            data = self.raw_data/10 * self.max_voltage

            # Downsample
            data = numpy.mean(data.reshape(-1, self.oversampling_ratio), axis=1)

            if self.asynchronous:
                self.daq.queue.put(data)
                return 0
            else:
                self.daq.data = data

        def finish(self, status):
            return 0 # The function should return an integer)
            
    def stop(self):
        """ If running in asynchronous mode, this stops the task"""
        self.task.StopTask()
        self.task.ClearTask()
        self.task = None

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

    def _get_rate(self, rate, oversampling_ratio):
        # gather the rate from the inputs
        if rate and oversampling_ratio and rate * oversampling_ratio < 2:
            raise ValueError(
                "Frequency needs to be > 2 Hz. "
                "You gave a rate of %f and an oversampling ratio of %f. "
                "Try increasing the oversampling ratio" 
                % (rate, oversampling_ratio))
        elif rate:
            # use the passed rate
            return rate
        elif self.rate:
            return self.rate
        else:
            from hardware import lia
            rate = .1/lia.time_constant
            return max(2, rate)

    def _get_max_voltage(self, max_voltage):
        # gather the maximum voltage from the inputs
        if max_voltage:
            # used the passed max_voltage
            return max_voltage
        elif self.max_voltage:
            return self.max_voltage
        else:
            from hardware import lia
            return lia.sensitivity
            