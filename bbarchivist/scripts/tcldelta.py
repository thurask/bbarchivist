#!/usr/bin/env python3
"""Grab latest delta update for TCL API devices."""

import sys  # load arguments
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2017 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke a function with those arguments.
    """
    parser = scriptutils.default_parser("bb-tcldelta", "Check for delta updates for TCL devices")
    parser.add_argument("curef", help="PRD to check")
    parser.add_argument("fvver", help="Current OS version")
    parser.add_argument(
        "-d",
        "--download",
        dest="download",
        help="Download update file",
        action="store_true",
        default=False)
    args = parser.parse_args(sys.argv[1:])
    parser.set_defaults()
    tcldelta_main(args.curef, args.fvver, args.download)


def tcldelta_main(curef, fvver, download=False):
    """
    Scan one PRD and produce download URL and filename.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param fvver: Current firmware version.
    :type fvver: str

    :param download: If we'll download the file that this returns. Default is False.
    :type download: bool
    """
    scriptutils.tcl_prd_scan(curef, download, mode=2, fvver=fvver)


if __name__ == "__main__":
    grab_args()
