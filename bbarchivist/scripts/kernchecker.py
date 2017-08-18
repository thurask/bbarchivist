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


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`kernchecker.kernchecker_main` with those arguments.
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
    kernchecker_main(args.utils)


def kernchecker_prep(kernlist):
    """
    Prepare output from kernel list.

    :param kernlist: List of kernel URLs.
    :type kernlist: list(str)
    """
    splitkerns = [x.split("/") for x in kernlist]
    platforms = list({x[0] for x in splitkerns})
    kerndict = {x: [] for x in platforms}
    for kernel in splitkerns:
        kerndict[kernel[0]].append("\t{0}".format(kernel[1]))
    return kerndict


def kernchecker_main(utils=False):
    """
    Wrap around :mod:`bbarchivist.networkutils` kernel checking.

    :param utils: If we're checking utilities rather than kernels.
    :type utils: bool
    """
    scriptutils.slim_preamble("KERNCHECKER")
    tocheck = "UTILS" if args.utils else "KERNELS"
    print("\nCHECKING {0}...\n".format(tocheck))
    kernlist = networkutils.kernel_scraper(args.utils)
    kerndict = kernchecker_prep(kernlist)
    for board in kerndict.keys():
        print(board)
        utilities.lprint(sorted(kerndict[board], reverse=True))
    decorators.enter_to_exit(True)


if __name__ == "__main__":
    grab_args()
