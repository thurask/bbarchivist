#!/usr/bin/env python3

"""This module is used for dealing with SQL databases, including CSV export."""

__author__ = "Thurask"
__license__ = "Do whatever"
__copyright__ = "2015 Thurask"

import sqlite3  # the sql library
import csv  # write to csv
import os  # paths
import operator  # for sorting
from bbarchivist.utilities import file_exists  # check if file exists


def prepare_sw_db():
    """
    Create SQLite database, if not already existing.
    """
    thepath = os.path.expanduser("~")
    thepath = os.path.join(thepath, "bbarchivist.db")
    try:
        cnxn = sqlite3.connect(thepath)
        with cnxn:
            crsr = cnxn.cursor()
            # Filter OS/software, including uniqueness, case-insensitivity, existence, etc.
            reqs = "TEXT NOT NULL UNIQUE COLLATE NOCASE"
            table = "Swrelease(Id INTEGER PRIMARY KEY, Os " + reqs + ", Software " + reqs + ")"
            crsr.execute("CREATE TABLE IF NOT EXISTS " + table)
    except sqlite3.Error as sqerror:  # pragma: no cover
        print(str(sqerror))


def insert_sw_release(osversion, swrelease):
    """
    Insert values into main SQLite database.

    :param osversion: OS version.
    :type osversion: str

    :param swrelease: Software release.
    :type swrelease: str
    """
    thepath = os.path.expanduser("~")
    thepath = os.path.join(thepath, "bbarchivist.db")
    try:
        cnxn = sqlite3.connect(thepath)
        with cnxn:
            crsr = cnxn.cursor()
            crsr.execute("INSERT INTO Swrelease(Os, Software) VALUES (?,?)",
                         (osversion, swrelease))
    except sqlite3.IntegrityError:  # pragma: no cover
        pass  # avoid dupes
    except sqlite3.Error as sqerror:  # pragma: no cover
        print(str(sqerror))


def export_sql_db():
    """
    Export main SQL database into a CSV file.
    """
    thepath = os.path.expanduser("~")
    sqlpath = os.path.join(thepath, "bbarchivist.db")
    if file_exists(sqlpath):
        try:
            cnxn = sqlite3.connect(sqlpath)
            with cnxn:
                csvpath = os.path.join(thepath, "swrelease.csv")
                csvw = csv.writer(open(csvpath, "w"))
                crsr = cnxn.cursor()
                crsr.execute("SELECT Os,Software FROM Swrelease")
                rows = crsr.fetchall()
                sortedrows = sorted(rows, key=operator.itemgetter(0))
                csvw.writerow(('osversion', 'swrelease'))
                csvw.writerows(sortedrows)
        except sqlite3.Error as sqerror:  # pragma: no cover
            print(str(sqerror))
    else:  # pragma: no cover
        print("NO SQL DATABASE FOUND!")
        raise SystemExit
