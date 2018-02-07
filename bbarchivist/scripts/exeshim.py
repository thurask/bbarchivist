#!/usr/bin/env python3
"""Python interface for cap/cfp."""

from bbarchivist import argutils  # default parser
from bbarchivist import bbconstants  # cap/cfp version
from bbarchivist import utilities  # platform

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2018 Thurask"


def cap_main():
    """
    Run cap.
    """
    sdesc = "BlackBerry CAP."
    starget = utilities.grab_cap()
    argutils.generic_windows_shim("bb-cap", sdesc, starget, bbconstants.CAP.version)

def cfp_main():
    """
    Run cfp.
    """
    sdesc = "BlackBerry CFP."
    starget = utilities.grab_cfp()
    argutils.generic_windows_shim("bb-cfp", sdesc, starget, bbconstants.CFP.version)
