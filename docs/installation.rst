python

.. code:: python

   >>> import numpy
   >>> numpy.__file__
   ‘/Users/wheelerj/miniconda3/lib/python3.5/site-packages/numpy/‘


.. code:: bash

   $ cd /Users/wheelerj/miniconda3/lib/python3.5/site-packages/
   $ ln -s /Users/wheelerj/Dropbox/digonnet/hardware hardware

The reason why ``hardware`` is repeated twice is because of the directory file structure. The github repository ``hardware`` contains a folder for documentation and a folder for the actual python package. When creating a symbolic link, you need to link to this directory.

::

   hardware/
   ├── LICENSE.md
   ├── README.md
   ├── docs
   │   ├── Makefile
   │   ├── conf.py
   │   ├── index.rst
   │   ├── make.bat
   │   └── modules
   │       ├── data_acquisition_units.rst
   │       ├── function_generators.rst
   │       ├── gyros.rst
   │       ├── laser_diode_drivers.rst
   │       ├── lock_in_amplifiers.rst
   │       ├── optical_power_meters.rst
   │       ├── oscilloscopes.rst
   │       ├── rotation_stages.rst
   │       └── spectrum_analyzers.rst
   └── hardware
       ├── __init__.py
       ├── data_acquisition_units.py
       ├── function_generators.py
       ├── gyros.py
       ├── laser_diode_drivers.py
       ├── lock_in_amplifiers.py
       ├── optical_power_meters.py
       ├── oscilloscopes.py
       ├── rotation_stages.py
       └── spectrum_analyzers.py
       
