#!/usr/bin/env python3
"""Python interface for cfp."""

import sys  # load arguments
import subprocess  # running cfp
from bbarchivist import bbconstants  # cfp version
from bbarchivist import scriptutils  # default parser
from bbarchivist import utilities  # platform

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def cfp_main():
    """
    Run cfp.
    """
    parser = scriptutils.default_parser("bb-cfp", "BlackBerry CFP.")
    capver = "|{0}".format(bbconstants.CFP.version)
    parser = scriptutils.external_version(parser, capver)
    parser.parse_known_args(sys.argv[1:])
    if utilities.is_windows():
        subprocess.call([utilities.grab_cfp()] + sys.argv[1:])
    else:
        print("Sorry, Windows only.")

if __name__ == "__main__":
    cfp_main()
