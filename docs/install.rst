Installation
============

End user installation
---------------------

`pip` is your friend here!

If you have it in your path, you can simply use::

    pip install pyimgren

It will take care of any required dependencies and will install the latest version of pyimgren. It will also install a `pyimgren` command that will be directly callable from a shell :ref:`ref <cmd_line>`

If it is not in your path, it is likely that you have to use the `py` launcher. In that case you use `pip` as::

    py -m pip install pyimgren

The installation is exactly the same as it is when launching directly `pip`. But you will have to still use the `py` launcher to call pyimgren from a command line :ref:`ref <py_launch>`.

Developper installation
-----------------------

The source is of course available on `PyPI <https://pypi.org/project/pyimgren/#files>`_. But the tests directory is only available on GitHUB.

Here again, you can download the full source for the relevant version, but the recommended way is to use `git` to clone the repository. It will give you all the versions in one single operation, as well as a nice environment if you want  to later send a pull request.

So simply do::

    git clone https://github.com/s-ball/pyimgren.git pyimgren

Beware: integration tests require `pyfakefs <https://pypi.org/project/pyfakefs>`_. See :doc:`testing` for more.
