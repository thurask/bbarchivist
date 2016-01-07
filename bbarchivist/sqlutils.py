#!/usr/bin/env python3
"""This module is used for dealing with SQL databases, including CSV export."""

import sqlite3  # the sql library
import csv  # write to csv
import os  # paths
import operator  # for sorting
import time  # current date
from bbarchivist.utilities import UselessStdout  # check if file exists
# flake8: noqa

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


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
            crs = cnxn.cursor()
            reqid = "INTEGER PRIMARY KEY"
            reqs = "TEXT NOT NULL UNIQUE COLLATE NOCASE"
            reqs2 = "TEXT NOT NULL"
            table = "Swrelease(Id {0}, Os {1}, Software {1}, Available {2}, Date {2})".format(
                *(reqid, reqs, reqs2))
            crs.execute("CREATE TABLE IF NOT EXISTS " + table)
    except sqlite3.Error as sqerror:
        print(str(sqerror))


def insert(osversion, swrelease, available, curdate=None):
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
            crs = cnxn.cursor()
            try:
                crs.execute("INSERT INTO Swrelease(Os, Software, Available, Date) VALUES (?,?,?,?)",
                            (osversion, swrelease, available, curdate))  # insert if new
            except sqlite3.IntegrityError:
                crs.execute("UPDATE Swrelease SET Available=? WHERE Os=? AND Software=?",
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
            crs = cnxn.cursor()
            crs.execute("DELETE FROM Swrelease WHERE Os=? AND Software=?",
                        (osversion, swrelease))
    except sqlite3.Error as sqerror:
        print(str(sqerror))


def check_exists(osversion, swrelease):
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
            crs = cnxn.cursor()
            exis = crs.execute("SELECT EXISTS (SELECT 1 FROM Swrelease WHERE Os=? AND Software=?)",
                               (osversion, swrelease)).fetchone()[0]  # check if exists
            return bool(exis)
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
                crs = cnxn.cursor()
                crs.execute("SELECT Os,Software,Available,Date FROM Swrelease")
                rows = crs.fetchall()
                sortedrows = sorted(rows, key=operator.itemgetter(0))
                csvw.writerow(('OS Version', 'Software Release', 'Available', 'Date Modified'))
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
                crs = cnxn.cursor()
                crs.execute("SELECT Os,Software,Available,Date FROM Swrelease")
                rows = crs.fetchall()
        except sqlite3.Error as sqerror:
            print(str(sqerror))
            return None
        else:
            return rows
    else:
        print("NO SQL DATABASE FOUND!")
        raise SystemExit
