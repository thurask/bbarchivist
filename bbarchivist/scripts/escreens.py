#!/usr/bin/env python3
"""Calculates escreens codes."""

import sys  # load arguments
from bbarchivist import filehashtools  # main program
from bbarchivist import utilities  # input validation
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015 Thurask"


def escreens_main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.filehashtools.calculate_escreens` with arguments.
    """
    if len(sys.argv) > 1:
        parser = scriptutils.default_parser("bb-escreens",
                                            "Calculate escrens codes")
        parser.add_argument("pin",
                            help="PIN, 8 characters",
                            type=utilities.escreens_pin)
        parser.add_argument("app",
                            help="OS version, 10.x.y.zzzz")
        parser.add_argument("uptime",
                            help="Uptime, in ms",
                            type=utilities.positive_integer)
        parser.add_argument("duration",
                            help="1/3/6/15/30 days",
                            type=utilities.escreens_duration)
        args = parser.parse_args(sys.argv[1:])
        key = filehashtools.calculate_escreens(
            args.pin,
            args.app,
            str(args.uptime),
            args.duration)
        print(key)
    else:
        questionnaire()


def questionnaire():
    """
    Questions to ask if no arguments given.
    """
    pin = input("PIN: ")
    app = input("APP VERSION: ")
    uptime = int(input("UPTIME: "))
    duration = int(input("1/3/6/15/30 DAYS: "))
    pin = utilities.escreens_pin(pin)
    uptime = utilities.positive_integer(uptime)
    duration = utilities.escreens_duration(duration)
    print(" ")
    key = filehashtools.calculate_escreens(
        pin.lower(),
        app,
        str(uptime),
        duration)
    print(key)
    scriptutils.enter_to_exit(True)


if __name__ == "__main__":
    escreens_main()
