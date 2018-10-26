Testing pyimgren
================

The pyimgren package comes with a tests directory that tries to keep the code coverage above 90%.

To use it, you must first clone the repository, then checkout the most relevant version. For example if you want to work with the 0.3.0 release, you could use::

    git clone https://github.com/s-ball/pyimgren.git pyimgren
    cd pyimgren
    git checkout 0.3.0

Then you should run `setup.py test` (referently in a virtual environment) to control that all works fine in your environment::

    python setup.py test

The first time you use it, it may fetch `pyfakefs` from PyPI because it is required for integration tests.
