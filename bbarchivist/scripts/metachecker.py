#!/usr/bin/env python3
"""Checks BlackBerry's developer website for metadata."""

import sys  # load arguments
from bbarchivist import decorators  # enter to exit
from bbarchivist import networkutils  # check function
from bbarchivist import scriptutils  # default parser
from bbarchivist import utilities  # lprint

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def metachecker_main():
    """
    Wrap around :mod:`bbarchivist.networkutils` metadata checking.
    """
    parser = scriptutils.default_parser("bb-metachecker", "NDK metadata scraper.")
    parser.parse_args(sys.argv[1:])
    scriptutils.slim_preamble("METACHECKER")
    runt = networkutils.ndk_metadata() + networkutils.runtime_metadata()
    simu = networkutils.sim_metadata()
    print("RUNTIME METADATA")
    utilities.lprint(sorted(runt))
    print("\nSIMULATOR METADATA")
    utilities.lprint(sorted(simu))
    decorators.enter_to_exit(True)


if __name__ == "__main__":
    metachecker_main()
