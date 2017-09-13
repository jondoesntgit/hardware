from hardware import *
from allantools import oadev
import time
from numpy import floor, mean, cos, pi
from pyfog import Tombstone
import json
import re

class Gyro:

    def __init__(self, filepath):
        with open(filepath) as gyro_file:
            string = ""
            
            # Strip any comments
            for line in gyro_file:
                string += re.sub('//.*', '', line)
            data = json.loads(string)

            if 'name' in data:
                self.name = data['name']
            if 'length' in data:
                self.length = data['length']
            if 'pitch' in data:
                self.pitch = data['pitch']
            if 'diameter' in data:
                self.diameter = data['diameter']
                self.radius = data['diameter'] / 2
            if 'radius' in data:
                self.diameter = data['radius'] * 2
                self.radius = data['radius']

    def home(self):
        rot.angle = 0

    def autophase(self):
        tmp_sensitivity = lia.sensitivity
        lia.sensitivity = .03
        start_angle = rot.angle
        rot.ccw(2, background=True)
        time.sleep(.5)
        lia.autophase()
        lia.sensitivity = tmp_sensitivity
        rot.wait_until_motor_is_idle()
        rot.angle = start_angle

    def get_scale_factor(self, sensitivity = .3, pitch=37.4):
        """A python port of Jacob Chamoun's matlab script"""

        # set sensitivity and store current sensitivity
        cal_sensitivity = lia.sensitivity
        lia.sensitivity = sensitivity

        # set the integration time and filter slope and store the current integration
        cal_integration_time = lia.time_constant
        lia.time_constant = 0.01

        cal_velocity = rot.velocity
        rot.velocity = 1

        # set the acquisition rate
        cal_acquisition_rate = floor(1/cal_integration_time)

        # start acquisition and store the calibrated data
        rot.ccw(5, background=True)
        time.sleep(1)
        ccw_data = daq.read(seconds=3, verbose=False)
        time.sleep(2)

        rot.cw(5, background=True)
        time.sleep(1)
        cw_data = daq.read(seconds=3, verbose=False)
        time.sleep(2)

        lia.time_constant = cal_integration_time
        lia.sensitivity = cal_sensitivity
        rot.velocity = cal_velocity

        volt_seconds_per_degree = (mean(ccw_data) - mean(cw_data))/2/cos(pitch * pi / 180)
        volt_hours_per_degree = volt_seconds_per_degree / 3600
        degrees_per_hour_per_volt = 1 / volt_hours_per_degree
        return degrees_per_hour_per_volt


    def tombstone(self, seconds=None, minutes=None, hours=None, rate=10, autophase=False, autohome=True, scale_factor = 0):

        duration = 0
        if seconds:
            duration += seconds
        if minutes:
            duration += minutes * 60
        if hours:
            duration += hours * 3600

        if not time:
            raise ValueException("Cannot test for 0 seconds.")

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


    def get_arw(self, seconds=60, autophase=False, autohome=True, scale_factor=None):
        if not scale_factor:
            scale_factor = self.get_scale_factor()

        data = daq.read(seconds, rate=100)
        _, dev, _, _ = oadev(data*scale_factor, rate=100, data_type='freq', taus=[1])
        return dev[0]/60


