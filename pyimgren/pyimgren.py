import os.path
import glob
import datetime
import piexif
import sys
import collections
import io
import logging
import os.path

class PyimgrenException(Exception):
    """Base for pyimgren exceptions"""
class NamesLogException(PyimgrenException):
    """Raised when a line in the names.log file cannot be parsed

Attributes:
    numlig: line number where the problem occurs
    line  : content of the offending line"""
    def __init__(self, numlig, line):
        self.numlig = numlig
        self.line = line
    def __str__(self):
        return "Error in name log file line {}: >{}<".format(
            self.numlig, repr(self.line))

class UnknownPictureException(PyimgrenException):
    """Raised when trying to rename back a file not registered in the
ref_file"""
    def __init__(self, file, renamer):
        self.file = file
        self.ref_file = renamer.ref_file
        self.folder = renamer.folder
    def __str__(self):
        return "File {} in folder {} not found in {}".format(
            self.file, self.folder, self.ref_file)

class Renamer:
    """Parameters:
folder  : the folder where pictures will be renamed
src_mask: a pattern to select the files to be renamed (default
          "DSCF*.jpg")
dst_mask: a format containing strftime formatting directives, that
          will be used for the new name of a picture (default
          "%Y%m%d_%H%M%S")
ext_mask: the extension of the new name
ref_file: the name of a file that will remember the old names
         (default names.log)
debug   : a boolean flag that will cause a line to be printed for
          each rename when true
dummy   : a boolean flag that will cause a "dry run", meaning that
          the folder will be scanned, and debug info eventually printed
          but no file will be renamed

All those parameters become attributes of the object.

A Renamer is used to rename image names provided by a camera
(commonly IMGxxxxx.JPG or DSCFyyyy.JPG into a name based on the time
when the photography had been taken (as smartphones do). That time is
extracted from the exif tag of the picture. No rename occurs if the
picture contains no exif time..

A file named names.log is created in the folder to store the new names
and the original ones, in order to be able to rename them back.

Typical use:

conv = Renamer(path)
conv.rename() # to convert all files with selected pattern to "date" names
conv.back()

This class requires piexif and Python >= 3."""
    
    def __init__(self, folder, src_mask = "DSCF*.jpg",
                 dst_mask = "%Y%m%d_%H%M%S",
                 ext_mask = ".jpg",
                 ref_file = "names.log",
                 debug = False,
                 dummy = False):
        self.folder, self.src_mask, self.dst_mask, self.ref_file = (
            folder, src_mask, dst_mask, ref_file)
        self.ext_mask, self.debug, self.dummy = ext_mask, debug, dummy
        self._log = logging.getLogger('pyimgren')
    def rename(self, *pictures):
        """Rename pictures in folder (by default the pictures with the
src_mask pattern)

pictures is an iterable of paths. If a path is a folder, a new Renamer
is started in that folder with current parameters to rename all files
matching src_mask. If it is a file (that must be in the Renamer folder),
that file will be renamed regardless of src_mask. If it contains
wildcard characters (* and ?), all files matching that pattern will be
renamed."""
        names = self._load_names()
        if len(pictures) == 0:
            pictures = [self.src_mask]
        for pict in pictures:
            files = glob.glob(os.path.join(self.folder, pict))
            if len(files) == 0:
                self._log.warning("{} not found".format(pict))
            else:
                for file in files:
                    if os.path.isdir(file):
                        sub = Renamer(file, self.src_mask,
                                      self.dst_mask,
                                      self.ext_mask,
                                      self.ref_file,
                                      self.debug,
                                      self.dummy)
                        sub._log = self._log
                        sub.rename()
                    else:  # it is a file: must be in folder
                        rel = os.path.relpath(file, self.folder)
                        if rel.startswith('..'):
                            self._log.warning("%s is not in %s", file,
                                           self.folder)
                            continue
                        if os.path.dirname(rel) != '':
                            self._log.warning("%s is not directly in %s",
                                           file, self.folder)
                            continue
                            
                        dat = exif_dat(file)
                        if dat is not None:
                            new_name = self._get_new_name(
                                datetime.datetime.strftime(dat, self.dst_mask)) \
                                 + self.ext_mask
                            if self.debug:
                                self._log.debug("%s -> %s", rel, new_name)
                            names[new_name] = rel
                            if not self.dummy:
                                os.rename(file, os.path.join(self.folder,
                                                             new_name))
        if len(names) != 0:
            with io.open(
                os.path.join(self.folder, self.ref_file),
                "w", encoding="utf-8") as fd:
                for name, old in names.items():
                    fd.write(u"{}:{}\n".format(os.path.normcase(name), old))
    def back(self, *pictures):
        """Rename pictures back to their initial name in folder
(by default all pictures known in ref file)

pictures is an iterable of names. If one name exists in the local,
ref_file, that file will be renamed back. If it contains wildcard
characters (* and ?), all files matching that pattern will be
processed."""

        names = self._load_names()
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
                sub._log = self._log
                sub.back()
            else:  # it is a file: must be in names
                rel = os.path.relpath(file, self.folder)
                try:
                    orig = names[os.path.normcase(rel)]
                except KeyError as e:
                    self._log.warning(UnknownPictureException(rel,self))
                    continue
                if self.debug: self._log.debug("%s -> %s", rel, orig)
                if not self.dummy:
                    os.rename(file, os.path.join(self.folder, orig))
    def _load_names(self):
        names = collections.OrderedDict()
        numlig = 0
        try:
            with io.open(os.path.join(self.folder, self.ref_file),
                         encoding='utf-8') as fd:
                for line in fd:
                    numlig += 1
                    row = [i.strip() for i in line.split(u":")[:2]]
                    names[row[0]] = row[1]
        except FileNotFoundError:
            pass
        except IndexError as e:
            raise NamesLogException(numlig,line).with_traceback(
                sys.exc_info()[2]) from e
        return names
    def _get_new_name(self, name):
        if os.path.exists(name + self.ext_mask):
            for i in range(ord('a'), ord('z') + 1):
                n = name + chr(i)
                if not os.path.exists(n + self.ext_mask): return n
            for i in range(ord('a'), ord('z') + 1):
                for j in range(ord('a'), ord('z') + 1):
                    n = name + chr(i) + chr(j) + self.ext_mask
                    if not os.path.exists(n): return n
            raise RuntimeError("Too many files for {}".format(
                name + self.ext_mask))
        return name

def exif_dat(file):
    """Utility function that uses the piexif module to extract the date
and time when the picture was taken from the exif tags"""
    try:
        exif = piexif.load(file)["Exif"]
    except ValueError:
        return None
    dt = None
    for i in (0x9003, 0x9004):
        dt = exif[i]
        if dt is not None: break
    if dt is None: return None
    return datetime.datetime.strptime(dt.decode('ascii'),
                                      "%Y:%m:%d %H:%M:%S")
