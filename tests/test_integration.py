#  SPDX-FileCopyrightText: 2025-present s-ball <s-ball@laposte.net>
#  #
#  SPDX-License-Identifier: MIT

import os.path
import shutil
import sys

from pyfakefs.fake_filesystem_unittest import TestCase

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
                                   target_path="/orig")
        self.fs.create_dir("/test")
        self.ren = Renamer("/test")
        
    def test_orig(self):
        """Control existence of the known jpeg image in /orig"""
        self.assertTrue(os.path.exists("/orig/DSCF9762.JPG"))

    def test_simple_rename(self):
        """Rename a single file by giving its name and control:
    * that the original file name has disappeared
    * that names.log has received the expected values
"""
        shutil.copyfile("/orig/DSCF9762.JPG", "/test/foo")
        self.ren.rename("foo")
        self.assertFalse(os.path.exists("/test/foo"))
        self.assertTrue(os.path.exists("/test/names.log"))
        names = self.ren.load_names()
        self.assertEqual(list(names.values()), ["foo"])
        new_name = list(names.keys())[0]
        self.assertTrue(os.path.exists(os.path.join("/test", new_name)))

    def test_simple_back(self):
        """Rename a single file (by its name), rename back and controls that
the file is actually back"""
        shutil.copyfile("/orig/DSCF9762.JPG", "/test/foo")
        self.ren.rename("foo")
        self.ren.back()
        self.assertTrue(os.path.exists("/test/foo"))

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
                                   target_path="/orig")
        self.fs.create_dir("/test")
        self.ren = Renamer("/test")
        self.fs.create_dir("/src")

    def test_simple_merge(self):
        """Merge a single file by giving its name and control that:
            * the original file not been touched
            * no names.log was created
            * a new file exists in /test along with a names.log
        """
        shutil.copyfile("/orig/DSCF9762.JPG", "/src/foo")
        self.ren.merge("foo", src_folder="/src")
        self.assertTrue(os.path.exists("/src/foo"))
        self.assertTrue(os.path.exists("/test/names.log"))
        new, old = next(iter(self.ren.names.items()))
        self.assertEqual('foo', old)
        self.assertTrue(os.path.exists(os.path.join('/test', new)))
        self.assertTrue(os.path.exists(os.path.join('/test', 'names.log')))
        files = os.listdir("/test")
        self.assertEqual(2, len(files))

    def test_multiple_merge(self):
        """Merge 2 files with the same exif timestamp.

        Controls that second has same base name than first one + 'a'
        """
        shutil.copyfile("/orig/DSCF9762.JPG", "/src/foo")
        shutil.copyfile("/orig/DSCF9762.JPG", "/src/bar")
        self.ren.merge("foo", "bar", src_folder="/src")
        files = sorted(os.listdir("/test"))
        self.assertEqual(3, len(files))
        self.assertEqual(files[1][:-4], files[0][:-4] + "a")


class TestMultiRenames(TestCase):
    """
    Test renaming of files already present in the ref file.

    When a file has already an original name, and a different delta is used,
    the new name replaces the previous one to point to the original name.
    """
    def setUp(self):
        self.setUpPyfakefs()
        self.fs.add_real_directory(os.path.dirname(__file__),
                                   target_path="/orig")
        self.fs.create_dir("/test")
        shutil.copyfile('/orig/DSCF9762.JPG', '/test/DSCF9762.JPG')
        self.ren = Renamer("/test")
        self.ren.rename('DSCF9762.JPG')
        self.new_name = next(iter(self.ren.names.keys()))

    def test_init(self):
        self.assertTrue(os.path.exists('/test/names.log'))
        self.assertEqual(1, len(self.ren.names))
        old = next(iter(self.ren.names.values()))
        self.assertEqual('DSCF9762.JPG', old)

    def test_double(self):
        ren = Renamer('/test')
        ren.rename(self.new_name, delta=2)
        self.assertEqual(1, len(ren.names))
        self.assertFalse(self.new_name in ren.names.keys())
        self.assertTrue('DSCF9762.JPG' in ren.names.values())

    def test_back(self):
        ren = Renamer('/test')
        ren.rename(self.new_name, delta=2)
        ren.back()
        self.assertTrue(os.path.exists('/test/DSCF9762.JPG'))
        self.ren.names = None
        self.ren.load_names()
        # noinspection PyTypeChecker
        self.assertEqual(0, len(self.ren.names))

    def test_delta_2(self):
        ren = Renamer('/test')
        ren.rename('*.jpg', delta = 2)
        self.assertEqual(1, len(ren.names))
        self.assertFalse(os.path.exists(
            os.path.join('/test', self.new_name)))
        ren.back()
        self.assertEqual(0, len(ren.names))
        self.assertTrue(os.path.exists('/test/DSCF9762.JPG'))


class TestMergeOrig(TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.fs.add_real_directory(os.path.dirname(__file__),
                                   target_path="/orig")
        self.fs.create_dir("/test")
        self.fs.create_dir('/test2')
        shutil.copyfile('/orig/DSCF9762.JPG', '/test/DSCF9762.JPG')
        shutil.copyfile('/orig/DSCF9762.JPG', '/test2/DSCF9762.JPG')
        self.ren = Renamer("/test")
        self.ren.rename('DSCF9762.JPG')
        self.new_name = next(iter(self.ren.names.keys()))

    def test_file_is_orig(self):
        self.ren.merge('/test2/*')
        self.assertEqual(2, len(self.ren.names))
        self.assertEqual('DSCF9762.JPG', self.ren.names[self.new_name])


class TestSameName(TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.fs.add_real_directory(os.path.dirname(__file__),
                                   target_path="/orig")
        self.fs.create_dir("/test")
        self.fs.create_dir('/test2')
        shutil.copyfile('/orig/DSCF9762.JPG', '/test2/DSCF9762.JPG')
        ren = Renamer('/test2')
        ren.rename('*.JPG')
        for file in os.listdir('/test2'):
            if file != 'names.log':
                self.new_name = file

    def test_init(self):
        self.assertFalse(os.path.exists('/test2/DSCF9762.JPG'))

    def test_rename(self):
        ren = Renamer('/test2')
        ren.rename(self.new_name)
        self.assertEqual({self.new_name: 'DSCF9762.JPG'}, ren.names)

    def test_merge(self):
        ren = Renamer('/test')
        ren.merge(os.path.join('/test2', self.new_name))
        self.assertTrue(os.path.exists(os.path.join('/test', self.new_name)))
        self.assertEqual(0, len(ren.names))


if __name__ == "__main__":
    import unittest
    unittest.main(verbosity=2)
