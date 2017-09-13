import visa
import serial

# Check Serial
try:
    from .NSC_A1 import *
    rot = NSC_A1()
    print('rot = %s' % rot.identify())
    print('  Rotation platform angle = %.2f' % rot.angle)
except:
    print("Couldn't open rotation stage")



# see what's on the bus
rm = visa.ResourceManager()

resources_dict = dict()

for resource in rm.list_resources():
    try: 
        # Avoid serial devices...
        # They cause some bugs...
        if 'ASRL' in resource:
            continue
        inst = rm.open_resource(resource)
        idn = inst.query('*IDN?')
        resources_dict[idn] = resource
    except:
        # Couldn't open...
        pass

# Load the modules for which we have matches on the bus
idn = 'Agilent Technologies,33250A,0,2.01-1.01-2.00-03-2\n'
if idn in resources_dict.keys():
    from .Agilent_33250A import *
    awg = Agilent_33250A(resources_dict[idn])
    print('awg = %s' % idn[:-1])


idn = 'ILX Lightwave,3724B,37243817,4.8\n'
if idn in resources_dict.keys():
    from .ILX_Lightwave_3724B import *
    ldd = ILX_Lightwave_3724B(resources_dict[idn])
    print('ldd = %s' % idn[:-1])


idn = 'StanfordResearchSystems,DS345,31802,1.04\n'
if idn in resources_dict.keys():
    from .SRS_DS345 import *
    awg2 = SRS_DS345(resources_dict[idn])
    print('awg2 = %s' % idn[:-1])


idn = 'Stanford_Research_Systems,SR844,s/n48713,ver1.006\n'
if idn in resources_dict.keys():
    from .SRS_SR844 import *
    lia = SRS_SR844(resources_dict[idn])
    print('lia = %s' % idn[:-1])


idn = 'ANDO,AQ6317B,00113576,MR02.10  OR02.07\r\n'
if idn in resources_dict.keys():
    from .ANDO_AQ6317B import *
    osa = ANDO_AQ6317B(resources_dict[idn])
    print('osa = %s' % idn[:-2])

idn = 'Agilent Technologies,DSO1024A,CN50138128,00.04.06\n'
if idn in resources_dict.keys():
    from .Agilent_DSO1024A import *
    osc = Agilent_DSO1024A(resources_dict[idn])
    print('osc = %s' % idn[:-1])

# TODO
# Load Newport Optical Power Meter
from .Newport_1830_C import *


# Check for DAQ
# Actually, I don't know how to do this. But it's always plugged in...
if True:
    from .NI_9215 import *
    daq = NI_9215()

from .gyro import *