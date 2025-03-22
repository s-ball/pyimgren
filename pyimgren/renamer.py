"""Implementation of the package"""

# MIT License
# Copyright (c) 2018 s-ball

import collections
import datetime
import gettext
import glob
import io
import itertools
import locale
import logging
import os.path
import os.path
import os.path
import shutil
import sys
from typing import Iterable, Mapping

import piexif

_ = lambda x: x

# a hack to use the new root_dir feature of glob.glob for Python>=3.10
# while still being 3.9 compliant

try:
    glob.glob('a', root_dir='b')
    def genfiles(names: Iterable[str], folder: str):
        for name in names:
            for n in glob.glob(name, root_dir=folder):
                yield n
except TypeError:
    def genfiles(names: Iterable[str], folder: str):
        for name in names:
            for n in glob.glob(os.path.join(folder, name)):
                yield os.path.basename(n)


def nls_init(reset: bool=False) -> str:
    """ Initialize the package for i18n

    Parameters:
        reset: Indicates whether i18n should be setup (if True)
               or removed (if False)

    Returns: the name of the locale currently used by the package
    """
    global _

    if reset:
        _ = lambda x: x
        loc = None
    else:
        if "LANG" in os.environ:
            loc = os.environ["LANG"]
        else:
            loc = locale.getlocale()[0]
            if loc is None:
                try:
                    loc = locale.setlocale(locale.LC_ALL, '')[0]
                except locale.Error:
                    loc = None

        _ = gettext.translation("pyimgren",
                                         os.path.join(os.path.dirname(__file__),
                                                      "locale"),
                                         loc,
                                         fallback=True).gettext
    return loc

class PyimgrenException(Exception):
    """Base for pyimgren exceptions"""


class NamesLogException(PyimgrenException):
    """Raised when a line in the names.log file cannot be parsed

    Attributes:
        numlig: line number where the problem occurs
        line  : content of the offending line
    """
    def __init__(self, numlig: int, line: str):
        self.numlig = numlig
        self.line = line
    def __str__(self):
        return _("Error in name log file line {}: >{}<").format(
            self.numlig, repr(self.line))


class UnknownPictureException(PyimgrenException):
    """Raised when trying to rename back a file not registered in the
    ref_file

    Attributes:
        file    : name of the unknown image
        ref_file: the reference file (names.txt) of the Renamer
        folder  : the (output) folder of the Renamer
    """
    def __init__(self, file: str, renamer: "Renamer"):
        self.file = file
        self.ref_file = renamer.ref_file
        self.folder = renamer.folder
    def __str__(self):
        return "File {} in folder {} not found in {}".format(
            self.file, self.folder, self.ref_file)

class MergeSameDirException(PyimgrenException):
    """Raised when trying to merge one directory into itself.

    Attributes:
        folder: name of the directory
    """
    def __init__(self, folder: str):
        self.folder = folder

    def __str__(self):
        return _("Cannot merge {} into itself").format(self.folder)


