#!/usr/bin/env python3
"""Calculates escreens codes."""

import sys  # load arguments

from bbarchivist import argutils  # input validation
from bbarchivist import decorators  # enter to exit
from bbarchivist import hashutils  # main program

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2019 Thurask"


def escreens_main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.hashutils.calculate_escreens` with arguments.
    """
    if len(sys.argv) > 1:
        parser = argutils.default_parser("bb-escreens", "Calculate escrens codes")
        parser.add_argument("pin",
                            help="PIN, 8 characters",
                            type=argutils.escreens_pin)
        parser.add_argument("app",
                            help="OS version, 10.x.y.zzzz")
        parser.add_argument("uptime",
                            help="Uptime, in ms",
                            type=argutils.positive_integer)
        parser.add_argument("duration",
                            help="1/3/6/15/30 days",
                            type=argutils.escreens_duration)
        args = parser.parse_args(sys.argv[1:])
        key = hashutils.calculate_escreens(
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
    pin = argutils.escreens_pin(pin)
    uptime = argutils.positive_integer(uptime)
    duration = argutils.escreens_duration(duration)
    key = hashutils.calculate_escreens(pin.lower(), app, str(uptime), duration)
    print("\n{0}".format(key))
    decorators.enter_to_exit(True)


if __name__ == "__main__":
    escreens_main()
