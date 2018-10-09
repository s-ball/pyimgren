import unittest
import pyimgren
import re

class InfraTest(unittest.TestCase):
    def test_version_is_string(self):
        self.assertTrue(isinstance(pyimgren.__version__, str),
                        "No version string")
    def test_version_format(self):
        m = re.match(r"(\d+).(\d+).(\d+)", pyimgren.__version__)
        self.assertIsNotNone(m, "Wrong format version")
        majv = int(m.group(1))
        minv = int(m.group(2))
        self.assertTrue(majv > 0 or minv > 0, "Unacceptable version 0.0")
