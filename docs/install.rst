Installation
============

End user installation
---------------------

:program:`pip` is your friend here!

If you have it in your path, you can simply use::

    pip install pyimgren

It will take care of any required dependencies and will install the latest
version of pyimgren.
It will also install a :program:`pyimgren` command that will be directly
callable from a shell (:ref:`ref <cmd_line>`).

If ``pip`` is not in your path (common on Windows), you are likely to have
to use the :program:`py`
launcher. In that case you use :program:`pip` as::

    py -m pip install pyimgren

The installation is exactly the same as it is when launching directly
:program:`pip`. But you will have to still use the :program:`py` launcher to
call pyimgren from a command line :ref:`ref <py_launch>`.

Developer installation
-----------------------

The source is of course available in the source package from
`PyPI <https://pypi.org/project/pyimgren/#files>`_.

Alternatively, you can download the full source for the relevant version
as a :file:`.zip` file from GitHub, but the
recommended way is to use Git to clone the repository. It will give you all
the versions in one single operation, as well as a nice environment if you
want  to later send a pull request.

So simply do::

    git clone https://github.com/s-ball/pyimgren.git pyimgren

In any case, you should then install the package in development mode and
ask for the ``test`` extra dependencies::

    pip install -e .[test]

That way you will automatically get the ``pyfakefs`` package which is required
for the integration tests.

.. note::
  The various untagged commits in the Git hierarchy are not guaranteed to be
directly usable. At some points, some tests can fail and unexpected errors can
occur. Use the master branch when you want to contribute. In any other cases,
stick to a release, or be sure to pass all tests and be prepared to look into
the source code if something goes wrong.
