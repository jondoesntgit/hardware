.. Digonnet Hardware documentation master file, created by
   sphinx-quickstart on Sun Sep 17 21:00:29 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Digonnet Hardware's documentation!
=============================================

In order for most of these modules to work, you will need to install the following libaries:

- pyvisa/visa (for most instruments)
- pyserial/serial (for rotation stages)
- pyDAQmx (for NI DAQ units)

For all of the VISA instruments, the GPIB bus address needs to be passed to
the class constructor to initialize an object. The bus address can be found
by a script similar to the following

>>> import visa
>>> rm = visa.ResourceManager()
>>> rm.list_resources()

Several of the most-used instruments in the lab have already been giving names in the ``__init__.py`` file. These default instruments can be loaded into the
main script namespace (as well as other scripts) by running

>>> from hardware import *

.. toctree::
   :maxdepth: 2
   :caption: Modules
   :glob:

   modules/*


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
