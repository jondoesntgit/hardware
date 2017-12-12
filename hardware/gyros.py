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
    print("""Could not automatically import lock-in amplifier and rotation
    stage. Some functions may not work.
    """)

from allantools import oadev
import time
from numpy import floor, mean, cos, pi
from pyfog import Tombstone
import json
import re


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
        time.sleep(.5)
        lia.autophase()

        rot.velocity = tmp_velocity
        lia.sensitivity = tmp_sensitivity
        rot.wait_until_motor_is_idle()
        rot.angle = start_angle

    def get_scale_factor(self, sensitivity=.3, velocity=1, pitch=None):
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

        # set sensitivity and store current sensitivity
        cal_sensitivity = lia.sensitivity
        lia.sensitivity = sensitivity

        # set the integration time and filter slope and store the current
        # integration
        cal_integration_time = lia.time_constant
        lia.time_constant = 0.01

        cal_velocity = rot.velocity
        rot.velocity = velocity

        # set the acquisition rate
        cal_acquisition_rate = floor(1/cal_integration_time)

        # start acquisition and store the calibrated data
        rot.ccw(5, background=True)
        time.sleep(1)
        ccw_data = daq.read(seconds=3, rate=cal_acquisition_rate,
                            verbose=False)
        time.sleep(2)

        rot.cw(5, background=True)
        time.sleep(1)
        cw_data = daq.read(seconds=3, rate=cal_acquisition_rate, verbose=False)
        time.sleep(2)

        lia.time_constant = cal_integration_time
        lia.sensitivity = cal_sensitivity
        rot.velocity = cal_velocity

        if not pitch:
            pitch = float(self.data.get('pitch', 0))

        volt_seconds_per_degree = (mean(ccw_data) - mean(cw_data))/2\
            / cos(pitch * pi / 180)
        volt_hours_per_degree = volt_seconds_per_degree / 3600
        degrees_per_hour_per_volt = 1 / volt_hours_per_degree
        return degrees_per_hour_per_volt

    def tombstone(self, seconds=None, minutes=None, hours=None, rate=10,
                  autophase=False, autohome=True, scale_factor=0):
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

        if not time:
            raise ValueError("Cannot test for 0 seconds.")

        if autohome:
            self.home()

        if autophase:
            self.autophase()

        if scale_factor == "auto":
            scale_factor = self.scale_factor

        elif not scale_factor:
            scale_factor = self.get_scale_factor()

        start = time.time()
        data = daq.read(duration, rate)
        return Tombstone(data, rate, start=start, scale_factor=scale_factor)

    def get_arw(self, seconds=60, autophase=False, autohome=True,
                scale_factor=None):
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

        data = daq.read(seconds, rate=100)
        _, dev, _, _ = oadev(data*scale_factor, rate=100, data_type='freq',
                             taus=[1])
        return dev[0]/60
