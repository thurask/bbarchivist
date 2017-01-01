#!/usr/bin/env python3
"""Python interface for cap."""

from bbarchivist import bbconstants  # cap version
from bbarchivist import scriptutils  # default parser
from bbarchivist import utilities  # platform

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2017 Thurask"


def cap_main():
    """
    Run cap.
    """
    scriptutils.generic_windows_shim("bb-cap", "BlackBerry CAP.", utilities.grab_cap(), bbconstants.CAP.version)

if __name__ == "__main__":
    cap_main()
