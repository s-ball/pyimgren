Usage
=====

As a Python module
------------------

Simple usage
************

You only have to import :mod:`pyimgren` and create a :class:`~pyimgren.pyimgren.Renamer`::

    import pyimgren

    ren = pyimgren.Renamer("/path/to_folder")      # use default options here

and that's all...

You can then use the :meth:`~.rename` and :meth:`~.back` methods to rename
pictures forth and back::

    ren.rename("DSC*.JPF")     # rename all files in the folder matching DSCF*.JPG
    ...
    ren.back("20160910*.jpg")  # only rename back pictures taken on 10/09/2016

You can also merge files from a different directory. It makes sense when you
want to pick pictures from another camera::

    ren.merge("IMG*.JPG", src_folder="e:\dcim")

Mid-level usage
***************

All messages from the :mod:`pyimgren` module go through the :mod:`logging`
module. If you want debug messages to be actually printed, you **must**
configure a non default handler processing that level before using
:meth:`~.rename`, :meth:`~.back` and :meth:`~.merge`, methods with a
`debug=True` parameter::

    log = logging.getLogger('pyimgren')
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler())
    ...
    ren.rename("IMG*.JPEG", debug=True)       # ok, debug messages will be printed

Advanced usage
**************

If you want to build a complete front end for :mod:`pyimgren`, you will
probably be interested by the others methods from :class:`~.Renamer` and the
function :func:`~.exif_dat`.

This last one tries its best to extract an exif timestamp from a file and
returns ``None`` if it could not find one. You can use it to easily build a
dictionary ``{file_name: exif_timestamp}`` from a list of picture names::

    dd = { file: exif_dat(file) for file in files }

It is guaranteed to never raise any exception.

The other methods from :class:`~.Renamer`, namely :meth:`~.load_names` and
:meth:`~.get_new_name` respectively load the names of pictures which have been
renamed (both new name and original one), and find what would be the new name
of a file with respect to the ``a`` to ``zz`` suffixes. Examples::

    # build a list of all files in the folder with their original name
    names = ren.load(names).items()

or::

    file_name = ...
    dat = exif_dat(file_name)
    if dat is not None:
        new_name = get_new_name(dat.strftime(ren.dst_mask) + ren.dst_ext)

.. _cmd_line:

From the command line
---------------------

The package provides a command line interface to the :class:`~.Renamer` class.

Syntax:

.. code-block:: none

    usage: pyimgren [-h] [-V] [--folder FOLDER] [-d DST_MASK]
                    [-e EXT_MASK] [-r REF_FILE] [-x DELTA] [-D] [-X]
                    {rename,back,merge} ...

    Rename pictures according to their exif timestamp

    positional arguments:
      {rename,back,merge}   sub-commands
        rename              rename files by using their exif timestamp
        back                rename files back to their original name
        merge               merge files from a different folder

    options:
      -h, --help            show this help message and exit
      -V, --version         show program's version number and exit
      --folder FOLDER, -f FOLDER
                            folder containing files to rename
      -d DST_MASK, --dst_mask DST_MASK
                            format for the new file name
      -e EXT_MASK, --ext EXT_MASK
                            extension for the new file name
      -r REF_FILE, --ref_file REF_FILE
                            a file to remember the old names
      -x DELTA, --delta DELTA
                            number of minutes to add to exif time
      -D, --debug           print a line per rename
      -X, --dry_run         process normally except no rename occurs

and for sub-commands:

.. code-block:: none

    usage: pyimgren {rename|back} [-h] files [files ...]

    positional arguments:
      files       files to process

    options:
      -h, --help  show this help message and exit
or:

.. code-block:: none

    usage: pyimgren merge [-h] [-s SRC_FOLDER] files [files ...]

    positional arguments:
      files                 files to process

    options:
      -h, --help            show this help message and exit
      -s SRC_FOLDER, --src_folder SRC_FOLDER
                            source folder for merging from

This internally starts a :class:`~.Renamer` with the options passed as
parameter. If option ``-D|--debug`` is present a :class:`StreamHandler`
is configured to process Debug level message in the :mod:`logging` module.
Then, the :class:`~.Renamer` runs the method corresponding to the sub-command.

Default values:
***************

All (global) options have default values::

    folder:         current directory (.)
    DST_MASK:       %Y%m%d_%H%M%S
    EXT_MASK:       .jpg
    REF_FILE:       names.log
    delta:          0.0

Options ``debug`` and ``dry_run`` are inactive by default.

.. _py_launch:

Special case
************

On Windows, the Python script directories are commonly not in the PATH,
and users use the :program:`py` launcher to start the interpreter or the
scripts. In that case, the ``pyimgren`` package can be started from the
command line as a module:

.. code-block:: none

        usage: py [version] -m pyimgren [-h] [-V] [--folder FOLDER] [-d DST_MASK]
                        [-e EXT_MASK] [-r REF_FILE] [-x DELTA] [-D] [-X]
                        {rename,back,merge} ...

The parameters are exactly the same they were for the script.
