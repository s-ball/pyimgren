#  SPDX-FileCopyrightText: 2025-present s-ball <s-ball@laposte.net>
#  #
#  SPDX-License-Identifier: MIT

import sys
import unittest
from unittest.mock import patch

import pyimgren.__main__
from pyimgren.cmdline import set_parser, simple_cmd


class TestMain(unittest.TestCase):
    def test_parser_normal(self):
        """Controls decoding of various params"""
        self.parser = set_parser()
        self.parser.prog = "pyimgren"
        args_list = {"-D -f fold back DSCF*.jpg":
                     {"folder": "fold", "files": ["DSCF*.jpg"],
                      "dst_mask": "%Y%m%d_%H%M%S",
                      "ext_mask": ".jpg", "ref_file": "names.log",
                      "debug": True, "dummy": False, "subcommand": "back",
                      "delta": 0.0
                      },
                     "--ext=.jpeg -X -f fold rename IMG*.jpg":
                     {"folder": "fold", "dst_mask": "%Y%m%d_%H%M%S",
                      "ext_mask": ".jpeg", "ref_file": "names.log",
                      "debug": False, "dummy": True, "subcommand": "rename",
                      "files": ["IMG*.jpg"], "delta": 0.0
                      },
                     "--ext=.jpeg -X -f fold -x 1.5 rename IMG*.jpeg":
                     {"folder": "fold",
                      "dst_mask": "%Y%m%d_%H%M%S",
                      "ext_mask": ".jpeg", "ref_file": "names.log",
                      "debug": False, "dummy": True, "subcommand": "rename",
                      "files": ["IMG*.jpeg"], "delta": 1.5
                      },
                     """--dst=%Y%m%d%H%M%S -f fold rename IMG*.*""":
                     {"folder": "fold",
                      "dst_mask": "%Y%m%d%H%M%S",
                      "ext_mask": ".jpg", "ref_file": "names.log",
                      "debug": False, "dummy": False, "subcommand": "rename",
                      "files": ["IMG*.*"], "delta": 0.0
                      },
                     "-r names.txt --folder=fold rename DSC*.jpg":
                     {"folder": "fold",
                      "dst_mask": "%Y%m%d_%H%M%S",
                      "ext_mask": ".jpg", "ref_file": "names.txt",
                      "debug": False, "dummy": False, "subcommand": "rename",
                      "files": ["DSC*.jpg"], "delta": 0.0
                      },
                     "-r names.txt -f fold rename foo bar":
                     {"folder": "fold",
                      "dst_mask": "%Y%m%d_%H%M%S",
                      "ext_mask": ".jpg", "ref_file": "names.txt",
                      "debug": False, "dummy": False, "subcommand": "rename",
                      "files": ["foo", "bar"], "delta": 0.0
                      },
                     "merge -s fold foo bar":
                     {"folder": ".",
                      "dst_mask": "%Y%m%d_%H%M%S",
                      "ext_mask": ".jpg", "ref_file": "names.log",
                      "debug": False, "dummy": False, "subcommand": "merge",
                      "files": ["foo", "bar"], "src_folder": "fold",
                      "delta": 0.0
                      },
                     }
        for (args, v) in args_list.items():
            params = self.parser.parse_args(args.split())
            self.assertIsNotNone(params)
            self.assertEqual(v, vars(params))

    def test_main_rename(self):
        """Controls script call as rename"""
        with patch("pyimgren.cmdline.Renamer") as patcher:
            sys.argv = ["pyimgren", "-D", "-f", "tests", "rename", "foo"]
            ren = patcher("f")
            patcher.side_effect = [ren, Exception("Only one Renamer")]
            simple_cmd()
            ren.rename.assert_called_once()
            ren.back.assert_not_called()
            call = pyimgren.cmdline.Renamer.call_args
            ren_call = ren.rename.call_args
        kwargs = ren_call[1]
        self.assertEqual(True, kwargs["debug"])
        self.assertEqual(False, kwargs["dummy"])
        kwargs = call[1]
        self.assertEqual("tests", kwargs["folder"])
            
    def test_main_back(self):
        """Controls script call as back"""
        with patch("pyimgren.cmdline.Renamer") as patcher:
            sys.argv = [ "pyimgren", "-Xf", "foo", "back" ]
            ren = patcher("f")
            patcher.side_effect = [ren, Exception("Only one Renamer") ]
            simple_cmd()
            ren.back.assert_called_once()
            ren.rename.assert_not_called()
            call = pyimgren.cmdline.Renamer.call_args
            back_call = ren.back.call_args
        kwargs = back_call[1]
        self.assertEqual(False, kwargs["debug"])
        self.assertEqual(True, kwargs["dummy"])
        kwargs = call[1]
        self.assertEqual("foo", kwargs["folder"])

    def test_main_params(self):
        """Controls passing of script options"""
        with patch("pyimgren.cmdline.Renamer") as patcher:
            sys.argv = [ "pyimgren", "-Xf", "foo", "back" ]
            ren = patcher("f")
            patcher.side_effect = [ren, Exception("Only one Renamer") ]
            simple_cmd()
            call = pyimgren.cmdline.Renamer.call_args
        rename = pyimgren.Renamer(*(call[0]), **(call[1]))
        self.assertEqual("foo", rename.folder)

    def test_main_merge(self):
        """Controls script call as merge"""
        with patch("pyimgren.cmdline.Renamer") as patcher:
            sys.argv = [ "pyimgren", "-D", "-f", "tests", "merge", "/folder" ]
            ren = patcher("f")
            patcher.side_effect = [ren, Exception("Only one Renamer") ]
            simple_cmd()
            ren.merge.assert_called_once()
            ren.rename.assert_not_called()
            call = pyimgren.cmdline.Renamer.call_args
            merge_call = ren.merge.call_args
        kwargs = merge_call[1]
        self.assertEqual(True, kwargs["debug"])
        self.assertEqual(False, kwargs["dummy"])
        kwargs = call[1]
        self.assertEqual("tests", kwargs["folder"])
        
