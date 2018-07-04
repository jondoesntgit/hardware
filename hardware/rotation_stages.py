"""
Rotation Stages
===============

.. module:: rotation_stages

.. moduleauthor:: Jonathan Wheeler <jamwheel@stanford.edu>
.. moduleauthor:: Anjali Thontakudi

This module provides support for connecting to a rotation stage server.
The code for the rotation stage server is hosted in a private repo for
security via obscurity. A rotation_stage client object can be created by

>>> import hardware
>>> rot = hardware.rotation_stages.NSC_A1(hostname='hostname.stanford.edu')

"""

import requests
import json
import threading
from hardware import u
import random

class MockRotationStage:
    def __init__(self, instr_name = None):
        if not instr_name:
            self.name = "Rotation Stage - NSC A1"
        else:
            self.name = instr_name
        self._angle = random.randint(1, 361) * u.degree
        self._velocity = random.randint(1, 10) * u.degree/u.second

    def identify(self):
        return self.name

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value * u.degree

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, val):
        self._velocity = val * u.degree/u.second

    def rotate(self):
        print("Rotating")


class NSC_A1:
    """
    Defines a rotation_stage_client object for communicating with a rotation
    stage server.

    Args:
        hostname (str): The hostname of the server.

    Attributes:
        angle (float): The absolute position of the rotation stage in degrees
        velocity (float): The angular velocity of the rotation stage in degrees/second
    """
    def __init__(self, hostname):
        self.hostname = hostname.rstrip('/')

    @property
    def angle(self):
        r = requests.get(self.hostname + '/rot/angle')
        return r.json()['angle'] * u.degree

    @property
    def velocity(self):
        r = requests.get(self.hostname + '/rot/velocity')
        return r.json()['velocity'] * u.degree/u.second

    @velocity.setter
    def velocity(self, val):
        requests.get(self.hostname + '/rot/velocity/%f' % val)

    @angle.setter
    def angle(self, val):
        requests.get(self.hostname + '/rot/angle/%f' % val)

    def rotate(self, direction, background=False):
        if(direction.lower() == "cw" or direction.lower() == "clockwise"):
            self.cw()
        elif(direction.lower()=="ccw" or direction.lower()== "counterclockwise"):
            self.ccw()

    def cw(self, val, background=False):
        """
        Rotates clockwise through a specified angle.

        Args:
            val (float): The amount to rotate in degrees
            background (bool, optional): If true, runs the rotation in the background
            in order to allow other commands to be executed while the stage rotates.
        """
        if background:
            def worker(url):
                requests.get(url)
            threading.Thread(target=worker, args=(self.hostname + '/rot/cw/%f' % val,)).start()
        else:
            requests.get(self.hostname + '/rot/cw/%f' % val )

    def ccw(self, val, background=False):
        """
        Rotates counterclockwise through a specified angle.

        Args:
            val (float): The amount to rotate in degrees
            background (bool, optional): If true, runs the rotation in the background
            in order to allow other commands to be executed while the stage rotates.
        """
        self.cw(-val, background)