class Renamer:
    """Main class of the module.

    A Renamer is used to rename image names provided by a camera
    (commonly IMGxxxxx.JPG or DSCFyyyy.JPG) into a name based on the time
    when the photography had been taken (as smartphones do). That time is
    extracted from the exif tag of the picture. No rename occurs if the
    picture contains no exif time.

    Parameters:
        folder  : the folder where pictures will be renamed
        dst_mask: a format containing strftime formatting directives, that
                  will be used for the new name of a picture (default
                  "%Y%m%d_%H%M%S")
        ext_mask: the extension of the new name
        ref_file: the name of a file that will remember the old names
                  (default names.log)


    All parameters become attribute of the object with the same name

    Attributes:
            delta:    a number of minutes to add to the time found in exif data.
                      This is intended to cope with a camera having a wrong time
                      (default 0)
            debug   : a boolean flag that will cause a line to be printed for
                      each rename when true (default false)
            dummy   : a boolean flag that will cause a "dry run", meaning that
                      the folder will be scanned, and debug info eventually printed
                      but no file will be renamed (default false)
        log: an object respecting a logging.Logger interface. By default,
            ``logging.getLogger("pyimgren")``

    A file named names.log is created in the folder to store the new names
    and the original ones, in order to be able to rename them back.

    Example::

        conv = Renamer(path)
        conv.rename(*files)   # to convert all files from the iterable files to
                              #  "date" names
        conv.back()

    Note:
        This class requires piexif and Python >= 3.
    """

    delta: int
    debug: bool
    dummy: bool
    _orig: set
    _target: set

    def __init__(self, folder,
                 dst_mask = "%Y%m%d_%H%M%S",
                 ext_mask = ".jpg",
                 ref_file = "names.log",
                 ):
        self.folder, self.dst_mask, self.ext_mask, self.ref_file = (
            folder, dst_mask, ext_mask, ref_file)
        self.log = logging.getLogger("pyimgren")
        self.names = None
        self._reset()

    def rename(self, *pictures, delta:int = 0,
               debug: bool=False, dummy:bool=False) -> None:
        """Rename pictures in folder

        Parameters:
            pictures: an iterable of names of files to rename (they must be in the
                Renamer folder). If a name contains
                wildcard characters (* and ?), all
                files matching that pattern will be renamed.
            delta:    a number of minutes to add to the time found in exif data.
                      This is intended to cope with a camera having a wrong time
            debug   : a boolean flag that will cause a line to be printed for
                      each rename when true
            dummy   : a boolean flag that will cause a "dry run", meaning that
                      the folder will be scanned, and debug info eventually printed
                      but no file will be renamed

        Uses load_names to load the names.log file, and get_new_name to avoid
        collisions in file names.

        Raises:
            RuntimeErrorException:
                if for a destination name, all files from a to zz already exist
        """
        self.delta, self.debug, self.dummy = delta, debug, dummy
        names = self.load_names()
        pictures = self._rename_filter(pictures)
        self._process(names, pictures, self.folder, self._move)
        self._save_names()
        self._reset()

    def back(self, *pictures, delta:int = 0,
               debug: bool=False, dummy:bool=False) -> None:
        """Rename pictures back to their initial name in folder
        (by default all pictures known in ref file)

        Parameters:
            pictures: an iterable of names. If one name exists in the local
                ref_file, that file will be renamed back. If it contains
                wildcard characters (* and ?), all files matching that
                pattern will be processed.
            delta:    a number of minutes to add to the time found in exif data.
                      This is intended to cope with a camera having a wrong time
            debug   : a boolean flag that will cause a line to be printed for
                      each rename when true
            dummy   : a boolean flag that will cause a "dry run", meaning that
                      the folder will be scanned, and debug info eventually printed
                      but no file will be renamed

        Uses load_names to load the names.log file.
        """
        self.delta, self.debug, self.dummy = delta, debug, dummy
        names = self.load_names()
        if len(pictures) == 0:
            files = list(names.keys())
        else:
            files = genfiles(pictures, self.folder)
        for file in files:
            try:
                orig = names[os.path.normcase(file)]
            except KeyError:
                self.log.warning(UnknownPictureException(file,self))
                continue
            if self.debug: self.log.debug("%s -> %s", file, orig)
            if not self.dummy:
                try:
                    os.rename(os.path.join(self.folder, file),
                              os.path.join(self.folder, orig))
                    del self.names[file]
                except OSError as e:
                    self.log.warning(_("Could not rename {file} in {folder}",
                                       ).format(file=file, folder = self.folder),
                                     exc_info=e)
        self._save_names()
        self._reset()
                    
    def merge(self, *files, src_folder:str= '.', delta:int = 0,
               debug: bool=False, dummy:bool=False) -> None:
        """Merge files from a different folder.

        Parameters:
            *files: file names or patterns containing wildcard characters (* or?)
                defining the files to be copied.
            src_folder: the name of the folder containing the files to merge.
                It cannot contain wildcard characters.
            delta:    a number of minutes to add to the time found in exif data.
                      This is intended to cope with a camera having a wrong time
            debug   : a boolean flag that will cause a line to be printed for
                      each rename when true
            dummy   : a boolean flag that will cause a "dry run", meaning that
                      the folder will be scanned, and debug info eventually printed
                      but no file will be renamed

        If src_folder is given it is used as a start path component for all
        relative paths in files.

        The files are not moved but remain in their original folder. As usual,
        the copies receive a name based on their exif timestamp encoded by
        strftime using dst_mask and dst_ext.

        If a name matches a directory, the directory is ignored and a warning
        is issued.
        
        Raises:
            RuntimeErrorException:
                if all files from a to zz already exist
        """
        self.delta, self.debug, self.dummy = delta, debug, dummy
        files = self._merge_filter(src_folder, files)
        names = self.load_names()
        self._process(names, files, src_folder, self._copy)
        self._save_names()
        self._reset()

    def load_names(self) -> Mapping[str, str]:
        """Load new and original names from a names.log file.

        Returns:
            OrderedDict:
                the keys of the dict are the new names of the
                renamed pictures and the values are the original names

        Raises:
            NamesLogException:
                the attributes of the NamesLogException are the number
                of the offending line and its content if a line in
                names.log contains no colon (:)
        """
        if self.names is not None:
            return self.names

        names = collections.OrderedDict()
        numlig = 0
        try:
            with io.open(os.path.join(self.folder, self.ref_file),
                         encoding="utf-8") as fd:
                for line in fd:
                    numlig += 1
                    row = [i.strip() for i in line.split(":")[:2]]
                    names[row[0]] = row[1]
        except FileNotFoundError:
            pass
        except IndexError as e:
            raise NamesLogException(numlig,line).with_traceback(
                sys.exc_info()[2]) from e
        self.names = names
        self._target = set(self.names.keys())
        self._orig = set(self.names.values())
        return names

    def _save_names(self):
        if not self.dummy:
            file = os.path.join(self.folder, self.ref_file)
            if len(self.names) == 0:
                if os.path.exists(file):
                    os.remove(file)
            else:
                with io.open(file, "w", encoding="utf-8") as fd:
                    for name, old in self.names.items():
                        fd.write("{}:{}\n".format(os.path.normcase(name),
                                                  old))
            self._target = set(self.names.keys())
            self._orig = set(self.names.values())

    def get_new_name(self, name: str) -> str:
        """Finds the final name of a picture if a file with that name
            already exists.

        Parameters:
            name: the name (without the extension which shall be ext_mask)

        Returns:
            str:
                a name composed with
                    * the value of name
                    * a suffix between a and zz until a file of that name does
                      not exist in the directory
                    * ext_mask

        Raises:
            RuntimeError:
                if all files from a to zz already exist
        """
        return self.get_new_file_name(name + self.ext_mask)

    def get_new_file_name(self, file: str) -> str:
        old_names = set(os.path.normcase(name) for name in itertools.chain(
            self.names.values(), self.names.keys()))
        name, ext = file.split('.') if '.' in file else (file, '')
        if ext != '':
            ext = '.' + ext
        norm_file = os.path.normcase(file)
        if os.path.exists(os.path.join(self.folder, file)) \
                or norm_file in old_names:
            for i in range(ord("a"), ord("z") + 1):
                n = name + chr(i) + ext
                norm_file = os.path.normcase(n)
                if not os.path.exists(os.path.join(self.folder, n)) \
                        and norm_file not in old_names:
                    return n
            for i in range(ord("a"), ord("z") + 1):
                for j in range(ord("a"), ord("z") + 1):
                    n = name + chr(i) + chr(j) + ext
                    norm_file = os.path.normcase(n)
                    if not os.path.exists(os.path.join(self.folder, n)) \
                            and norm_file not in old_names:
                        return n
            raise RuntimeError(_("Too many files for {}").format(
                file))
        return file

    def _process(self, names: Mapping[str, str], pictures: Iterable[str],
                 src_folder: str, file_action):
        """Processing common to rename and merge."""
        for pict in pictures:
            files = glob.glob(os.path.join(src_folder, pict))
            if len(files) == 0:
                self.log.warning(_("{} not found").format(pict))
            else:
                for file in files:
                    if os.path.isdir(file):
                        self._warn_dir(file)
                    else:  # it is a file: must be in folder
                        rel = os.path.basename(file)
                        dat = exif_dat(file)
                        if dat is not None:
                            dat += datetime.timedelta(minutes=self.delta)
                            new_name = dat.strftime(self.dst_mask)
                            # special case: do not try to rename a file with
                            # its original name
                            if (os.path.normcase(new_name + self.ext_mask)
                                    == os.path.normcase(rel)) and (
                                    file_action == self._move):
                                continue
                            new_name = self.get_new_name(
                                dat.strftime(self.dst_mask))
                            if self.debug:
                                self.log.debug("%s -> %s", rel, new_name)
                            if not self.dummy:
                                file_action(file, self.folder, new_name, rel)
        return names

    def _reset(self):
        self.delta = 0
        self.debug = self.dummy = False

    def _warn_dir(self, file: str):
        self.log.warning(_("Merge cannot process %s: is a directory"), file)


    def _move(self, file: str, folder: str, new_name: str, rel: str):
        """Simply rename a file (full path) in a directory (folder)."""
        os.rename(file, os.path.join(folder, new_name))
        new_rel = os.path.normcase(rel)
        if new_rel in self._target:
            new_rel = self.names[rel]
            del self.names[rel]
            rel = new_rel
        elif new_rel in self._orig:
            rel = self.get_new_file_name(rel)
        self.names[new_name] = rel

    def _copy(self, file: str, folder: str, new_name: str, rel: str):
        shutil.copy(file, os.path.join(folder, new_name))
        if os.path.normcase(new_name) != os.path.normcase(rel):
            self.names[new_name] = self.get_new_file_name(rel)

    def _merge_filter(self, src_folder, files: Iterable[str]) -> Iterable[str]:
        def test_path(file, folder):
            if os.path.dirname(os.path.normpath(os.path.abspath(file))) == folder:
                self.log.warning(_('%(file)s in target folder'), {'file': file})
                return False
            return True
        return [file for file in (os.path.join(src_folder, file) for file in files)
                if test_path(file, os.path.normpath(os.path.abspath(self.folder)))]

    def _rename_filter(self, pictures: Iterable[str]) -> Iterable[str]:
        def test_path(file):
            if (os.path.dirname(file) != '' and
                    os.path.relpath(file, self.folder) != os.path.basename(file)):
                self.log.warning('%(file)s not in target folder',
                                 {'file': file})
                return False
            return True
        return [file for file in pictures if test_path(file)]


def exif_dat(file):
    """Extract the timestamp of a picture file from the exif tags.

    This function is a wrapper around the piexif module to easily find the
    date and time when the picture was taken. It first tries the time when
    the camera took the picture, then the time when the file was writen on
    the memory card.
    
    Parameters:
        file: the name of an image file that shall contain an exif tag

    Returns:
        datetime.datetime:
            the date when the picture was taken or stored by the camera found
            in the exif tag or None if no date could be found.
    """
    try:
        exif = piexif.load(file)["Exif"]
    except ValueError:
        return None
    for i in (0x9003, 0x9004, 0x132):
        dt = exif.get(i)
        if dt is not None: break
    if dt is None: return None
    return datetime.datetime.strptime(dt.decode("ascii"),
                                      "%Y:%m:%d %H:%M:%S")
