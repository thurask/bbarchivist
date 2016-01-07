#!/usr/bin/env python3
"""Checks BlackBerry's Android kernel repo for available branches."""

import sys  # load arguments
from bbarchivist import bbconstants  # versions/constants
from bbarchivist import networkutils  # check function
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def kernchecker_main():
    """
    Wrap around :mod:`bbarchivist.networkutils` kernel checking.
    """
    parser = scriptutils.default_parser("bb-kernchecker",
                                        "Kernel version scraper.")
    parser.parse_args(sys.argv[1:])
    print("~~~KERNCHECKER VERSION {0}~~~".format(bbconstants.VERSION))
    print("\nCHECKING KERNELS...\n")
    kernlist = networkutils.kernel_scraper()
    for item in kernlist:
        print(item)
    scriptutils.enter_to_exit(True)


if __name__ == "__main__":
    kernchecker_main()
