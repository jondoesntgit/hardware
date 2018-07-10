import hardware
from hardware import u
import pint


def test_unit_registry():
    assert type(u) == pint.registry.UnitRegistry
    
def test_ldd():
    ldd = hardware.ILX_Lightwave_3724B()
    assert ldd.current.units == u.milliamp

def test_awg():
    ag = hardware.Agilent_33250A()
    srs = hardware.SRS_DS345()
    hp = hardware.HP_33120A()

    assert ag.frequency.units == u.hertz and ag.volt.units == u.volt and
           srs.frequency.units == u.hertz and srs.volt.units == u.volt and
           hp.frequency.units == u.hertz and srs.volt.units == u.volt

def test_opm():
    opm = hardware.Newport_1830_C()
    assert opm.power.units == u.milliwatt

def test_spectum_analyzer():
    sa = hardware.Rohde_Schwarz_FSEA_20()
    new_center = 10 * u.kilohertz
    new_start = 8 * u.kilohertz
    new_stop = 12 * U.kilohertz

    assert sa.center.units == u.hertz and sa.start.units == u.hertz and
           sa.stop.units == u.hertz and sa.rbw.units == u.hertz and
           sa.vbw.units == u.hertz and sa.time.units == u.second and
           sa.reference.units = u.watt

def test_rot_stage():
    rot = hardware.NSC_A1()

    new_angle = .1 * u.hectodegree
    new_velocity = .2 * u.hectodegree/u.second
    new_max_angle = 20000 * u.millidegree
    new_min_angle = 0 * u.microdegree

    rot.angle = new_angle
    rot.velocity = new_velocity
    rot.max_angle = new_max_angle
    rot.min_angle = new_min_angle

    # rot.angle = .1 * u.hectodegree
    # rot.velocity =  .2 * u.hectodegree/u.second
    # rot.max_angle = 20000 * u.millidegree
    # rot.min_angle = 0 * u.microdegree

    assert rot.angle.units == u.degree and
           rot.velocity.units == u.degree/u.second and
           rot.max_angle.units == u.degree and
           rot.min_angle.units == u.degree

def test_lia():
    lia = hardware.NSC_A1()

    new_phas = 1200 * u.decidegree
    new_time_const = 300 * u.millisecond
    lia.phase = new_phas
    lia.time_constant = new_time_const

    assert lia.phase.units == u.degree amd lia.time_constant.units == u.second
