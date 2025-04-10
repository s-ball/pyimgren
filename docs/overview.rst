Overview
========

Goal
----

Digital cameras name their pictures in a sequential manner. When you want to
put pictures from several cameras in the same folder, they will be sorted by
camera instead of by picture date and time.

Even if we can find here and there programs that allow for batch renaming of
such pictures, I could not find a portable Python module for that. So the
goals of this project are:

* few dependencies: a Python 3 (tested for Python >= 3.9)
* few additional module requirements: only piexif_ and i18nparse_ are required
  at installation time
* portability: this is a pure Python package and is tested with Appveyor
  (Windows and Linux) for versions 3.9 to 3.13.

It is intended to be an importable package that can be included in other
Python project, as well as a command line utility that can be launched from a
shell.

Features
--------

The central class of the package is :class:`~pyimgren.renamer.Renamer`. It
normally acts on a single folder passed at initialization time. It should be
given a ``strftime`` format string and an extension (starting with a dot like
``.jpg``). It can then:

* rename files from the folder given by their names of by patterns to a name
  constructed with the date from the exif tag, the ``strftime`` format string
  and the extension. When more than one file should get the same name, the
  following are given names suffixed with ``a`` to ``zz`` before the extension.

  For example with a ``"%Y%m%d"`` mask and a ``".jpeg"`` extension, 2 pictures
  from the 10 september 2016 will be given the names ``"20160910.jpeg"`` and
  ``"20160910a.jpeg"``. Optionally, you can pass a delta in minutes to add to
  the time extracted for the exif tag.

* rename back files from the folder to their original names. For that,
  :meth:`~pyimgren.renamer.Renamer.rename` creates a special file in the folder
  (by default :file:`names.log`) to
  record the new and original names. Optionally it can operate on a limited set
  of the renamed pictures.

* merge files from a different directory. The files are directly copied from
  their original folder with their final name based on their exif timestamp.

Dependencies
------------

This package has few requirements:

* a Python >= 3 (only tested with >= 3.9)
* the piexif_ package available from PyPI and automatically installed in a
  `pip` installation.
* the i18nparse_ package available from PyPI, and automatically installed
  too.

Internationalization
--------------------

This package supports gettext type localization, and provides French messages in addition to English.

Limits
------

The upcoming 1.0 version breaks a lot of compatibility with previous ones.

The documentations (both English and French) are still a work in progress...

.. _piexif:  https://github.com/hMatoba/Piexif
.. _i18nparse: https://github.com/s-ball/i18nparse
