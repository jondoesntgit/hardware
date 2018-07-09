from setuptools import setup, find_packages
import os
# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name = "hardware",
      version='0.2.0dev',
      author='Jonathan Wheeler',
      author_email='jamwheel@stanford.edu',
      description = (
        "Python hardware wrappers for photonics laboratory instruments."
        ),
      long_description=read('README.md'),
      packages=find_packages(),
      install_requires=['numpy'],
      setup_requires=["pytest-runner"],
      tests_require=["pytest"]
)
