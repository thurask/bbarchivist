#!/usr/bin/env python3
"""Checks BlackBerry's Android kernel repo for available branches."""

import sys  # load arguments
from bbarchivist import networkutils  # check function
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def kernchecker_main():
    """
    Wrap around :mod:`bbarchivist.networkutils` kernel checking.
    """
    parser = scriptutils.default_parser("bb-kernchecker", "Kernel version scraper.")
    parser.add_argument(
        "-u",
        "--utils",
        help="Check android-utils repo instead",
        action="store_true",
        default=False)
    args = parser.parse_args(sys.argv[1:])
    parser.set_defaults()
    scriptutils.slim_preamble("KERNCHECKER")
    tocheck = "UTILS" if args.utils else "KERNELS"
    print("\nCHECKING {0}...\n".format(tocheck))
    kernlist = networkutils.kernel_scraper(args.utils)
    scriptutils.lprint(kernlist)
    scriptutils.enter_to_exit(True)


if __name__ == "__main__":
    kernchecker_main()
