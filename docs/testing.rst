Testing pyimgren
================

The :mod:pyimgren package comes with a tests directory that tries to keep the code
coverage above 90%.

To use it, you must first clone the repository, then checkout the most
relevant version. For example if you want to work with the 1.0.0 release,
you could use::

    git clone https://github.com/s-ball/pyimgren.git pyimgren
    cd pyimgren
    git checkout 1.0.0

Then you should run the tests (preferentially in a virtual environment) to
control that all works fine in your environment::

    pip install .[test]       # or pip install -e .[test] for a dev. install
    python -m unittest

The first time you use it, it may fetch `pyfakefs`_ from PyPI because it is
required for integration tests.

.. _pyfakefs: https://pypi.org/project/pyfakefs/