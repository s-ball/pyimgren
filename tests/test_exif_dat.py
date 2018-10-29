import unittest
from  pyimgren.pyimgren import exif_dat
import datetime
import os

class ExifDatTest(unittest.TestCase):
    def test_exif_dat(self):  # control dat of a JPEG file
        folder = os.path.dirname(__file__)
        self.assertEqual(datetime.datetime(2018, 8, 29, 15, 24, 20),
                         exif_dat(os.path.join(folder, "DSCF9762.JPG")))
        
