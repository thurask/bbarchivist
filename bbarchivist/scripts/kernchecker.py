#!/usr/bin/env python3
"""Checks BlackBerry's Android kernel repo for available branches."""

import sys  # load arguments
from bbarchivist import decorators  # enter to exit
from bbarchivist import networkutils  # check function
from bbarchivist import scriptutils  # default parser
from bbarchivist import utilities  # lprint

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2017 Thurask"


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
    splitkerns = [x.split("/") for x in kernlist]
    platforms = list({x[0] for x in splitkerns})
    kerndict = {x: [] for x in platforms}
    for kernel in splitkerns:
        kerndict[kernel[0]].append("\t{0}".format(kernel[1]))
    for board in kerndict.keys():
        print(board)
        utilities.lprint(sorted(kerndict[board], reverse=True))
    decorators.enter_to_exit(True)


if __name__ == "__main__":
    kernchecker_main()
