#!/usr/bin/env python3
"""Generate bar file URL."""

import sys  # load arguments
from bbarchivist import decorators  # enter to exit
from bbarchivist import utilities  # generation
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2016-2017 Thurask"


def questionnaire():
    """
    Ask input from user.
    """
    software = input("SOFTWARE RELEASE (ex. 10.3.2.2848): ")
    appname = input("APPLICATION NAME (ex. sys.android): ")
    appver = input("APPLICATION VERSION (ex. 10.3.2.348): ")
    print(utilities.create_bar_url(software, appname, appver, True))


def barlinker_main():
    """
    Wrap around :mod:`bbarchivist.utilities` link generation.
    """
    if len(sys.argv) > 1:
        parser = scriptutils.default_parser("bb-barlinker", "Bar file link generator.")
        parser.add_argument("appname", help="Full app name (ex. 'sys.pim.calendar')")
        parser.add_argument("appver", help="App version (ex. '10.3.2.371')")
        parser.add_argument("software", help="Software version of OS")
        parser.set_defaults()
        args = parser.parse_args(sys.argv[1:])
        print(utilities.create_bar_url(args.software, args.appname, args.appver, True))
    else:
        questionnaire()
    decorators.enter_to_exit(True)


if __name__ == "__main__":
    barlinker_main()
