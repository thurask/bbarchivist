#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, R0913, R0912, R0914, R0915, W0142
"""This module is used for dealing with SQL databases, including CSV export."""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015 Thurask"

import sqlite3  # the sql library
import csv  # write to csv
import os  # paths
import operator  # for sorting
import time  # current date
from bbarchivist.utilities import UselessStdout  # check if file exists


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
            reqid = "INTEGER PRIMARY KEY"
            reqs = "TEXT NOT NULL UNIQUE COLLATE NOCASE"
            reqs2 = "TEXT NOT NULL"
            table = "Swrelease(Id {0}, Os {1}, Software {1}, Available {2}, Date {2})".format(
                *(reqid, reqs, reqs2))
            crsr.execute("CREATE TABLE IF NOT EXISTS " + table)
    except sqlite3.Error as sqerror:
        print(str(sqerror))


def insert_sw_release(osversion, swrelease, available, curdate=None):
    """
    Insert values into main SQLite database.

    :param osversion: OS version.
    :type osversion: str

    :param swrelease: Software release.
    :type swrelease: str

    :param servers: If release is available. String converted boolean.
    :type servers: str

    :param curdate: If None, today. For manual dates, specify this.
    :type curdate: str
    """
    if curdate is None:
        curdate = time.strftime("%Y %B %d")
    try:
        cnxn = sqlite3.connect(prepare_path())
        with cnxn:
            crsr = cnxn.cursor()
            try:
                crsr.execute("INSERT INTO Swrelease(Os, Software, Available, Date) VALUES (?,?,?,?)",
                             (osversion, swrelease, available, curdate))  # insert if new
            except sqlite3.IntegrityError:
                crsr.execute("UPDATE Swrelease SET Available=? WHERE Os=? AND Software=?",
                             (available, osversion, swrelease))  # update if not new
    except sqlite3.IntegrityError:
        UselessStdout.write("ASDASDASD")  # avoid dupes
    except sqlite3.Error as sqerror:
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
    except sqlite3.Error as sqerror:
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
    except sqlite3.Error as sqerror:
        print(str(sqerror))


def export_sql_db():
    """
    Export main SQL database into a CSV file.
    """
    thepath = os.path.expanduser("~")
    sqlpath = os.path.join(thepath, "bbarchivist.db")
    if os.path.exists(sqlpath):
        try:
            cnxn = sqlite3.connect(prepare_path())
            with cnxn:
                csvpath = os.path.join(thepath, "swrelease.csv")
                csvw = csv.writer(open(csvpath, "w"), dialect='excel')
                crsr = cnxn.cursor()
                crsr.execute("SELECT Os,Software,Available,Date FROM Swrelease")
                rows = crsr.fetchall()
                sortedrows = sorted(rows, key=operator.itemgetter(0))
                csvw.writerow(('OS Version', 'Software Release', 'Available', 'First Added'))
                csvw.writerows(sortedrows)
        except sqlite3.Error as sqerror:
            print(str(sqerror))
    else:
        print("NO SQL DATABASE FOUND!")
        raise SystemExit


def list_sw_releases():
    """
    Return every SW/OS pair in the database.
    """
    thepath = os.path.expanduser("~")
    sqlpath = os.path.join(thepath, "bbarchivist.db")
    if os.path.exists(sqlpath):
        try:
            cnxn = sqlite3.connect(prepare_path())
            with cnxn:
                crsr = cnxn.cursor()
                crsr.execute("SELECT Os,Software,Available,Date FROM Swrelease")
                rows = crsr.fetchall()
        except sqlite3.Error as sqerror:
            print(str(sqerror))
            return None
        else:
            return rows
    else:
        print("NO SQL DATABASE FOUND!")
        raise SystemExit
