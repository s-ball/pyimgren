# MIT License
# Copyright (c) 2018 s-ball

from . import __version__, Renamer, __name__ as prog
import argparse
import logging
import i18nparse
import gettext
import os.path
import locale

localedir = os.path.join(os.path.dirname(__file__), "locale")
lang = locale.getdefaultlocale()[0]
tr = gettext.translation("main", localedir, [lang], fallback=True)
_ = tr.gettext

def set_parser():
    parser = argparse.ArgumentParser(
        prog = prog,
        description=_("Rename pictures according to their exif timestamp"))
    parser.add_argument("-v", "--version", action="version",
                        version="%(prog)s " + __version__)
    parser.add_argument("--folder", "-f", default = ".",
                        help = _("folder containing files to rename"))
    parser.add_argument("-s", "--src_mask", default="DSCF*.jpg",
                        help = _("pattern to select the files to rename"))
    parser.add_argument("-d", "--dst_mask", default="%Y%m%d_%H%M%S",
                        help = _("format for the new file name"))
    parser.add_argument("-e", "--ext", default=".jpg", dest="ext_mask",
                        help = _("extension for the new file name"))
    parser.add_argument("-r", "--ref_file", default="names.log",
                        help = _("a file to remember the old names"))
    parser.add_argument("-D", "--debug", action="store_true",
                        help = _("print a line per rename"))
    parser.add_argument("-X", "--dry_run", action="store_true", dest="dummy",
                        help = _("process normally except no rename occurs"))

    # subcommands configuration (rename, back, merge)
    subparser = parser.add_subparsers(dest='subcommand', help=_("sub-commands"))
    ren = subparser.add_parser("rename", help=
                               _("rename files by using their exif timestamp"))
    ren.add_argument("files", nargs="*",
                      help = _("files to process (default: src_mask)"))
    back = subparser.add_parser("back",
                            help=_("rename files back to their original name"))
    back.add_argument("files", nargs="*",
                    help = _("files to process (default: content of ref_file)"))
    merge = subparser.add_parser("merge",
                                 help=_("merge files from a different folder"))
    merge.add_argument("src_folder", metavar="folder",
                        help = _("folder from where merge picture files"))
    merge.add_argument("files", nargs="*",
                      help = _("files to process (default: src_mask)"))
    # parser.set_defaults(subcommand="rename") # uncomment to have a default
    return parser

def main():
    locale.setlocale(locale.LC_ALL, "")
    i18nparse.activate()
    parser = set_parser()
    params = parser.parse_args()
    files = params.files
    command = params.subcommand
    kwargs = vars(params)
    del kwargs["subcommand"]
    del kwargs["files"]
    if command == "merge":
        src_folder = params.src_folder
        del kwargs["src_folder"]
    if params.debug:
        log = logging.getLogger("pyimgren")
        log.setLevel(logging.DEBUG)
        log.addHandler(logging.StreamHandler())
    renamer = Renamer(**kwargs)
    if command == "merge":
        renamer.merge(src_folder, *files)
    else:
        getattr(renamer, command)(*files)

if __name__ == "__main__":
    main()
