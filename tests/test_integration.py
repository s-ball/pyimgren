from pyfakefs.fake_filesystem_unittest import TestCase
import os.path
import shutil

import sys
parent = os.path.dirname(os.path.dirname(__file__))
if parent not in sys.path:
    sys.path.append(parent)

from pyimgren import Renamer

class SimpleTest(TestCase):
    def setUp(self):
        """Initialize a Renamer in /test (in a fake file system).
Import current directory in /orig to have a known image in DSCF9762.JPG"""
        self.setUpPyfakefs()
        self.fs.add_real_directory(os.path.dirname(__file__),
                                   target_path = "/orig")
        self.fs.create_dir("/test")
        self.ren = Renamer("/test")
        
    def test_orig(self):
        """Control existance of the known jpeg image in /orig"""
        self.assertTrue(os.path.exists("/orig/DSCF9762.JPG"))
        

    def test_simple_rename(self):
        """Rename a single file by giving its name and control:
    * that the original file name has disappared
    * that names.log has received the expected values
"""
        shutil.copyfile("/orig/DSCF9762.JPG", "/test/foo")
        self.ren.rename("foo")
        self.assertFalse(os.path.exists("/test/foo"))
        self.assertTrue(os.path.exists("/test/names.log"))
        with open("/test/names.log") as fd:
            names = self.ren.load_names()
        self.assertEqual(list(names.values()), ["foo"])
        new_name = list(names.keys())[0]
        self.assertTrue(os.path.exists(os.path.join("/test", new_name)))

    def test_simple_back(self):
        """Rename a single file (by its name), rename back and controls that
the file is actually back"""
        shutil.copyfile("/orig/DSCF9762.JPG", "/test/foo")
        self.ren.rename("foo")
        with open("/test/names.log") as fd:
            names = self.ren.load_names()
        new_name = list(names.keys())[0]
        self.ren.back()
        self.assertTrue(os.path.exists("/test/foo"))

    def test_dir_rename(self):
        """Call rename on a subdir and controls that:
   * the main folder was not touched
   * the rename occured in the sub folder"""
        self.fs.create_dir("/test/sub")
        shutil.copyfile("/orig/DSCF9762.JPG", "/test/DSCF9762.jpg")
        shutil.copyfile("/orig/DSCF9762.JPG", "/test/sub/DSCF9762.jpg")
        self.ren.rename("sub")
        self.assertTrue(os.path.exists("/test/DSCF9762.jpg"))
        self.assertFalse(os.path.exists("/test/sub/DSCF9762.jpg"))
        self.assertTrue(os.path.exists("/test/sub/names.log"))
        self.assertFalse(os.path.exists("/test/names.log"))

    def test_dir_back(self):
        """Call rename then back on a subfolder and controls that the image
file is back in the sub folder"""
        self.fs.create_dir("/test/sub")
        shutil.copyfile("/orig/DSCF9762.JPG", "/test/DSCF9762.jpg")
        shutil.copyfile("/orig/DSCF9762.JPG", "/test/sub/DSCF9762.jpg")
        self.ren.rename("sub")
        self.ren.back("sub")
        self.assertTrue(os.path.exists("/test/DSCF9762.jpg"))
        self.assertTrue(os.path.exists("/test/sub/DSCF9762.jpg"))
        self.assertTrue(os.path.exists("/test/sub/names.log"))
        self.assertFalse(os.path.exists("/test/names.log"))


    def test_common_timestamp(self):
        """Rename many files having same timestamp and control the names they
receive"""
        shutil.copyfile("/orig/DSCF9762.JPG", "/test/foo")
        shutil.copyfile("/orig/DSCF9762.JPG", "/test/bar")
        shutil.copyfile("/orig/DSCF9762.JPG", "/test/fee")
        self.ren.rename("foo", "bar")
        self.assertTrue(os.path.exists("/test/fee"))
        self.assertFalse(os.path.exists("/test/foo"))
        self.assertFalse(os.path.exists("/test/bar"))
        names = self.ren.load_names()
        new_names = sorted(names.keys())
        self.assertEqual(new_names[1][:-4], new_names[0][:-4] + "a")


class MergeTest(TestCase):
    """Tests for the merge feature."""

    def setUp(self):
        self.setUpPyfakefs()
        self.fs.add_real_directory(os.path.dirname(__file__),
                                   target_path = "/orig")
        self.fs.create_dir("/test")
        self.ren = Renamer("/test")
        self.fs.create_dir("/src")

    def test_simple_merge(self):
        """Merge a single file by giving its name and control that:
            * the original file not been touched
            * no names.log was created
            * a new file exists in /test
        """
        shutil.copyfile("/orig/DSCF9762.JPG", "/src/foo")
        self.ren.merge("/src", "foo")
        self.assertTrue(os.path.exists("/src/foo"))
        self.assertFalse(os.path.exists("/test/names.log"))
        files = os.listdir("/test")
        self.assertEqual(1, len(files))

    def test_multiple_merge(self):
        """Merge 2 files with the same exif timestamp.

        Controls that second has same base name than first one + 'a'
        """
        shutil.copyfile("/orig/DSCF9762.JPG", "/src/foo")
        shutil.copyfile("/orig/DSCF9762.JPG", "/src/bar")
        self.ren.merge("/src", "foo", "bar")
        files = sorted(os.listdir("/test"))
        self.assertEqual(2, len(files))
        self.assertEqual(files[1][:-4], files[0][:-4] + "a")
    
if __name__ == "__main__":
    import unittest
    unittest.main(verbosity = 2)
