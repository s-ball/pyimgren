#  SPDX-FileCopyrightText: 2025-present s-ball <s-ball@laposte.net>
#  #
#  SPDX-License-Identifier: MIT

import argparse
import gettext
import locale
import logging
import os.path

import i18nparse

from . import __version__, Renamer, __name__ as prog
from . import nls_init as ext_init

_ = lambda x: x


def nls_init():
    global _
    lang = ext_init()
    if lang:
        localedir = os.path.join(os.path.dirname(__file__), "locale")
        tr = gettext.translation("cmdline", localedir, [lang], fallback=True)
        _ = tr.gettext


def set_parser():
    parser = argparse.ArgumentParser(
        prog = prog,
        description=_("Rename pictures according to their exif timestamp"))
    parser.add_argument("-V", "--version", action="version",
                        version="%(prog)s " + __version__,
                        help=_("show program's version number and exit"))
    parser.add_argument("--folder", "-f", default = ".",
                        help = _("folder containing files to rename"))
    parser.add_argument("-d", "--dst_mask", default="%Y%m%d_%H%M%S",
                        help = _("format for the new file name"))
    parser.add_argument("-e", "--ext", default=".jpg", dest="ext_mask",
                        help = _("extension for the new file name"))
    parser.add_argument("-r", "--ref_file", default="names.log",
                        help = _("a file to remember the old names"))
    parser.add_argument("-x", "--delta", default=0., type=float,
                        help = _("number of minutes to add to exif time"))
    parser.add_argument("-D", "--debug", action="store_true",
                        help = _("print a line per rename"))
    parser.add_argument("-X", "--dry_run", action="store_true", dest="dummy",
                        help = _("process normally except no rename occurs"))

    # subcommands configuration (rename, back, merge)
    subparser = parser.add_subparsers(dest='subcommand', help=_("sub-commands"))
    ren = subparser.add_parser("rename", help=
                               _("rename files by using their exif timestamp"))
    ren.add_argument("files", nargs="+",
                      help = _("files to process"))
    back = subparser.add_parser("back",
                            help=_("rename files back to their original name"))
    back.add_argument("files", nargs="*",
                    help = _("files to process (default: content of ref_file)"))
    merge = subparser.add_parser("merge",
                                 help=_("merge files from a different folder"))
    merge.add_argument("files", nargs="+",
                      help = _("files to process"))
    merge.add_argument("-s", "--src_folder", default=".",
                       help = _("source folder for merging from"))
    # parser.set_defaults(subcommand="rename") # uncomment to have a default
    return parser


def simple_cmd():
    locale.setlocale(locale.LC_ALL, "")
    i18nparse.activate()
    nls_init()
    parser = set_parser()
    params = parser.parse_args()
    files = params.files
    command = params.subcommand
    kwargs = vars(params)
    if params.debug:
        log = logging.getLogger("pyimgren")
        log.setLevel(logging.DEBUG)
        log.addHandler(logging.StreamHandler())
    renamer = Renamer(**{k: v for k,v in kwargs.items()
                         if k in ('folder', 'dst_mask', 'ext')})
    getattr(renamer, command)(*files, **{k: v for k,v in kwargs.items()
                                         if k in ('delta', 'debug',
                                                  'dummy', 'src_folder')})
