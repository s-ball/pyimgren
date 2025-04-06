[![AppVeyor Build status](https://ci.appveyor.com/api/projects/status/salqj2q1h8mid74t/branch/master?svg=true)](https://ci.appveyor.com/project/s-ball/pyimgren/branch/master)
[![Documentation Status](https://readthedocs.org/projects/pyimgren/badge/?version=latest)](https://pyimgren.readthedocs.io/en/latest/?badge=latest)

# pyimgren
A python module to rename images according to their exif tags.

## Current status

The current 1.0.0 version is the first version to be declared *stable.
It has a correct test coverage, but it still lacks *real world*
tests.

This package  is distributed in [PyPI](https://pypi.org/project/pyimgren/) since version 0.1.0.
Its full source is available from [GitHub](https://github.com/s-ball/pyimgren).

## Goals

Digital cameras name their pictures in a sequential manner. When you want to put
pictures from several cameras in the same folder, they will be sorted by camera
instead of by picture date and time.

Even if we can find here and there programs that allow for batch renaming of
such pictures, I could not find a portable Python module for that. So the
goals of this project are:

* few dependencies: a Python 3 (tested for >= 3.9)
* few additional module requirements: only [piexif](https://github.com/hMatoba/Piexif) and [i18nparse](https://github.com/s-ball/i18nparse)
are required at installation time; [hatch-msgfmt-s-ball](https://github.com/s-ball/hatch-msgfmt-s-ball)
is also required to build a wheel (compiles PO files to MO format)
* portability: this is a pure Python package and is tested with Appveyor
for versions 3.9 to 3.12.

## Localization
The package supports gettext type localization, and provides a French translation.

## Documentation
A more complete documentation (including a French translation) is available on
[ReadTheDocs](https://pyimgren.readthedocs.io/)

## Usage:

#### As a Python module

The pyimgren package contains one single class `Renamer` with three public
methods: `rename` to rename picture files according to their exif date,
`back` to rename them back to their original names, and `merge` to copy images
from another folder again with a name computed from their exif date.

A Renamer is used to rename image names provided by a camera
(commonly IMGxxxxx.JPG or DSCFyyyy.JPG) into a name based on the time
when the photography had been taken (as smartphones do). That time is
extracted from the exif tag of the picture. No rename occurs if the
picture contains no exif time. Optionally, a number of minutes to add to
the exif time can be given to process images from a camera that would
have a wrong time.

A file named names.log is created in the folder to store the new names
and the original ones, in order to be able to rename them back.

You create a Renamer with: 

 ```
renamer = Renamer(folder,
                 dst_mask = "%Y%m%d_%H%M%S",
                 ext_mask = ".jpg",
                 ref_file = "names.log",
                 debug = False,
                 dummy = False)
```

Parameters:

* folder: the default folder where pictures will be renamed
* dst_mask: a format containing strftime formatting directives, that
          will be used for the new name of a picture (default
          "%Y%m%d_%H%M%S")
* ext_mask: the extension of the new name (default ".jpg")
* ref_file: the name of a file that will remember the old names
          (default "names.log")
* debug   : a boolean flag that will cause a line to be printed for
          each rename when true (default False)
* dummy   : a boolean flag that will cause a "dry run", meaning that
          the folder will be scanned, and debug info eventually printed
          but no file will be renamed (default False)
          
Typical use:

```
from pyimgren import Renamer
...
conv = Renamer(path)
conv.rename('IMG*.jpg')    # to convert to "date" names
...
conv.back()                # if you want to revert to original names
```

#### As a script

The pip installation install a `pyimgren` script (`pyimgren.exe` on Windows)
in the Scripts directory. It can then be directly used (provided the Script
directory is in the path) with the following syntax:

```
usage: pyimgren [-h] [-v] [--folder FOLDER] [-d DST_MASK]
                [-e EXT_MASK] [-r REF_FILE] [-D] [-X]
                {rename,back,merge} [-x delta] files [files...]

Rename pictures according to their exif timestamp

positional arguments:
  {rename,back,merge}   sub-commands
    rename              rename files by using their exif timestamp
    back                rename files back to their original name
    merge               merge files from a different folder
  files                 paths of the files, may contain wildchars (? and *)

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --folder FOLDER, -f FOLDER
                        folder containing files to rename
  -d DST_MASK, --dst_mask DST_MASK
                        format for the new file name
  -e EXT_MASK, --ext EXT_MASK
                        extension for the new file name
  -r REF_FILE, --ref_file REF_FILE
                        a file to remember the old names
  -D, --debug           print a line per rename
  -X, --dry_run         process normally except no rename occurs
```

The sub commands have the following syntax:

```
usage: pyimgren [global_options ...] {back|rename}
            [-h] [-x delta] [-D] [-X] files [files ...]

positional arguments:
  files       files to process (default: content of ref_file)

options:
  -h, --help  show this help message and exit
  -x delta, --delta delta
                        minutes to add to the exif tag time
  -D, --debug           print a line per rename
  -X, --dry_run         process normally except no rename occurs
```

and

```
usage: pyimgren [global_options ...] merge [-h] -s folder files [files ...]

positional arguments:
  files       files to process (default: src_mask)

options:
  -h, --help           show this help message and exit
  -s folder            folder from where merge picture files
  -x delta, --delta delta
                        minutes to add to the exif tag time
  -D, --debug           print a line per rename
  -X, --dry_run         process normally except no rename occurs
```

#### As a module

It can be used as a Python module, which allows to use it in Windows even
if the Scripts directory is not in the path thanks to the `py` launcher
with same syntax as the script:

```
usage: python -m pyimgren same_arguments...

```

or when using the Windows launcher `py -m pyimgren ...`

## Installing

### End user installation

With pip: `pip install pyimgren`.

### Developer installation

If you want to contribute or integrate pyimgren in your own code, you should
get a copy of the full tree from [GitHub](https://github.com/s-ball/pyimgren):

```
git clone https://github.com/s-ball/pyimgren [your_working_copy_folder]
```

#### Running the tests

As the project intends to be PyPI compatible, you can simply run tests from
the main folder with:

```
pytest tests
```
or (if you use `hatch`)

```commandline
hatch test
```

The integration tests depend on [pyfakefs](http://pyfakefs.org), which is automatically
installed from PyPI when you run `hatch test`. But as it is not required for
running `pyimgren`, nor installed by `pip install pyimgren`, you should
use `pip install .[test]` from the cloned directory to safely use `pytest test`
or `python -m unittest`

## Contributing

As this project is developed on my free time, I cannot guarantee very fast
feedbacks. Anyway, I shall be glad to receive issues or pull requests on GitHUB. 

## Versioning

This project uses a standard Major.Minor.Patch versioning pattern. Inside a
major version, public API stability is expected (at least after 1.0.0
version will be published).

## License

This project is licensed under the MIT License - see the LICENSE.txt file
for details

## Acknowledgments

* The hard job of exif data processing was already done in [piexif](https://github.com/hMatoba/Piexif)
* The excellent [pyfakefs](http://pyfakefs.org), allows integration tests to run on a
fake file system
