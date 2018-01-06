#!/usr/bin/env python3
"""Grab latest delta update for TCL API devices."""

import sys  # load arguments
from bbarchivist import decorators  # enter to exit
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2017-2018 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke a function with those arguments.
    """
    parser = scriptutils.default_parser("bb-tcldelta", "Check for delta updates for TCL devices")
    parser.add_argument("curef", help="PRD to check", default=None, nargs="?")
    parser.add_argument("fvver", help="Current OS version", default=None, nargs="?")
    parser.add_argument(
        "-d",
        "--download",
        dest="download",
        help="Download update file",
        action="store_true",
        default=False)
    parser.add_argument(
        "-o",
        "--original-filename",
        dest="original",
        help="Save with original filename (implies -d)",
        action="store_true",
        default=False)
    parser.add_argument(
        "-x",
        "--export",
        dest="export",
        help="Write XML to logs folder",
        action="store_true",
        default=False)
    args = parser.parse_args(sys.argv[1:])
    parser.set_defaults()
    if None in (args.curef, args.fvver):
        args = questionnaire(args)
    tcldelta_main(args.curef, args.fvver, args.download, args.original, args.export)
    decorators.enter_to_exit(True)


def questionnaire(args):
    """
    Clear up missing arguments.

    :param args: Arguments.
    :type args: argparse.Namespace
    """
    if args.curef is None:
        args.curef = input("CUREF: ")
    if args.fvver is None:
        args.fvver = input("STARTING OS: ")
    return args


def tcldelta_main(curef, fvver, download=False, original=False, export=False):
    """
    Scan one PRD and produce download URL and filename.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param fvver: Current firmware version.
    :type fvver: str

    :param download: If we'll download the file that this returns. Default is False.
    :type download: bool

    :param original: If we'll download the file with its original filename instead of delta-safe. Default is False.
    :type original: bool

    :param export: Whether to export XML response to file. Default is False.
    :type export: bool
    """
    scriptutils.tcl_prd_scan(curef, download, mode=2, fvver=fvver, original=original, export=export)


if __name__ == "__main__":
    grab_args()
