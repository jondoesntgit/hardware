import visa, pyvisa  # TODO: perhaps we should try to consolodate thise...
import sys
import os
from pint import _DEFAULT_REGISTRY
import logging
import datetime

logger = logging.getLogger(__name__)

u = _DEFAULT_REGISTRY
Q_ = u.Quantity

# use a+ instead to append to the file - useful for tracking settings over the
# course of several measurements

log_filename = datetime.datetime.today().strftime("%y%m%d.log")
log_file = open(log_filename, 'a')
with log_file:
    # load the logging capabilities
    logging.basicConfig(
        filename=log_filename,
        filemode="a+",
        format='%(asctime)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)

# Load the rotation stage if the hostname environment variable is set

if os.getenv('ROTATION_STAGE_SERVER'):
    from .rotation_stages import NSC_A1
    rot = NSC_A1(hostname=os.getenv('ROTATION_STAGE_SERVER'))
    logger.info('rot = %s' % rot.identify())


# see what's on the bus

resources_dict = dict()

try:
    rm = visa.ResourceManager()
    for resource in rm.list_resources():
        try:
            # Avoid serial devices...
            # They cause some bugs...
            if 'ASRL' in resource:
                continue
            inst = rm.open_resource(resource)
            idn = inst.query('*IDN?')
            resources_dict[idn] = resource
        except pyvisa.errors.VisaIOError:
            # Couldn't open...
            pass

except OSError:
    # Visa not installed on this system
    pass

# Load the modules for which we have matches on the bus
idn = 'Agilent Technologies,33250A,0,2.01-1.01-2.00-03-2\n'
if idn in resources_dict.keys():
    from .function_generators import Agilent_33250A
    awg = Agilent_33250A(resources_dict[idn])
    logger.info('awg = %s' % idn[:-1])

idn = 'HEWLETT-PACKARD,33120A,0,7.0-5.0-1.0\n'
if idn in resources_dict.keys():
    from .function_generators import HP_33120A
    awg = HP_33120A(resources_dict[idn])
    logger.info('awg = %s' % idn[:-1])

idn = 'ILX Lightwave,3724B,37243817,4.8\n'
if idn in resources_dict.keys():
    from .laser_diode_drivers import ILX_Lightwave_3724B
    ldd = ILX_Lightwave_3724B(resources_dict[idn])
    logger.info('ldd = %s' % idn[:-1])


idn = 'StanfordResearchSystems,DS345,31802,1.04\n'
if idn in resources_dict.keys():
    from .function_generators import SRS_DS345
    awg2 = SRS_DS345(resources_dict[idn])
    logger.info('awg2 = %s' % idn[:-1])


idn = 'Stanford_Research_Systems,SR844,s/n48713,ver1.006\n'
if idn in resources_dict.keys():
    from .lock_in_amplifiers import SRS_SR844
    lia = SRS_SR844(resources_dict[idn])
    logger.info('lia = %s' % idn[:-1])

idn = 'Stanford_Research_Systems,SR844,s/n43595,ver1.006\n'
if idn in resources_dict.keys():
    from .lock_in_amplifiers import SRS_SR844
    lia = SRS_SR844(resources_dict[idn])
    logger.info('lia = %s' % idn[:-1])


idn = 'ANDO,AQ6317B,00113576,MR02.10  OR02.07\r\n'
if idn in resources_dict.keys():
    from .spectrum_analyzers import ANDO_AQ6317B
    osa = ANDO_AQ6317B(resources_dict[idn])
    logger.info('osa = %s' % idn[:-2])

idn = 'Agilent Technologies,DSO1024A,CN50138128,00.04.06\n'
if idn in resources_dict.keys():
    from .oscilloscopes import Agilent_DSO1024A
    osc = Agilent_DSO1024A(resources_dict[idn])
    logger.info('osc = %s' % idn[:-1])

idn = 'Rohde&Schwarz,FSEA 20,847121/025,3.30\n'
if idn in resources_dict.keys():
    from .spectrum_analyzers import Rohde_Schwarz_FSEA_20
    rfsa = Rohde_Schwarz_FSEA_20(resources_dict[idn])
    logger.info('rfsa = %s' % idn[:-1])

# TODO
# Load Newport Optical Power Meter
# try:
#    from .optical_power_meters import Newport_1830_C
# except:
#    pass

# Check for DAQ
# TODO
# Run some sort of script to detect if the daq is plugge in
# niDAQmx only available on Windows
if sys.platform.startswith('win'):
    from .data_acquisition_units import NI_9215
    daq = NI_9215()
    logger.info("daq = " + daq.identify())

# Load a Gyro if defined in environment variable
#
# Gyro depends on lia, daq, and rot. Make sure these are defined before fog.
if os.getenv('DEFAULT_GYRO'):
    from .gyros import Gyro
    fog = Gyro(filepath=os.getenv('DEFAULT_GYRO'))
    logger.info('fog = %s' % fog)
