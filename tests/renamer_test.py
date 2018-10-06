import unittest
import unittest.mock
import pyimgren
import os.path
import io

class RenamerTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.folder = os.path.dirname(__file__)
    def setUp(self):
        self.obj = pyimgren.Renamer(self.folder)
    def test_load_names_ok(self):
        with unittest.mock.patch("pyimgren.pyimgren.io.open",
                                 return_value = io.StringIO(u"""a:b
c:d
""")):
            names = self.obj._load_names()
            self.assertEqual(2, len(names.keys()))
            self.assertEqual(u'b', names[u'a'])
    def test_load_names_ko(self):
        with unittest.mock.patch("pyimgren.pyimgren.io.open",
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
            
