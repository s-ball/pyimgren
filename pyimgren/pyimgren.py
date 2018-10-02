import os.path
import glob
import datetime
import piexif
import csv
import sys
import collections

class Renamer:
    """Parameters:
folder: the default folder where pictures will be renamed
src_mask: a pattern to select the files to be renamed (default
          "DSCF*.jpg")
dst_mask: a format containing strftime formatting directives, that
          will be used for the new name of a picture (default
          "%Y%m%d_%H%M%S")
ext_mask: the extension of the new name
ref_file: the name of a file that will remember the old names
debug   : a boolean flag that will cause a line to be printed for
          each rename when true
dummy   : a boolean flag that will cause a "dry run", meaning that
          the folder will be scanned, and debug info eventually printed
          but no file will be renamed
          
A Renamer is used to rename image names provided by a camera
(commonly IMGxxxxx.JPG or DSCFyyyy.JPG into a name based on the time
when the photography had been taken (as smartphones do). That time is
extracted from the exif tag of the picture. No rename occurs if the
picture contains no exif time..

A file named names.log is created in the folder to store the new names
and the original ones, in order to be able to rename them back.

Typical use:

conv = Renamer(path)
conv.rename()    # to convert to "date" names
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
    def rename(self, folder = None):
        """Rename pictures in folder (by default the folder declared
at Renamer initialization"""
        if folder is None: folder = self.folder
        orig_folder = os.getcwd()
        os.chdir(folder)
        names = self._load_names()
        for file in glob.glob(self.src_mask):
            dat = self._get_dat(file)
            if dat is not None:
                new_name = self._get_new_name(
                    datetime.datetime.strftime(dat, self.dst_mask)) \
                     + self.ext_mask
                if self.debug:
                    print(file, "->", new_name, file=sys.stderr)
                names[new_name] = file
                if not self.dummy:
                    os.rename(file, new_name)
        if len(names) != 0:
            with open(self.ref_file, "w", newline='') as fd:
                wr = csv.writer(fd, delimiter = ":")
                for name, old in names.items():
                    wr.writerow((name, old))
        os.chdir(orig_folder)
    def back(self, folder = None):
        """Rename pictures back to their initial name in folder
(by default the folder declared at Renamer initialization)"""
        if folder is None: folder = self.folder
        orig_folder = os.getcwd()
        os.chdir(folder)
        names = self._load_names()
        for name, orig in names.items():
            if self.debug: print(name, "->", orig, file=sys.stderr)
            if not self.dummy: os.rename(name, orig)
        os.chdir(orig_folder)
    def _load_names(self):
        names = collections.OrderedDict()
        try:
            with open(self.ref_file) as fd:
                rd = csv.reader(fd, delimiter=":")
                for numlig, row in enumerate(rd):
                    names[row[0]] = row[1]
        except FileNotFoundError:
            pass
        except IndexError:
            print(numlig, row)
            raise
        return names
    def _get_dat(self, file):
        exif = piexif.load(file)["Exif"]
        dt = None
        for i in (0x9003, 0x9004):
            dt = exif[i]
            if dt is not None: break
        if dt is None: return None
        return datetime.datetime.strptime(dt.decode('ascii'),
                                          "%Y:%m:%d %H:%M:%S")
    def _get_new_name(self, name):
        if os.path.exists(name + self.ext_mask):
            for i in range(ord('a'), ord('z') + 1):
                n = name + chr(i)
                if not os.path.exists(n + self.ext_mask): return n
            for i in range(ord('a'), ord('z') + 1):
                for j in range(ord('a'), ord('z') + 1):
                    n = name + chr(i) + chr(j) + self.ext_mask
                    if not os.path.exist(n): return n
            raise RuntimeError("Too much files for {}".format(
                name + self.ext_mask))
        return name
