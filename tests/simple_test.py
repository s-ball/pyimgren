import unittest
import pyimgren
import datetime
import os

class RenamerTest(unittest.TestCase):
    def test_exif_dat(self):  # control dat of a JPEG file (private method)
        folder = os.path.dirname(__file__)
        ren = pyimgren.Renamer(folder)
        self.assertEqual(datetime.datetime(2018, 8, 29, 15, 24, 20),
                         ren._get_dat(os.path.join(folder, 'DSCF9762.JPG')))
        
