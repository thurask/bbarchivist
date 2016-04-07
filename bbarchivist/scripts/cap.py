#!/usr/bin/env python3
"""Python interface for cap."""

import sys  # load arguments
import subprocess  # running cap
from bbarchivist import scriptutils  # default parser
from bbarchivist import utilities  # platform

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def cap_main():
    """
    Run cap.
    """
    parser = scriptutils.default_parser("bb-cap", "BlackBerry CAP.")
    parser.parse_known_args(sys.argv[1:])
    if utilities.is_windows():
        subprocess.call([utilities.grab_cap()] + sys.argv[1:])
    else:
        print("Sorry, Windows only.")

if __name__ == "__main__":
    cap_main()
