#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, R0913, R0912, R0914, R0915
"""Export SQL database to CSV."""

import argparse  # parse arguments
from bbarchivist import bbconstants  # versions/constants
from bbarchivist import sqlutils  # the export function


def sqlexport_main():
    """
    Wrapper around CSV export function.

    Invoke :func:`bbarchivist.sqlutils.export_sql_db`.
    """
    parser = argparse.ArgumentParser(
        prog="bb-sqlexport",
        description="Export SQL database to CSV.",
        epilog="http://github.com/thurask/bbarchivist")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " +
        bbconstants.VERSION)
    parser.set_defaults()
    sqlutils.export_sql_db()
if __name__ == "__main__":
    sqlexport_main()
