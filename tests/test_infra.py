#  SPDX-FileCopyrightText: 2025-present s-ball <s-ball@laposte.net>
#  #
#  SPDX-License-Identifier: MIT

import re
import unittest

import pyimgren


class InfraTest(unittest.TestCase):
    """Controls that pyimgren__version is defined, is a string, and is
above 0.0"""
    def test_version_is_string(self):
        """Controls that pyimgren.__version__ is a string"""
        self.assertTrue(isinstance(pyimgren.__version__, str),
                        "No version string")

    def test_version_format(self):
        """Controls that pyimgren has an acceptable format and is not 0.0.x"""
        m = re.match(r"(\d+).(\d+).(\d+)", pyimgren.__version__)
        self.assertIsNotNone(m, "Wrong format version")
        maj_v = int(m.group(1))
        min_v = int(m.group(2))
        self.assertTrue(maj_v > 0 or min_v > 0, "Unacceptable version 0.0")
