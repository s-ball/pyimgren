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
        self.setUpPyfakefs()
        self.fs.add_real_directory(os.path.dirname(__file__),
                                   target_path = '/orig')
        self.fs.create_dir('/test')
        self.ren = Renamer('/test')
        
    def test_orig(self):
        self.assertTrue(os.path.exists('/orig/DSCF9762.JPG'))
        

    def test_simple_rename(self):
        shutil.copyfile('/orig/DSCF9762.JPG', '/test/foo')
        self.ren.rename('foo')
        self.assertFalse(os.path.exists('/test/foo'))
        self.assertTrue(os.path.exists('/test/names.log'))
        with open('/test/names.log') as fd:
            names = self.ren._load_names()
        self.assertEqual(list(names.values()), ['foo'])
        new_name = list(names.keys())[0]
        self.assertTrue(os.path.exists(os.path.join('/test', new_name)))

    def test_simple_back(self):
        shutil.copyfile('/orig/DSCF9762.JPG', '/test/foo')
        self.ren.rename('foo')
        with open('/test/names.log') as fd:
            names = self.ren._load_names()
        new_name = list(names.keys())[0]
        self.ren.back()
        self.assertTrue(os.path.exists('/test/foo'))

    def test_dir_rename(self):
        self.fs.create_dir('/test/sub')
        shutil.copyfile('/orig/DSCF9762.JPG', '/test/DSCF9762.jpg')
        shutil.copyfile('/orig/DSCF9762.JPG', '/test/sub/DSCF9762.jpg')
        self.ren.rename('sub')
        self.assertTrue(os.path.exists('/test/DSCF9762.jpg'))
        self.assertFalse(os.path.exists('/test/sub/DSCF9762.jpg'))
        self.assertTrue(os.path.exists('/test/sub/names.log'))
        self.assertFalse(os.path.exists('/test/names.log'))

    def test_dir_back(self):
        self.fs.create_dir('/test/sub')
        shutil.copyfile('/orig/DSCF9762.JPG', '/test/DSCF9762.jpg')
        shutil.copyfile('/orig/DSCF9762.JPG', '/test/sub/DSCF9762.jpg')
        self.ren.rename('sub')
        self.ren.back('sub')
        self.assertTrue(os.path.exists('/test/DSCF9762.jpg'))
        self.assertTrue(os.path.exists('/test/sub/DSCF9762.jpg'))
        self.assertTrue(os.path.exists('/test/sub/names.log'))
        self.assertFalse(os.path.exists('/test/names.log'))


    def test_common_timestamp(self):
        shutil.copyfile('/orig/DSCF9762.JPG', '/test/foo')
        shutil.copyfile('/orig/DSCF9762.JPG', '/test/bar')
        shutil.copyfile('/orig/DSCF9762.JPG', '/test/fee')
        self.ren.rename('foo', 'bar')
        self.assertTrue(os.path.exists('/test/fee'))
        self.assertFalse(os.path.exists('/test/foo'))
        self.assertFalse(os.path.exists('/test/bar'))
        names = self.ren._load_names()
        new_names = sorted(names.keys())
        self.assertEqual(new_names[1][:-4], new_names[0][:-4] + 'a')

if __name__ == "__main__":
    import unittest
    unittest.main(verbosity = 2)
