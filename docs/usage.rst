Usage
=====

As a Python module
------------------

Simple usage
************

You only have to import :mod:`pyimgren` and create a :class:`~.Renamer`::

    import pyimgren

    ren = pyimgren.Renamer("/path/to_folder")      # use default options here

and that's all...

You can then use the :meth:`~.rename` and :meth:`~.back` methods to rename pictures forth and back::

    ren.rename()      # rename all files in the folder matching DSCF*.JPG
    ...
    ren.back("20160910*.jpg")  # only rename back pictures taken on 10/09/2016

Advanced usage
**************

All messages from the :mod:`pyimgren` module go through the `logging` module. If you want debug messages to be actually printed, you **must** configure a non default handler processing that level before using :meth:`~.rename` and :meth:`~.back` methods with a `debug=True` parameter::

    log = logging.getLogger('pyimgren')
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler())
    ...
    ren.rename(debug=True)           # ok, debug messages will be printed

You can automatically process sub folders. If `thumbnails` is a subfolder of the current folder, you can use::

    ren.rename("thumbnails")

This will automatically start a new :class:`~.Renamer` in `thumbnails` with the exact same options as `ren` and call :meth:`~.rename` on it. But **beware**:

* this will process all files matching the `src_mask` parameter of `ren`
* this will create a `names.log` file (or more exactly a file for which the name is the value of the `ref_file` parameter) in the `thumbnails` directory.

Long story made short, it can make sense and is actually used in the command line interface, but it does not allow to process folders that are not descendant from the `ren` folder, nor to specify a limited list of files.

.. _cmd_line:

From the command line
---------------------

The package provides a command line interface to the :class:`~.Renamer` class.

Syntax:

.. code-block:: none

    usage: pyimgren [-h] [-v] [-b] [-s SRC_MASK] [-d DST_MASK] [-e EXT_MASK]
                    [-r REF_FILE] [-D] [-X]
                    folder [files [files ...]]

    Rename pictures according to their exif timestamp

    positional arguments:
      folder                folder containing files to rename
      files                 files of sub folders to process (optional)

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -b, --back            restore original names
      -s SRC_MASK, --src_mask SRC_MASK
                            pattern to select the files to rename
      -d DST_MASK, --dst_mask DST_MASK
                            format for the new file name
      -e EXT_MASK, --ext EXT_MASK
                            extension for the new file name
      -r REF_FILE, --ref_file REF_FILE
                            a file to remember the old names
      -D, --debug           print a line per rename
      -X, --dry_run         process normally except no rename occurs

This internally starts a :class:`~.Renamer` with the options passed as parameter. If option `-D|--debug` is present a `StreamHandler` is configured to process Debug level message in the `logging` module. Then, the :class:`~.Renamer` runs its :meth:`rename` method if the `-b|--back` option is not present, else the :meth:`back` method.

.. _py_launch:

Special case
************

On Windows, the Python script directories are commonly not in the PATH, and users use the `py` launcher to start the interpretor or the scripts. In that case, the `pyimgren` package can be started from the command line as a module:

.. code-block:: none

    usage: py [py options] -m pyimgren [-h] [-v] [-b] [-s SRC_MASK]
                    [-d DST_MASK] [-e EXT_MASK] [-r REF_FILE] [-D] [-X]
                    folder [files [files ...]]

The parameters are exactly the same they were for the script.
