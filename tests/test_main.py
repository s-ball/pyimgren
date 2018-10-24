import unittest
from pyimgren import __version__, Renamer
from pyimgren.__main__ import set_parser, main
from unittest.mock import patch, Mock
import pyimgren.__main__
import sys

class TestMain(unittest.TestCase):
    def test_parser_normal(self):
        """Controls decoding of various params"""
        self.parser = set_parser()
        self.parser.prog = 'pyimgren'
        args_list = {"-D --back fold":
                     {'folder': 'fold', 'src_mask': "DSCF*.jpg",
                      'dst_mask': "%Y%m%d_%H%M%S",
                      'ext_mask': ".jpg", 'ref_file': "names.log",
                      'debug': True, 'dummy': False, 'back': True,
                      'files': []
                      },
                     "--ext=.jpeg -X fold":
                     {'folder': 'fold', 'src_mask': "DSCF*.jpg",
                      'dst_mask': "%Y%m%d_%H%M%S",
                      'ext_mask': ".jpeg", 'ref_file': "names.log",
                      'debug': False, 'dummy': True, 'back': False,
                      'files': []
                      },
                     """--src=IMG*.* --dst=%Y%m%d%H%M%S fold""":
                     {'folder': 'fold', 'src_mask': "IMG*.*",
                      'dst_mask': "%Y%m%d%H%M%S",
                      'ext_mask': ".jpg", 'ref_file': "names.log",
                      'debug': False, 'dummy': False, 'back': False,
                      'files': []
                      },
                     "-r names.txt fold":
                     {'folder': 'fold', 'src_mask': "DSCF*.jpg",
                      'dst_mask': "%Y%m%d_%H%M%S",
                      'ext_mask': ".jpg", 'ref_file': "names.txt",
                      'debug': False, 'dummy': False, 'back': False,
                      'files': []
                      },
                     "-r names.txt fold foo bar":
                     {'folder': 'fold', 'src_mask': "DSCF*.jpg",
                      'dst_mask': "%Y%m%d_%H%M%S",
                      'ext_mask': ".jpg", 'ref_file': "names.txt",
                      'debug': False, 'dummy': False, 'back': False,
                      'files': ['foo', 'bar']
                      },
                     }
        for (args, v) in args_list.items():
            params = self.parser.parse_args(args.split())
            self.assertIsNotNone(params)
            self.assertEqual(v, vars(params))

    def test_main_rename(self):
        """Controls script call as rename"""
        with patch('pyimgren.__main__.Renamer') as patcher:
            sys.argv = [ 'pyimgren', '-D', 'tests' ]
            ren = patcher('f')
            patcher.side_effect = [ren, Exception("Only one Renamer") ]
            main()
            ren.rename.assert_called_once_with()
            ren.back.assert_not_called()
            call = pyimgren.__main__.Renamer.call_args
        kwargs = call[1]
        self.assertEqual(True, kwargs['debug'])
        self.assertEqual(False, kwargs['dummy'])
        self.assertEqual('tests', kwargs['folder'])
            
    def test_main_back(self):
        """Controls script call as back"""
        with patch('pyimgren.__main__.Renamer') as patcher:
            sys.argv = [ 'pyimgren', '-Xb', 'foo' ]
            ren = patcher('f')
            patcher.side_effect = [ren, Exception("Only one Renamer") ]
            main()
            ren.back.assert_called_once_with()
            ren.rename.assert_not_called()
            call = pyimgren.__main__.Renamer.call_args
        kwargs = call[1]
        self.assertEqual(False, kwargs['debug'])
        self.assertEqual(True, kwargs['dummy'])
        self.assertEqual('foo', kwargs['folder'])

    def test_main_params(self):
        """Controls passing of script options"""
        with patch('pyimgren.__main__.Renamer') as patcher:
            sys.argv = [ 'pyimgren', '-Xb', 'foo' ]
            ren = patcher('f')
            patcher.side_effect = [ren, Exception("Only one Renamer") ]
            main()
            call = pyimgren.__main__.Renamer.call_args
        ren = pyimgren.Renamer(*(call[0]), **(call[1]))
        self.assertTrue(ren.dummy)
        self.assertFalse(ren.debug)
        self.assertEqual('foo', ren.folder)
