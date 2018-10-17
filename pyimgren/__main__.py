from . import __version__, Renamer, __name__ as prog
import argparse
import logging

def set_parser():
    parser = argparse.ArgumentParser(
        prog = prog,
        description="Rename pictures according to their exif timestamp")
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('folder',
                        help = "folder containing files to rename")
    parser.add_argument('-b', '--back', action='store_true',
                        help = 'restore original names')
    parser.add_argument('-s', '--src_mask', default="DSCF*.jpg",
                        help = "pattern to select the files to rename")
    parser.add_argument('-d', '--dst_mask', default="%Y%m%d_%H%M%S",
                        help = "format for the new file name")
    parser.add_argument('-e', '--ext', default=".jpg", dest='ext_mask',
                        help = "extension for the new file name")
    parser.add_argument('-r', '--ref_file', default="names.log",
                        help = "a file to remember the old names")
    parser.add_argument('-D', '--debug', action='store_true',
                        help = "print a line per rename")
    parser.add_argument('-X', '--dry_run', action='store_true', dest='dummy',
                        help = "process normally except no rename occurs")
    return parser

def main():
    parser = set_parser()
    params = parser.parse_args()
    back = params.back
    kwargs = vars(params)
    del kwargs['back']
    if params.debug:
        log = logging.getLogger('pyimgren')
        log.setLevel(logging.DEBUG)
        log.addHandler(logging.StreamHandler())
    renamer = Renamer(**kwargs)
    if back:
        renamer.back()
    else:
        renamer.rename()

if __name__ == "__main__":
    main()
