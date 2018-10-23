import unittest
try:
    from unittest import mock
except:
    import mock
import pyimgren.pyimgren
import os.path
import io
import collections
import datetime

class RenamerTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.folder = os.path.dirname(__file__)
    def setUp(self):
        self.obj = pyimgren.Renamer(self.folder)
    def test_load_names_ok(self):
        """Extract a name from a names.log file"""
        with unittest.mock.patch("pyimgren.pyimgren.io.open",
                                 return_value = io.StringIO(u"""a:b
c:d
""")):
            names = self.obj._load_names()
            self.assertEqual(2, len(names.keys()))
            self.assertEqual(u'b', names[u'a'])
    def test_load_names_ko(self):
        """Try to extract a name from a broken names.log file"""
        with mock.patch("pyimgren.pyimgren.io.open",
                                 return_value = io.StringIO(u"""a:b
c
:d
""")):
            try:
                names = self.obj._load_names()
            except pyimgren.pyimgren.NamesLogException as e:
                self.assertEqual(2, e.numlig)
                self.assertEqual(u'c\n', e.line)
                self.assertTrue(isinstance(str(e), str))
                return
            self.fail("No NamesLogException")
    def test_get_names(self):
        """find a new name pretending 55 files already exist"""
        with mock.patch('os.path.exists',
                        side_effect = ([True] * 55) + [False]):
            n = self.obj._get_new_name('foo')
            self.assertEqual(56, os.path.exists.call_count)
            self.assertEqual(os.path.join(self.obj.folder, 'foobc')
                             + self.obj.ext_mask,
                             os.path.exists.call_args[0][0])
            self.assertEqual(os.path.join(self.obj.folder, 'foo')
                             + self.obj.ext_mask,
                             os.path.exists.call_args_list[0][0][0])
            self.assertEqual(os.path.join(self.obj.folder, 'fooa')
                             + self.obj.ext_mask,
                             os.path.exists.call_args_list[1][0][0])
            self.assertEqual('foobc' + self.obj.ext_mask, n)
    def test_back(self):
        """Rename back 3 files"""
        flist = [('a', 'b'), ('c', 'd'), ('e', 'f')]
        with mock.patch('os.rename'),mock.patch.object(
            self.obj, "_load_names", return_value =
            collections.OrderedDict(flist)), mock.patch(
                'glob.glob', side_effect = [
                    [ os.path.join(self.folder, i)]
                    for i,j in flist]):
            
            self.obj.back()
            self.assertEqual(3, os.rename.call_count)
            for i, pair in enumerate(flist):
                self.assertEqual(
                    tuple(map(lambda x: os.path.join(self.folder, x),pair)),
                    os.rename.call_args_list[i][0])
    def test_rename(self):
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
        with mock.patch('os.rename'), \
             mock.patch.object(self.obj, "_load_names",
                               return_value = collections.OrderedDict()), \
             mock.patch('io.open', return_value = open_ctx), \
             mock.patch('glob.glob', return_value = names), \
             mock.patch('pyimgren.pyimgren.exif_dat',
                        side_effect = dates):
            self.obj.rename()
            for i, n in enumerate(names):
                nn0 = dates[i].strftime(self.obj.dst_mask) + self.obj.ext_mask
                nn = os.path.join(self.folder, nn0)
                self.assertEqual((n, nn), os.rename.call_args_list[i][0])
                self.assertEqual(nn0 + ":" +
                                 os.path.relpath(n, self.folder) + '\n',
                                 fd.write.call_args_list[i][0][0])
            
    def test_rename_dir(self):
        """Rename a sub-folder"""
        abs_folder = os.path.join(self.folder, 'sub')
        sub = mock.Mock(spec = pyimgren.Renamer)
        with mock.patch('os.path.join', return_value=abs_folder) as join, \
             mock.patch('os.path.isdir') as isdir, \
             mock.patch('glob.glob', return_value=[abs_folder]), \
             mock.patch('pyimgren.pyimgren.Renamer', return_value = sub) as ren:
            self.obj.rename('sub')
            ren.assert_called_once_with(abs_folder, self.obj.src_mask,
                                    self.obj.dst_mask,
                                    self.obj.ext_mask,
                                    self.obj.ref_file,
                                    self.obj.debug,
                                    self.obj.dummy)
            self.assertTrue(sub._log is self.obj._log)
            sub.rename.assert_called_once_with()
            
    def test_unknown_picture(self):
        """Try to rename back a file not known in names.log"""
        log = mock.Mock()
        with mock.patch('os.path.isdir', return_value = False), \
             mock.patch('os.path.relpath', return_value = "xy"), \
             mock.patch('glob.glob', return_value = ['xy']), \
             mock.patch.object(self.obj, '_log') as log, \
             mock.patch.object(self.obj, '_load_names',
                return_value = collections.OrderedDict([('a', 'b')])):
        
            self.obj.back("xy")
            e = log.method_calls[0][1][0]
            self.assertTrue(isinstance(e,
                            pyimgren.pyimgren.UnknownPictureException))
            self.assertEqual(self.obj.folder, e.folder)
            self.assertEqual(self.obj.ref_file, e.ref_file)
    def test_back_dir(self):
        """Rename back a sub-folder"""
        abs_folder = os.path.join(self.folder, 'sub')
        sub = mock.Mock(spec = pyimgren.Renamer)
        with mock.patch('os.path.join', return_value=abs_folder), \
             mock.patch('os.path.isdir', return_value = True), \
             mock.patch('glob.glob', return_value=[abs_folder]), \
             mock.patch('pyimgren.pyimgren.Renamer', return_value = sub) as ren:
            self.obj.back('sub')
            ren.assert_called_once_with(abs_folder, self.obj.src_mask,
                                    self.obj.dst_mask,
                                    self.obj.ext_mask,
                                    self.obj.ref_file,
                                    self.obj.debug,
                                    self.obj.dummy)
            self.assertTrue(sub._log is self.obj._log)
            sub.back.assert_called_once_with()
    def test_too_many_files(self):
        """Try to rename more than 700 files with same timestamp"""
        with mock.patch('os.path.exists', return_value = True):
            try:
                n = self.obj._get_new_name('foo')
            except Exception as e:
                self.assertTrue('foo' in str(e))
                return
        self.fail("No exception")

    def test_inexistant_file(self):
        """Try to rename an inexistant file"""
        with mock.patch.object(self.obj, '_log') as log:
            self.obj.rename('foo')
            self.assertEqual('warning', log.method_calls[0][0])
        
