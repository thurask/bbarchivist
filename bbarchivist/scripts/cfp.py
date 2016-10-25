#!/usr/bin/env python3
"""Python interface for cfp."""

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
    scriptutils.generic_windows_shim("bb-cfp", "BlackBerry CFP.", utilities.grab_cfp(), bbconstants.CFP.version)

if __name__ == "__main__":
    cfp_main()
