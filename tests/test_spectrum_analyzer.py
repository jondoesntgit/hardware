"""Tests for Rohde Rohde_Schwarz_FSEA_20 function generator."""

import pytest

try:
    from hardware import rfsa, u, log_filename
except (NameError, ImportError):
    # spectrum analyzer not connected
    pytestmark = pytest.mark.skip


def test_start():
    """Test that the start frequency is in the right units and is logged."""
    start = rfsa.start
    assert start.units == u.hertz
    rfsa.start = 10 * u.megahertz

    with open(log_filename) as file:
        string = "Start set to %f Hz." % rfsa.start.magnitude
        assert string in file.read()

    rfsa.start = start


def test_stop():
    """Test that the stop frequency is in the right units and is logged."""
    stop = rfsa.stop
    assert stop.units == u.hertz
    rfsa.stop = 14 * u.megahertz

    with open(log_filename) as file:
        string = "Stop set to %f Hz." % rfsa.start.magnitude
        assert string in file.read()

    rfsa.stop = stop


def test_center():
    """Test that the center frequency is in the right units and is logged."""
    center = rfsa.center
    assert center.units == u.hertz
    rfsa.center = 12 * u.megahertz

    with open(log_filename) as file:
        string = "Center set to %f Hz." % rfsa.center.magnitude
        assert string in file.read()

    rfsa.center = center


def test_span():
    """Test that the span is in the right units and is logged"""
    span = rfsa.span
    assert span.units == u.hertz
    rfsa.span = 100 * u.hertz

    with open(log_filename) as file:
        string = "Span set to %f Hz." % rfsa.span.magnitude
        assert string in file.read()

    rfsa.span = span


def test_rbw():
    """Test that the resolution bandwidth is in the right units and is logged."""
    rbw = rfsa.rbw
    assert rbw.units == u.hertz
    rfsa.rbw = 10 * u.kilohertz

    with open(log_filename) as file:
        string = "RBW set to %f Hz." % rfsa.rbw.magnitude
        assert string in file.read()

    # return to initial condition
    rfsa.rbw = rbw


def test_vbw():
    """Test that the bandwidth is in the right units and is logged"""
    vbw = rfsa.vbw
    assert vbw.units == u.hertz
    rfsa.vbw = 10 * u.kilohertz

    with open(log_filename) as file:
        string = "VBW set to %f Hz." % rfsa.vbw.magnitude
        assert string in file.read()

    # return to initial condition
    rfsa.vbw = vbw


def test_time():
    """Test that the time is in the right units and is logged"""
    time = rfsa.time
    assert time.units == u.second
    rfsa.time = 5 * u.second

    with open(log_filename) as file:
        string = "Time set to %f seconds." % rfsa.vbw.magnitude
        assert string in file.read()

    # return to initial condition
    rfsa.time = time
