import visa
import numpy as np


class SRS_DS345():
    def __init__(self, visa_search_term):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)

    def identify(self):
        return self.inst.query('*IDN?')[:-1]

    @property
    def freq(self):
        """Returns frequency in Hz"""

        # get f in kHz
        f = self.inst.query('FREQ?')

        return float(f)

    @freq.setter
    def freq(self, val):
        """Sets frequency in Hz"""
        self.inst.write('FREQ %i' % val)

    # alias
    frequency = freq

    @property
    def volt(self):
        """Returns Vpp in volts"""
        return float(self.inst.query('AMPL?')[:-3])

    @volt.setter
    def volt(self, val):
        """Sets Vpp in volts"""
        self.inst.write('AMPL %f' % val)

    @property
    def phase(self):
        return float(self.inst.query('PHSE?'))

    @phase.setter
    def phase(self, val):
        """Sets phase in degrees"""
        self.inst.write('PHSE %f' % val)

    def upload(self, points_array):
        points_array = np.array(points_array)
        if points_array.dtype not in ['float64', 'int32']:
            raise Exception('Array is not numeric')
        if max(points_array) > 1 or min(points_array) < -1:
            raise Exception('Values should be floats between -1 and +1')
        values = ', '.join(map(str, points_array))
        self.inst.write('DATA VOLATILE, %s' % values)

    def save_as(self, waveform_name):
        self.inst.write('DATA:COPY %s' % waveform_name)

    def upload_as(self, points_array, waveform_name):
        self.upload(points_array)
        self.save_as(waveform_name)
