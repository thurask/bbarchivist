#!/usr/bin/env python3

"""This module is used for dealing with SQL databases, including CSV export."""

__author__ = "Thurask"
__license__ = "Do whatever"
__copyright__ = "2015 Thurask"

import sqlite3  # the sql library
import csv  # write to csv
import os  # paths
import operator  # for sorting
from bbarchivist.utilities import file_exists, UselessStdout  # check if file exists


def prepare_path():
    """
    Figure out where the path is.
    """
    thepath = os.path.expanduser("~")
    sqlpath = os.path.join(thepath, "bbarchivist.db")
    return sqlpath


def prepare_sw_db():
    """
    Create SQLite database, if not already existing.
    """
    try:
        cnxn = sqlite3.connect(prepare_path())
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
    try:
        cnxn = sqlite3.connect(prepare_path())
        with cnxn:
            crsr = cnxn.cursor()
            crsr.execute("INSERT INTO Swrelease(Os, Software) VALUES (?,?)",
                         (osversion, swrelease))
    except sqlite3.IntegrityError:  # pragma: no cover
        UselessStdout.write("ASDASDASD")  # avoid dupes
    except sqlite3.Error as sqerror:  # pragma: no cover
        print(str(sqerror))


def pop_sw_release(osversion, swrelease):
    """
    Remove given entry from database.

    :param osversion: OS version.
    :type osversion: str

    :param swrelease: Software release.
    :type swrelease: str
    """
    try:
        cnxn = sqlite3.connect(prepare_path())
        with cnxn:
            crsr = cnxn.cursor()
            crsr.execute("DELETE FROM Swrelease WHERE Os=? AND Software=?",
                                (osversion, swrelease))
    except sqlite3.Error as sqerror:  # pragma: no cover
        print(str(sqerror))


def check_entry_existence(osversion, swrelease):
    """
    Check if we did this one already.

    :param osversion: OS version.
    :type osversion: str

    :param swrelease: Software release.
    :type swrelease: str
    """
    try:
        cnxn = sqlite3.connect(prepare_path())
        with cnxn:
            crsr = cnxn.cursor()
            exis = crsr.execute("SELECT EXISTS (SELECT 1 FROM Swrelease WHERE Os=? AND Software=?)",
                                (osversion, swrelease)).fetchone()[0]  # check if exists
            if exis:
                return True
            else:
                return False
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
            cnxn = sqlite3.connect(prepare_path())
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
