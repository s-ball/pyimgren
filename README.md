# pyimgren
A python module to rename images according to their exif tags.

## BEWARE: work in progress

This package package is distributed in PyPI since version 1.0.1. It is currently in alpha-level and full source is available from [GitHUB](https://github.com/s-ball/pyimgren).

## Goals

Digital cameras name their picture in a sequential manner. When you want to put pictures from several cameras in the same folder, they will be sorted by camera instead of by picture date and time.

Even if we can find here and there programs that allow for batch renaming of such pictures, I could not find a portable Python module for that. So the goals of this project are:

* few dependencies: a Python 3 (>= 3.2)
* few additional module requirements: only [piexif](https://github.com/hMatoba/Piexif) is required at installation time
* portability: this is a pure Python package and is tested with travis-ci (linux) and AppVeyor (Windows) for versions 3.3 to 3.6 (3.7 for AppVeyor only).

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

Still not implemented...

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

## Contributing

As this project is developped on my free time, I cannot guarantee very fast feedbacks. Anyway, I shall be glad to receive issues or pull requests on GitHUB. 

## Versioning

This project uses a standard Major.Minor.Patch versioning pattern. Inside a major version, public API stability is expected (at least after 1.0.0 version will be published).

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* The hard job of exif data processing was already done in [piexif](https://github.com/hMatoba/Piexif)
