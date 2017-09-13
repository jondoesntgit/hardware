import visa
from numpy import array, arange
import time

class Agilent_DSO1024A:
    """ ANDO AQ6317B Optical Spectrum Analyzer"""
    def __init__(self, visa_search_term):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)

    def identify(self):
        return self.inst.query('*IDN?')

    def set_timeout(self,milliseconds):
        self.inst.timeout = milliseconds

    def single(self):
        self.inst.write(':SINGLE')

    def run(self):
        self.inst.write(':RUN')

    def stop(self):
        self.inst.write(':STOP')

    def acquire(self, channel=1):
        
        self.inst.write('ACQuire:TYPE NORMAL')
        self.inst.write('SINGLE')
        self.inst.write('WAVeform:SOURce CHAN%i' % channel)
        self.inst.write('WAVeform:FORMat ASCII')
        time.sleep(2)
        
        yref = float(self.inst.query('WAVeform:YREF?'))
        yinc = float(self.inst.query('WAVeform:YINC?'))
        yor = float(self.inst.query('WAVeform:YOR?'))
        
        xinc = float(self.inst.query('WAV:XINC?'))
        xor = float(self.inst.query('WAV:XOR?'))
        
        data = self.inst.query('WAVeform:DATA?')
        #data_values = array([int.from_bytes(val.encode(), 'big') for val in data[12:]])
        data_values = array(data[12:].split(',')).astype(float)
        self.inst.write('RUN')
        
        y = data_values # (yref + data_values) * yinc - yor
        x = xor + (arange(len(y)) * xinc)
        
        return x, y
