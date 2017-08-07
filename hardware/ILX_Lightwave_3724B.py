import visa

class ILX_Lightwave_3724B():
    def __init__(self, visa_search_term):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)

    @property
    def current(self):
	    return float(self.inst.query('LAS:LDI?')[:-1])

    @current.setter
    def current(self, val):
	    self.inst.write('LAS:LDI %f' % val)