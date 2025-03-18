#  SPDX-FileCopyrightText: 2025-present s-ball <s-ball@laposte.net>
#  #
#  SPDX-License-Identifier: MIT

import collections
import datetime
import io
import os.path
import unittest
import unittest.mock as mock

import pyimgren


class RenamerTest(unittest.TestCase):
    """Tests for the Renamer class"""
    
    @classmethod
    def setUpClass(cls):
        cls.folder = os.path.dirname(__file__)

    def setUp(self):
        self.obj = pyimgren.Renamer(self.folder)

    def test_load_names_ok(self):
        """Extract a name from a names.log file"""
        with mock.patch("pyimgren.renamer.io.open",
                                 return_value = io.StringIO(u"""a:b
c:d
""")):
            names = self.obj.load_names()
            self.assertEqual(2, len(names.keys()))
            self.assertEqual("b", names["a"])

    def test_load_names_ko(self):
        """Try to extract a name from a broken names.log file"""
        with mock.patch("pyimgren.renamer.io.open",
                                 return_value = io.StringIO("""a:b
c
:d
""")):
            try:
                self.obj.load_names()
            except pyimgren.renamer.NamesLogException as e:
                self.assertEqual(2, e.numlig)
                self.assertEqual("c\n", e.line)
                self.assertTrue(isinstance(str(e), str))
                return
            self.fail("No NamesLogException")

    def test_get_names(self):
        """find a new name pretending 55 files already exist"""
        with mock.patch("os.path.exists",
                        side_effect = ([True] * 55) + [False]):
            self.obj.names = {}
            n = self.obj.get_new_name("foo")
            self.assertEqual(56, os.path.exists.call_count)
            self.assertEqual(os.path.join(self.obj.folder, "foobc")
                             + self.obj.ext_mask,
                             os.path.exists.call_args[0][0])
            self.assertEqual(os.path.join(self.obj.folder, "foo")
                             + self.obj.ext_mask,
                             os.path.exists.call_args_list[0][0][0])
            self.assertEqual(os.path.join(self.obj.folder, "fooa")
                             + self.obj.ext_mask,
                             os.path.exists.call_args_list[1][0][0])
            self.assertEqual("foobc" + self.obj.ext_mask, n)

    def test_back(self):
        """Rename back 3 files"""
        flist = [("a", "b"), ("c", "d"), ("e", "f")]
        with mock.patch("os.rename"), mock.patch(
                "glob.glob", side_effect = [
                    [ os.path.join(self.folder, i)]
                    for i,j in flist]), mock.patch(
                'os.path.exists', return_value=True), mock.patch.object(
                self.obj, '_save_names'):
            self.obj.names = collections.OrderedDict(flist)
            self.obj.back()
            self.assertEqual(3, os.rename.call_count)
            for i, pair in enumerate(flist):
                self.assertEqual(
                    tuple(map(lambda x: os.path.join(self.folder, x),pair)),
                    os.rename.call_args_list[i][0])
            self.assertEqual(0, len(self.obj.names))

    def test_rename(self, delta=0):
        """Rename 4 files"""
        fd = mock.Mock()
        dates = [
            datetime.datetime(2018,2,1),
            datetime.datetime(2018, 3, 1),
            datetime.datetime(2018, 2, 2),
            datetime.datetime(2018, 4, 1)
            ]
        names = [os.path.join(self.folder, i) for i in "abcd"]
        open_ctx = mock.Mock()
        open_ctx.__enter__ = mock.Mock(return_value = fd)
        open_ctx.__exit__ = mock.Mock()
        with mock.patch("os.rename"), \
             mock.patch("io.open", return_value = open_ctx), \
             mock.patch("glob.glob", return_value = names), \
             mock.patch("pyimgren.renamer.exif_dat",
                        side_effect = dates):
            self.obj.names = collections.OrderedDict()
            self.obj._orig = self.obj._target = set()
            self.obj.rename('?', delta=delta)
            dates = [d + datetime.timedelta(minutes=delta)
                     for d in dates]
            for i, n in enumerate(names):
                nn0 = dates[i].strftime(self.obj.dst_mask) + self.obj.ext_mask
                nn = os.path.join(self.folder, nn0)
                self.assertEqual((n, nn), os.rename.call_args_list[i][0])
                self.assertEqual(nn0 + ":" +
                                 os.path.relpath(n, self.folder) + "\n",
                                 fd.write.call_args_list[i][0][0])

    def test_rename_delta(self):
        """Rename files with 60 minutes delta"""
        self.test_rename(delta=60)

    def test_rename_no_exif_tag(self):
        """Try to rename files having no exif tag"""
        fd = mock.Mock()
        names = [os.path.join(self.folder, i) for i in "abcd"]
        open_ctx = mock.Mock()
        open_ctx.__enter__ = mock.Mock(return_value = fd)
        open_ctx.__exit__ = mock.Mock()
        dates = [None] * len(names)
        with mock.patch("os.rename"), \
             mock.patch("io.open", return_value = open_ctx), \
             mock.patch("glob.glob", return_value = names), \
             mock.patch("pyimgren.renamer.exif_dat",
                        side_effect = dates):
            self.obj.names = collections.OrderedDict()
            self.obj.rename()
            os.rename.assert_not_called()
            fd.write.assert_not_called()
            
    def test_rename_dir(self):
        """Try to rename a sub-folder: should warn"""
        abs_folder = os.path.join(self.folder, "sub")
        with mock.patch("os.path.join", return_value=abs_folder), \
             mock.patch("os.path.isdir"), \
             mock.patch("glob.glob", return_value=[abs_folder]), \
             mock.patch.object(self.obj.log, 'warning') as warning:
            self.obj.rename("sub")
            warning.assert_called_once()
            
    def test_unknown_picture(self):
        """Try to rename back a file not known in names.log"""
        with mock.patch("os.path.isdir", return_value = False), \
             mock.patch("os.path.relpath", return_value = "xy"), \
             mock.patch("glob.glob", return_value = ["xy"]), \
             mock.patch.object(self.obj, "log") as log, \
             mock.patch.object(self.obj, '_save_names'):
            self.obj.names = collections.OrderedDict([("a", "b")])
            self.obj.back("xy")
            e = log.method_calls[0][1][0]
            self.assertTrue(isinstance(e,
                            pyimgren.renamer.UnknownPictureException))
            self.assertEqual(self.obj.folder, e.folder)
            self.assertEqual(self.obj.ref_file, e.ref_file)

    def test_too_many_files(self):
        """Try to rename more than 700 files with same timestamp"""
        self.obj.names = {}
        with mock.patch("os.path.exists", return_value = True):
            try:
                self.obj.get_new_name("foo")
            except RuntimeError as e:
                self.assertTrue("foo" in str(e))
                return
        self.fail("No exception")

    def test_non_existent_file(self):
        """Try to rename a nonexistent file"""
        with mock.patch.object(self.obj, "log") as log:
            self.obj.rename("foo")
            self.assertEqual("warning", log.method_calls[0][0])

    def test_rename_twice(self):
        """Rename a file that has already been renamed"""
        names = collections.OrderedDict({'b': 'a'})
        with mock.patch.object(self.obj, 'load_names', return_value=names), \
             mock.patch.object(self.obj, "_save_names"), \
             mock.patch('glob.glob', side_effect=lambda x: [x]), \
             mock.patch('os.rename') as rename, \
             mock.patch('pyimgren.renamer.exif_dat', return_value=datetime.datetime(2018,2,1)),\
             mock.patch.object(self.obj, 'get_new_name', return_value='c'):
            self.obj.names = names
            self.obj._orig = set(self.obj.names.values())
            self.obj._target = set(self.obj.names.keys())
            self.obj.rename('b', debug=True)
            rename.assert_called_once()
            self.assertTrue(rename.call_args[0][0].endswith('b'))
            self.assertTrue(rename.call_args[0][1].endswith('c'))
            self.assertEqual(collections.OrderedDict({'c': 'a'}), self.obj.names)

    def test_rename_old(self):
        """Rename a file while its name has been used is a previous pass"""
        names = collections.OrderedDict({'b': 'x'})
        with mock.patch.object(self.obj, 'load_names', return_value=names), \
             mock.patch.object(self.obj, "_save_names"), \
             mock.patch('glob.glob', side_effect=lambda x: [x]), \
             mock.patch('os.rename') as rename, \
             mock.patch('pyimgren.renamer.exif_dat', return_value=datetime.datetime(2018,2,1)),\
             mock.patch.object(self.obj, 'get_new_name', return_value='c'):
            self.obj.names = names
            self.obj._orig = set(self.obj.names.values())
            self.obj._target = set(self.obj.names.keys())
            self.obj.rename('x', debug=True)
            rename.assert_called_once()
            self.assertTrue(rename.call_args[0][0].endswith('x'))
            self.assertTrue(rename.call_args[0][1].endswith('c'))
            self.assertEqual(collections.OrderedDict({'b': 'x', 'c': 'xa'}), self.obj.names)


