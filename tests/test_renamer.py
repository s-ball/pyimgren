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
                return
            self.fail("No NamesLogException")
    def test_get_names(self):
        """find a new name pretending 55 files already exist"""
        with mock.patch('os.path.exists',
                        side_effect = ([True] * 55) + [False]):
            n = self.obj._get_new_name('foo')
            self.assertEqual(56, os.path.exists.call_count)
            self.assertEqual('foobc' + self.obj.ext_mask,
                             os.path.exists.call_args[0][0])
            self.assertEqual('foo' + self.obj.ext_mask,
                             os.path.exists.call_args_list[0][0][0])
            self.assertEqual('fooa' + self.obj.ext_mask,
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
                self.assertEqual(pair, os.rename.call_args_list[i][0])
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
                nn = dates[i].strftime(self.obj.dst_mask) + self.obj.ext_mask
                self.assertEqual((n, nn), os.rename.call_args_list[i][0])
                self.assertEqual(nn + ":" + n + '\n',
                                 fd.write.call_args_list[i][0][0])
            
             
