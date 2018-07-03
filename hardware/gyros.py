"""
Fiber Optic Gyroscopes
======================

.. module:: gyros
   :platform: Windows, Linux, OSX
   :synopsis: Provides support for common operations in characterizing fiber
      optic gyroscopes.

.. moduleauthor:: Jonathan Wheeler <jamwheel@stanford.edu>
"""



try:
    from hardware import lia, rot, daq
except:
    print(
        "Could not automatically import at least one of the following:\n"
        "   - lock-in amplifier rotation\n"
        "   - rotation stage\n"
        "   - data acquisition unit\n"
        "Some functions may not work.")

from allantools import oadev
import time
from numpy import floor, mean, cos, pi, zeros, nan, log10
from pyfog import Tombstone, InsufficientSampleTimeError, InsufficientSamplingRateError
import json
import re
import threading

class Gyro:
    """
    An object which contains functions for automating characterization of
    fiber optic gyroscopes.

    Args:
        filepath (str): A filepath to a json file containing properties of
            the gyro.

    Examples:
        Suppose a json file ``kvothe.json`` contains the following markup 
        describing a gyro
        named `Kvothe`.

        .. code:: json

            { // Specs for the Kvothe Gyro
                "diameter": 0.08, // Meters
                "length": 1085, // meters
                "pitch": 37.4 // degrees
            }

        The following code will initialize the gyro objects

        >>> from hardware import *
        >>> gyro = hardware.gyros.Gyro('kvothe.json')

        From here, different tests can be run on the gyro.

        >>> test1 = gyro.tombstone(hours=4)

    """
    def __init__(self, filepath):
        with open(filepath) as gyro_file:
            string = ""

            # Strip any comments
            for line in gyro_file:
                string += re.sub('//.*', '', line)
            self.data = json.loads(string)

            self.filepath = filepath

            if 'name' in self.data:
                self.name = self.data['name']
            if 'length' in self.data:
                self.length = self.data['length']
            if 'pitch' in self.data:
                self.pitch = self.data['pitch']
            if 'diameter' in self.data:
                self.diameter = self.data['diameter']
                self.radius = self.data['diameter'] / 2
            if 'radius' in self.data:
                self.diameter = self.data['radius'] * 2
                self.radius = self.data['radius']

    def __repr__(self):
        return "Gyro('%s')" % self.filepath

    def __getitem__(self, key):
        return self.data[key]

    def home(self):
        """
        Returns fiber optic gyroscope to home position. Ideally, the home
        position should be calibrated to rotational east or west such that
        when the gyro is in this position, it does not detect any component
        of the earth rate.
        """
        rot.angle = 0

    def autophase(self, sensitivity=0.03, velocity=1):
        """
        Attempts to place all of the rotation signal in the X quadrature of the
        lock-in amplifier.

        Args:
            sensitivity (float): the sensitivity of the lock in amplifier in
                volts
            velocity (float): the angular velocity of the rotation stage in
                deg/s

        """
        tmp_sensitivity = lia.sensitivity
        tmp_velocity = rot.velocity

        rot.velocity = velocity
        lia.sensitivity = sensitivity
        start_angle = rot.angle
        rot.ccw(2, background=True)
        time.sleep(1)
        lia.autophase()

        rot.velocity = tmp_velocity
        lia.sensitivity = tmp_sensitivity
        time.sleep(3)
        rot.angle = start_angle

    def get_scale_factor(self, sensitivity=None, velocity=1, pitch=None):
        """
        A partial
        python port of Jacob Chamoun's matlab script to grab the scale factor

        Args:
            sensitivity (float): The sensitivity of the lock-in amplifier
            pitch (float): The angle between the gyro normal and the rotation
                stage normal
            velocity (float): The rotation stage velocity in units of °/s.

        Returns:
            float: The scale factor :math:`S`.

            This scale factor converts
            between the rotation in degrees
            per hour, and the lock-in amplifier output in volts.

            :math:`\Omega[t] = S \cdot V[t]`
        """

        if not sensitivity:
            sensitivity = self.data.get('sensitivity', .3)
        # set sensitivity and store current sensitivity
        cal_sensitivity = lia.sensitivity
        lia.sensitivity = sensitivity

        # set the integration time and filter slope and store the current
        # integration
        cal_integration_time = lia.time_constant
        lia.time_constant = 0.01
        
        # set the rotation speed and store the current
        # rotation speed
        cal_velocity = rot.velocity
        rot.velocity = velocity

        # set the acquisition rate
        cal_acquisition_rate = floor(1/cal_integration_time) # should this be 1/(3*integration time)??

        # start acquisition and store the calibrated data
        rot.ccw(velocity * 4.5, background=True)
        time.sleep(1)
        ccw_data = daq.read(seconds=3, rate=cal_acquisition_rate,
                            verbose=False)
        time.sleep(5)

        rot.cw(velocity * 4.5, background=True)
        time.sleep(1)
        cw_data = daq.read(seconds=3, rate=cal_acquisition_rate, verbose=False)
        time.sleep(5)

        lia.time_constant = cal_integration_time
        lia.sensitivity = cal_sensitivity
        rot.velocity = cal_velocity

        if not pitch:
            pitch = float(self.data.get('pitch', 0))

        volt_seconds_per_degree = (mean(ccw_data) - mean(cw_data))/2\
            / cos(pitch * pi / 180) / velocity
        volt_hours_per_degree = volt_seconds_per_degree / 3600
        degrees_per_hour_per_volt = 1 / volt_hours_per_degree
        return degrees_per_hour_per_volt

    def tombstone(self, seconds=None, minutes=None, hours=None, rate=None,
                  autophase=False, autohome=True, scale_factor=0, sensitivity=None,max_duration=None):
        """
        Performs a tombstone test of the gyro. The gyro records a time series
        of rotation data when no rotation is applied to it. This data can be
        used to test the noise and bias stability of the gyroscope.

        Args:
            seconds (float): The number of seconds
            minutes (float): The number of minutes
            hours (float): The number of hours
            rate (float): The sampling rate
            autophase (bool): If true, an autophase routine will be run.
            autohome (bool): If true, the gyro will return to the home position
                before running the tombstone test.
            scale_factor (float): The scale factor to use in order to convert
                between lock-in amplifier voltage and rotation rate in units
                of deg/h/Volt. If this is not set, the gyro will run the
                :func:`hardware.gyros.get_scale_factor` routine.
			Sensitivity (float): The sensitivity of the LIA for the scale
				calibration and taking data. Put in [V]

        Returns:
            Tombstone: A :class:`pyfog.tombstone.Tombstone` object

            This object contains all of the data and settings from this run.
        """
        duration = 0
        if seconds:
            duration += seconds
        if minutes:
            duration += minutes * 60
        if hours:
            duration += hours * 3600

        if autohome:
            self.home()

        if autophase:
            self.autophase()

        if scale_factor == "auto":
            scale_factor = self.scale_factor

        elif not scale_factor:
            scale_factor = self.get_scale_factor(sensitivity = sensitivity)

        start = time.time()

        if duration:
            print('Running sync')
            data = daq.read(duration, rate)
            if not rate:
                rate = len(data)/duration
            return Tombstone(data, rate, start=start, scale_factor=scale_factor)

        # Assume asynchronous
        if not max_duration:
            max_duration = 24*60*60

        if not rate:
            rate = 10
        initial_values = zeros(max_duration * rate)
        initial_values.fill(nan)

        tmb = Tombstone(initial_values, rate=rate, start=time.time(), scale_factor=scale_factor)
        
        tmb._data_thread = StoppableThread(target=self.detector, args=(tmb,), kwargs={"rate": rate, "max_duration": max_duration})
        tmb._adev_check_thread = StoppableThread(target=self.adev_checker, args=(tmb,))
        tmb._data_thread.start()
        tmb._adev_check_thread.start()
        return tmb

    def get_arw(self, seconds=60, autophase=False, autohome=True,
                scale_factor=None, rate=None):
        """
        Performs a tombstone test of the gyro, but rather than returning a
        :class:`pyfog.tombstone.Tombstone` object, it returns the ARW in units
        of deg/√h. If this is not set, the gyro will run the
        :func:`hardware.gyros.get_scale_factor` routine.

        Args:
            seconds (float): The number of seconds
            minutes (float): The number of minutes
            hours (float): The number of hours
            rate (float): The sample rate
            autophse (bool): If true, the gyro will return to the home position
                before running the tombstone test.
            scale_factor (float): The scale factor to use in order to convert
            between lock-in amplifier voltage and rotation rate in units of
            °/h/Volt. If this is not set, the gyro will run the

        Returns:
            float: The angular random walk in units of °/√h
        """
        if not scale_factor:
            scale_factor = self.get_scale_factor()

        data = daq.read(seconds, rate=rate)
        if not rate:
            rate = len(data/duration)
        _, dev, _, _ = oadev(data*scale_factor, rate=rate, data_type='freq',
                             taus=[1])
        return dev[0]/60

    def detector(self, tmb, rate, max_duration):
        data = daq.read(1, rate, asynchronous=True)
        i=0
        while i < rate*max_duration:
            data_to_add = next(data)
            next_i = i + len(data_to_add)
            if next_i > len(tmb): break
            tmb.iloc[i:next_i] = data_to_add
            i = next_i 
            if tmb._data_thread.stopped():
                return
        self.notify('Reached max duration')
        tmb.stop()

        
    def adev_checker(self, tmb, period=5, threshold=5):
        """Check every {period} seconds until ADev max climbs {threshold} dB above ADev min"""
        while True:
            time.sleep(period)
            if tmb._adev_check_thread.stopped():
                return
            try:
                ratio = 10*log10(max(tmb.devs[tmb.drift_idx:]) / tmb.drift)
                if ratio > threshold:
                    self.notify('Reached ADev Min')
                    break
            except InsufficientSampleTimeError as iste:
                # We expect a lot of ADev errors until we get enough data
                pass
            except InsufficientSamplingRateError as isre:
                self.notify('Sampling rate too small. Cannot resolve drift')
                break
        tmb.stop()

        
    def notify(self, msg):
        """Some function we can use to notify the user that a thread has finished"""
        print(msg)

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()