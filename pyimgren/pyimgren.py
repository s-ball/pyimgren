"""Implementation of the package"""

# MIT License
# Copyright (c) 2018 s-ball

import os.path
import glob
import datetime
import piexif
import sys
import collections
import io
import logging
import os.path
import shutil

_ = lambda x: x

class PyimgrenException(Exception):
    """Base for pyimgren exceptions"""


class NamesLogException(PyimgrenException):
    """Raised when a line in the names.log file cannot be parsed

    Attributes:
        numlig: line number where the problem occurs
        line  : content of the offending line
    """
    def __init__(self, numlig, line):
        self.numlig = numlig
        self.line = line
    def __str__(self):
        return _("Error in name log file line {}: >{}<").format(
            self.numlig, repr(self.line))


class UnknownPictureException(PyimgrenException):
    """Raised when trying to rename back a file not registered in the
    ref_file

    Attributes:
        file   : name of the unknown image
        renamer: the Renamer object that raised the current error
    """
    def __init__(self, file, renamer):
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
        ren: name of the Renamer folder
    """
    def __init__(self, folder):
        self.folder = folder

    def __str__(self):
        return _("Cannot merge {} into itself").format(self.folder)


class Renamer:
    """Main class of the module.

    A Renamer is used to rename image names provided by a camera
    (commonly IMGxxxxx.JPG or DSCFyyyy.JPG into a name based on the time
    when the photography had been taken (as smartphones do). That time is
    extracted from the exif tag of the picture. No rename occurs if the
    picture contains no exif time..

    Parameters:
        folder  : the folder where pictures will be renamed
        src_mask: a pattern to select the files to be renamed (default
                  "DSCF*.jpg")
        dst_mask: a format containing strftime formatting directives, that
                  will be used for the new name of a picture (default
                  "%Y%m%d_%H%M%S")
        ext_mask: the extension of the new name
        ref_file: the name of a file that will remember the old names
                  (default names.log)
        delta:    a number of minutes to add to the time found in exif data.
                  This is intended to cope with a camera having a wrong time
        debug   : a boolean flag that will cause a line to be printed for
                  each rename when true
        dummy   : a boolean flag that will cause a "dry run", meaning that
                  the folder will be scanned, and debug info eventually printed
                  but no file will be renamed


    All parameters become attribute of the object with the same name

    Attributes:
        log: an object respecting a logging.Logger interface. By default
            ``logging.getLogger("pyimgren")``

    A file named names.log is created in the folder to store the new names
    and the original ones, in order to be able to rename them back.

    Example::

        conv = Renamer(path)
        conv.rename()   # to convert all files with selected pattern to
                        #  "date" names
        conv.back()

    Note:
        This class requires piexif and Python >= 3.
    """
    
    def __init__(self, folder, src_mask = "DSCF*.JPG",
                 dst_mask = "%Y%m%d_%H%M%S",
                 ext_mask = ".jpg",
                 ref_file = "names.log",
                 delta = 0,
                 debug = False,
                 dummy = False):
        self.folder, self.src_mask, self.dst_mask, self.ref_file = (
            folder, src_mask, dst_mask, ref_file)
        self.ext_mask, self.debug, self.dummy = ext_mask, debug, dummy
        self.delta = delta
        self.log = logging.getLogger("pyimgren")
        self.names = None
        
    def rename(self, *pictures):
        """Rename pictures in folder (by default the pictures with the
        src_mask pattern)

        Parameters:
            pictures: an iterable of paths. If a path is a folder, a new Renamer
                is started in that folder with current parameters to rename all
                files matching src_mask. If it is a file (that must be in the
                Renamer folder), that file will be renamed regardless of
                src_mask. If it contains wildcard characters (* and ?), all
                files matching that pattern will berenamed.

        Uses load_names to load the names.log file, and get_new_name to avoid
        collisions in file names.

        Raises:
            RuntimeErrorException:
                if all files from a to zz already exist
        """
        names = self.load_names()
        self._process(names, pictures, self.folder, _move, _subdir)
        if len(names) != 0 and not self.dummy:
            with io.open(
                os.path.join(self.folder, self.ref_file),
                "w", encoding="utf-8") as fd:
                for name, old in names.items():
                    fd.write("{}:{}\n".format(os.path.normcase(name), old))

    def back(self, *pictures):
        """Rename pictures back to their initial name in folder
        (by default all pictures known in ref file)

        Parameters:
            pictures: an iterable of names. If one name exists in the local,
                ref_file, that file will be renamed back. If it contains
                wildcard characters (* and ?), all files matching that
                pattern will be processed.

        Uses load_names to load the names.log file.
        """
        names = self.load_names()
        if len(pictures) == 0:
            files = [os.path.join(self.folder, i) for i in names.keys()]
        else:
            def genfiles():
                for name in pictures:
                    for file in glob.glob(os.path.join(self.folder, name)):
                        yield file
            files = genfiles()
        for file in files:
            if os.path.isdir(file):
                sub = Renamer(file, self.src_mask,
                              self.dst_mask,
                              self.ext_mask,
                              self.ref_file,
                              self.debug,
                              self.dummy)
                sub.log = self.log
                sub.back()
            elif not os.path.exists(file) and file not in pictures:
                continue
            else:  # it is a file: must be in names
                rel = os.path.relpath(file, self.folder)
                try:
                    orig = names[os.path.normcase(rel)]
                except KeyError as e:
                    self.log.warning(UnknownPictureException(rel,self))
                    continue
                if self.debug: self.log.debug("%s -> %s", rel, orig)
                if not self.dummy:
                    os.rename(file, os.path.join(self.folder, orig))
                    del self.names[rel]
        if not self.dummy and os.path.exists(
                os.path.join(self.folder,self.ref_file)):
            self._save_names()
                    
    def merge(self, src_folder, *files):
        """Merge files from a different folder.

        Parameters:
            src_folder: the name of the folder containing the files to merge.
                It cannot contain wildcard characters.
            *files: file names or patterns containing wilcard characters (* or?)
                defining the files to be copied.

        The files are not moved but remain in their original folder. As usual,
        the copies receive a name based on their exif timestamp encoded by
        strftime using dst_mask and dst_ext.

        If a name matches the directory, the directory is ignored and a warning
        is issued.
        
        Raises:
            RuntimeErrorException:
                if all files from a to zz already exist
        """
        if os.path.samefile(self.folder, src_folder):
            raise MergeSameDirException(self.folder)
        names = self.load_names()
        self._process(names, files, src_folder, _copy, _warndir)
    
    def load_names(self):
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
        return names

    def _save_names(self):
        with io.open(
                os.path.join(self.folder, self.ref_file),
                "w", encoding="utf-8") as fd:
            for name, old in self.names.items():
                fd.write("{}:{}\n".format(os.path.normcase(name), old))

    def get_new_name(self, name):
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

    def get_new_file_name(self, file):
        old_names = [os.path.normcase(name) for name in self.names.values()]
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

    def _process(self, names, pictures, src_folder, file_action, dir_action):
        """Processing common to rename and merge."""
        if len(pictures) == 0:
            pictures = [self.src_mask]
        for pict in pictures:
            files = glob.glob(os.path.join(src_folder, pict))
            if len(files) == 0:
                self.log.warning(_("{} not found").format(pict))
            else:
                for file in files:
                    if os.path.isdir(file):
                        dir_action(self, file)
                    else:  # it is a file: must be in folder
                        rel = os.path.relpath(file, src_folder)
                        if rel.startswith(".."):
                            self.log.warning(_("%s is not in %s"), file,
                                           src_folder)
                            continue
                        if os.path.dirname(rel) != "":
                            self.log.warning(_("%s is not directly in %s"),
                                           file, src_folder)
                            continue
                            
                        dat = exif_dat(file)
                        if dat is not None:
                            dat += datetime.timedelta(minutes=self.delta)
                            new_name = self.get_new_name(
                                dat.strftime(self.dst_mask))
                            if self.debug:
                                self.log.debug("%s -> %s", rel, new_name)
                            if not self.dummy:
                                file_action(file, self.folder, new_name,
                                            rel, self)
        return names


def _move(file, folder, new_name, rel, renamer):
    """Simply rename a file (full path) in a directory (folder)."""
    os.rename(file, os.path.join(folder, new_name))
    renamer.names[new_name] = rel


def _subdir(ren, file):
    """Start a copy of a Renamer in a new folder (file)."""
    sub = Renamer(file, ren.src_mask,
                  ren.dst_mask,
                  ren.ext_mask,
                  ren.ref_file,
                  ren.debug,
                  ren.dummy)
    sub.log = ren.log
    sub.rename()


def _copy(file, folder, new_name, rel, renamer):
    shutil.copy(file, os.path.join(folder, new_name))
    renamer.names[new_name] = renamer.get_new_file_name(rel)


def _warndir(ren, file):
    ren.log.warning(_("Merge cannot process {}: is a directory"), file)


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
    dt = None
    for i in (0x9003, 0x9004):
        dt = exif[i]
        if dt is not None: break
    if dt is None: return None
    return datetime.datetime.strptime(dt.decode("ascii"),
                                      "%Y:%m:%d %H:%M:%S")
