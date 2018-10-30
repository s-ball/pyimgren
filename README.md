[![Travis-CI Build Status](https://travis-ci.com/s-ball/pyimgren.svg?branch=master)](https://travis-ci.com/s-ball/pyimgren) [![AppVeyor Build status](https://ci.appveyor.com/api/projects/status/salqj2q1h8mid74t/branch/master?svg=true)](https://ci.appveyor.com/project/s-ball/pyimgren/branch/master)
[![Documentation Status](https://readthedocs.org/projects/pyimgren/badge/?version=latest)](https://pyimgren.readthedocs.io/en/latest/?badge=latest)

# pyimgren
A python module to rename images according to their exif tags.

## Current status

This package package is distributed in PyPI since version 0.1.0. It can be used by end users, but should be considered at beta quality because it still lacks extensive testing. Its full source is available from [GitHUB](https://github.com/s-ball/pyimgren).

## Goals

Digital cameras name their pictures in a sequential manner. When you want to put pictures from several cameras in the same folder, they will be sorted by camera instead of by picture date and time.

Even if we can find here and there programs that allow for batch renaming of such pictures, I could not find a portable Python module for that. So the goals of this project are:

* few dependencies: a Python 3 (tested for >= 3.3)
* few additional module requirements: only [piexif](https://github.com/hMatoba/Piexif) is required at installation time
* portability: this is a pure Python package and is tested with Travis-CI (linux) and AppVeyor (Windows) for versions 3.3 to 3.6 (3.7 for AppVeyor only).

## Usage:

#### As a Python module

The pyimgren package contains one single class `Renamer` with two public methods: `rename` to rename picture files according to their exif date, and `back` to rename them back to their original names.

A Renamer is used to rename image names provided by a camera
(commonly IMGxxxxx.JPG or DSCFyyyy.JPG into a name based on the time
when the photography had been taken (as smartphones do). That time is
extracted from the exif tag of the picture. No rename occurs if the
picture contains no exif time..

A file named names.log is created in the folder to store the new names
and the original ones, in order to be able to rename them back.

You create a Renamer with: 

 ```
renamer = Renamer(folder, src_mask = "DSCF*.jpg",
                 dst_mask = "%Y%m%d_%H%M%S",
                 ext_mask = ".jpg",
                 ref_file = "names.log",
                 debug = False,
                 dummy = False)
```

Parameters:

* folder: the default folder where pictures will be renamed
* src_mask: a pattern to select the files to be renamed (default
          "DSCF*.jpg")
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
conv.rename()    # to convert to "date" names
...
conv.back()      # if you want to revert to original names
```

#### As a script

The pip installation install a `pyimgren` script (`pyimgren.exe` on Windows) in the Scripts directory. It can then be directly used (provided the Script directory be in the path) with the following syntax:

```
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
```

#### As a module

It can be use as a Python module, which allows to use it in Windows even if the Scripts directory is not in the path thanks to the `py` launcher with same syntax as the script:

```
usage: python -m pyimgren [-h] [-v] [-b] [-s SRC_MASK] [-d DST_MASK]
                [-e EXT_MASK] [-r REF_FILE] [-D] [-X]
                folder [files [files ...]]
```

or when using the Windows launcher `py -m pyimgren ...`

## Installing

### End user installation

With pip: `pip install pyimgren`.

### Developper installation

If you want to contribute or integrate pyimgren in your own code, you should get a copy of the full tree from [GitHUB](https://github.com/s-ball/pyimgren):

```
git clone https://github.com/s-ball/pyimgren [your_working_copy_folder]
```

#### Running the tests

As the project intends to be PyPI compatible, you can simply run tests from the main folder with:

```
python setup.py test
```

The integration tests depend on [pyfakefs](http://pyfakefs.org), which is automatically intalled from PyPI when you run `python setup.py test`. But it is not require for running `pyimgren`, nor installed by `pip install pyimgren`.

## Contributing

As this project is developped on my free time, I cannot guarantee very fast feedbacks. Anyway, I shall be glad to receive issues or pull requests on GitHUB. 

## Versioning

This project uses a standard Major.Minor.Patch versioning pattern. Inside a major version, public API stability is expected (at least after 1.0.0 version will be published).

## License

This project is licensed under the MIT License - see the LICENSE.txt file for details

## Acknowledgments

* The hard job of exif data processing was already done in [piexif](https://github.com/hMatoba/Piexif)
* The excellent [pyfakefs](http://pyfakefs.org), allows integration tests to run on a fake file system