class MergeTest(unittest.TestCase):
    """Tests for the merge method"""
    
    @classmethod
    def setUpClass(cls):
        cls.folder = os.path.dirname(__file__)

    def setUp(self):
        self.obj = pyimgren.Renamer(self.folder)

    def test_incorrect_files(self):
        """A file inside the renamer folder should issue a warning and not copy."""
        with mock.patch.object(self.obj, "_copy") as copy, \
             mock.patch("glob.glob", side_effect=lambda x: [x]), \
             mock.patch("os.path.samefile", return_value = False), \
             mock.patch.object(self.obj, "_move") as move, \
             mock.patch.object(self.obj.log, "warning") as warning:
            self.obj.folder = '/foo/fee'
            self.obj.merge("fee/bar", src_folder='/foo')
            self.assertEqual(1, warning.call_count)
            move.assert_not_called()
            copy.assert_not_called()

    def test_copy_called(self):
        """merge calls _copy and not _move."""
        with mock.patch.object(self.obj, "_copy") as copy, \
             mock.patch("glob.glob", side_effect=lambda x: [x]), \
             mock.patch.object(self.obj, "_move") as move, \
             mock.patch("pyimgren.renamer.exif_dat",
                        return_value=datetime.datetime(2016, 6, 4, 15, 9, 10)):
            self.obj.merge("foo", "bar", src_folder=os.path.join(self.folder, ".."))
            self.assertEqual(2, copy.call_count)
            copy.assert_any_call(os.path.join(self.folder, "..", "foo"),
                                          self.folder, "20160604_150910.jpg",
                                 'foo')
            copy.assert_called_with(os.path.join(self.folder, "..", "bar"),
                                          self.folder, "20160604_150910.jpg",
                                    'bar')
            move.assert_not_called()
            
    def test_ignore_dir(self):
        """merge should ignore directories and warn."""
        with mock.patch.object(self.obj, "_copy") as copy, \
             mock.patch("glob.glob", side_effect=lambda x: [x]), \
             mock.patch("pyimgren.renamer.exif_dat",
                        return_value=datetime.datetime(2016, 6, 4, 15, 9, 10)),\
             mock.patch("os.path.isdir", side_effect= [True, False ]), \
             mock.patch.object(self.obj.log, "warning") as warning:
            self.obj.merge("foo", "bar", src_folder=os.path.join(self.folder, ".."))
            self.assertEqual(1, copy.call_count)
            copy.assert_called_once_with(os.path.join(self.folder, "..", "bar"),
                                          self.folder, "20160604_150910.jpg",
                                         'bar')
            self.assertEqual(1, warning.call_count)
   
    def test_merge_old(self):
        """Merge a file whose name was used in a previous pass"""
        names = collections.OrderedDict({'b': 'x'})
        with mock.patch.object(self.obj, 'load_names', return_value=names), \
             mock.patch.object(self.obj, "_save_names"), \
             mock.patch('glob.glob', side_effect=lambda x: [x]), \
             mock.patch('shutil.copy') as copy, \
             mock.patch('pyimgren.renamer.exif_dat', return_value=datetime.datetime(2018,2,1)),\
             mock.patch.object(self.obj, 'get_new_name', return_value='c'):
            self.obj.names = names
            self.obj._orig = set(self.obj.names.values())
            self.obj._target = set(self.obj.names.keys())
            self.obj.merge('x', debug=True, src_folder='..')
            copy.assert_called_once()
            self.assertTrue(copy.call_args[0][0].endswith('x'))
            self.assertTrue(copy.call_args[0][1].endswith('c'))
            self.assertEqual(collections.OrderedDict({'b': 'x', 'c': 'xa'}), self.obj.names)
