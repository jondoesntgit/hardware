"""
Rotation Stages
===============

.. module:: rotation_stages

.. moduleauthor:: Jonathan Wheeler <jamwheel@stanford.edu>

This module provides support for connecting to a rotation stage server.
The code for the rotation stage server is hosted in a private repo for 
security via obscurity. A rotation_stage client object can be created by

>>> import hardware
>>> rot = hardware.rotation_stages.NSC_A1(hostname='hostname.stanford.edu')

"""

import requests
import json
import threading


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
        return r.json()['angle']

    @angle.setter
    def angle(self, val):
        requests.get(self.hostname + '/rot/angle/%f' % val)

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