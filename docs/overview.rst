Overview
========

Goal
----

Digital cameras name their pictures in a sequential manner. When you want to put pictures from several cameras in the same folder, they will be sorted by camera instead of by picture date and time.

Even if we can find here and there programs that allow for batch renaming of such pictures, I could not find a portable Python module for that. So the goals of this project are:

* few dependencies: a Python 3 (tested for >= 3.3)
* few additional module requirements: only piexif_ and i18nparse_ are required at installation time
* portability: this is a pure Python package and is tested with Travis-CI (linux) and AppVeyor (Windows) for versions 3.3 to 3.6 (3.7 for AppVeyor only).

It is intended to be an importable package that can be included in other Python project, as well as a command line utility that can be launched from a shell.

Features
--------

The central class of the package is :class:`~pyimgren.pyimgren.Renamer`. It normally acts on a single folder passed at initialization time. It should be given a ``strftime`` format string and an extension (starting with a dot like ``.jpg``). It can then:

* rename files from the folder given by their names of by patterns to a name contructed with the date from the exif tag, the ``strftime`` format string and the extension. When more than one file should get the same name, the following are given names postfixed with ``a`` to ``zz`` before the extension.
  For example with a ``"%Y%m%d"`` mask and a ``".jpeg"`` extension, 3 pictures from the 10 september 2016 will be given the names ``"20160910.jpeg"`` and ``"20160910a.jpeg"``. Optionally, you can pass a delta in minutes to add to the time extracted for the exif tag.

* rename back files from the folder to their original names. For that ``rename`` creates a special file in the folder (by default ``names.log``) to record the new and original names. Optionally it can operate on a limited set of the renamed pictures.

* merge files from a different directory. File are directly copied from their original folder with their final name based on their exif timestamp.

Dependencies
------------

This package has few requirements:

* a Python >= 3 (only tested with >= 3.3)
* the piexif_ package available from Pypi and automatically installed in a `pip` installation.
* the i18nparse_ package available from PyPI, and automatically installed too (since 0.6)

Internationalization
--------------------

This package supports gettext type localization, and provides French messages in addition to English.

Limits
------

At this time, there is no GUI interface.

.. _piexif:  https://github.com/hMatoba/Piexif
.. _i18nparse: https://github.com/s-ball/i18nparse
