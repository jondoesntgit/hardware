import visa
import numpy as np


class Newport_1830_C():
	# TODO: Fix this
    def __init__(self, address):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(address)

    def identify(self):
        return self.inst.query('*IDN?')[:-1]

    @property
    def power(self):
    	return float(self.inst.query('D?')[:-1])