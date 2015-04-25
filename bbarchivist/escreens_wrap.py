#!/usr/bin/env python3

import argparse
import sys
try:
    from . import escreens  # @UnusedImport
except SystemError:
    import escreens  # @UnresolvedImport @Reimport
try:
    from . import bbconstants  # @UnusedImport
except SystemError:
    import bbconstants  # @UnresolvedImport @Reimport
try:
    from . import utilities  # @UnusedImport
except SystemError:
    import utilities  # @UnresolvedImport @Reimport


def main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.escreens.calculate_escreens` with arguments.
    """
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(
            prog="bb-escreens",
            description="Calculates escreens codes.",
            epilog="http://github.com/thurask/bbarchivist")
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s " +
            bbconstants._version)
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
        key = escreens.calculate_escreens(
            args.pin,
            args.app,
            args.uptime,
            args.duration)
        print(key)
    else:
        pin = input("PIN: ")
        app = input("APP VERSION: ")
        uptime = int(input("UPTIME: "))
        duration = int(input("1/3/6/15/30 DAYS: "))
        pin = utilities.escreens_pin(pin)
        uptime = str(utilities.positive_integer(uptime))
        duration = utilities.escreens_duration(duration)
        print(" ")
        key = escreens.calculate_escreens(
            pin.lower(),
            app,
            uptime,
            duration)
        print(key)
        smeg = input("Press Enter to exit")  # @UnusedVariable
