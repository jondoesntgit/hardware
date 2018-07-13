from hardware import logger, u, log_file, log_filename
import pint

def test_logging():
    """Ensure that the logging is working loaded."""
    test_string = 'pytest wrote this.'
    logger.info(test_string)
    with open(log_filename) as file:
        assert test_string in file.read()


def test_unit_registry():
    assert type(u) == pint.registry.UnitRegistry
