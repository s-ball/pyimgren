# MIT License
# Copyright (c) 2018 s-ball

from . import __version__, Renamer, __name__ as prog
import argparse
import logging

def set_parser():
    parser = argparse.ArgumentParser(
        prog = prog,
        description="Rename pictures according to their exif timestamp")
    parser.add_argument("-v", "--version", action="version",
                        version="%(prog)s " + __version__)
    parser.add_argument("--folder", "-f", default = ".",
                        help = "folder containing files to rename")
    parser.add_argument("-s", "--src_mask", default="DSCF*.jpg",
                        help = "pattern to select the files to rename")
    parser.add_argument("-d", "--dst_mask", default="%Y%m%d_%H%M%S",
                        help = "format for the new file name")
    parser.add_argument("-e", "--ext", default=".jpg", dest="ext_mask",
                        help = "extension for the new file name")
    parser.add_argument("-r", "--ref_file", default="names.log",
                        help = "a file to remember the old names")
    parser.add_argument("-D", "--debug", action="store_true",
                        help = "print a line per rename")
    parser.add_argument("-X", "--dry_run", action="store_true", dest="dummy",
                        help = "process normally except no rename occurs")

    # subcommands configuration (rename, back, merge)
    subparser = parser.add_subparsers(dest='subcommand', help="sub-commands")
    ren = subparser.add_parser("rename", help=
                               "rename files by using their exif timestamp")
    ren.add_argument("files", nargs="*",
                      help = "files to process (default: src_mask)")
    back = subparser.add_parser("back",
                                help="rename files back to their original name")
    back.add_argument("files", nargs="*",
                       help = "files to process (default: content of ref_file)")
    merge = subparser.add_parser("merge",
                                 help="merge files from a different folder")
    merge.add_argument("src_folder", metavar="folder",
                        help = "folder from where merge picture files")
    merge.add_argument("files", nargs="*",
                      help = "files to process (default: src_mask)")
    # parser.set_defaults(subcommand="rename") # uncomment to have a default
    return parser

def main():
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
