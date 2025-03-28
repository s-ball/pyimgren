#  SPDX-FileCopyrightText: 2025-present s-ball <s-ball@laposte.net>
#  #
#  SPDX-License-Identifier: MIT

import unittest
from  pyimgren.renamer import exif_dat
import datetime
import os

class ExifDatTest(unittest.TestCase):
    def test_exif_dat(self):
        """Controls exif timestamp of a JPEG file"""
        folder = os.path.dirname(__file__)
        self.assertEqual(datetime.datetime(2018, 8, 29, 15, 24, 20),
                         exif_dat(os.path.join(folder, "DSCF9762.JPG")))
        
