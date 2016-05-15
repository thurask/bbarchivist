#!/usr/bin/env python3
"""This module is used for dealing with SQL databases, including CSV export."""

import sqlite3  # the sql library
import csv  # write to csv
import os  # paths
import operator  # for sorting
import time  # current date
from bbarchivist import decorators  # sql handlers

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def prepare_path():
    """
    Figure out where the path is.
    """
    sqlpath = os.path.join(os.path.expanduser("~"), "bbarchivist.db")
    return sqlpath


@decorators.sql_excepthandler("False")
def prepare_sw_db():
    """
    Create SQLite database, if not already existing.
    """
    cnxn = sqlite3.connect(prepare_path())
    with cnxn:
        crs = cnxn.cursor()
        reqid = "INTEGER PRIMARY KEY"
        reqs = "TEXT NOT NULL UNIQUE COLLATE NOCASE"
        reqs2 = "TEXT NOT NULL"
        table = "Swrelease(Id {0}, Os {1}, Software {1}, Available {2}, Date {2})".format(
            reqid, reqs, reqs2)
        crs.execute("CREATE TABLE IF NOT EXISTS " + table)


@decorators.sql_excepthandler("True")
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
    cnxn = sqlite3.connect(prepare_path())
    with cnxn:
        crs = cnxn.cursor()
        try:  # insert if new
            crs.execute(
                "INSERT INTO Swrelease(Os, Software, Available, Date) VALUES (?,?,?,?)",
                (osversion,
                 swrelease,
                 available,
                 curdate))
        except sqlite3.IntegrityError:  # update if not new
            crs.execute("UPDATE Swrelease SET Available=? WHERE Os=? AND Software=?",
                        (available, osversion, swrelease))


@decorators.sql_excepthandler("False")
def pop_sw_release(osversion, swrelease):
    """
    Remove given entry from database.

    :param osversion: OS version.
    :type osversion: str

    :param swrelease: Software release.
    :type swrelease: str
    """
    cnxn = sqlite3.connect(prepare_path())
    with cnxn:
        crs = cnxn.cursor()
        crs.execute("DELETE FROM Swrelease WHERE Os=? AND Software=?", (osversion, swrelease))


@decorators.sql_excepthandler("False")
def check_exists(osversion, swrelease):
    """
    Check if we did this one already.

    :param osversion: OS version.
    :type osversion: str

    :param swrelease: Software release.
    :type swrelease: str
    """
    cnxn = sqlite3.connect(prepare_path())
    with cnxn:  # check if exists
        crs = cnxn.cursor()
        exis = crs.execute(
            "SELECT EXISTS (SELECT 1 FROM Swrelease WHERE Os=? AND Software=?)",
            (osversion,
             swrelease)).fetchone()[0]
        return bool(exis)


@decorators.sql_excepthandler("False")
@decorators.sql_existhandler(prepare_path())
def export_sql_db():
    """
    Export main SQL database into a CSV file.
    """
    cnxn = sqlite3.connect(prepare_path())
    with cnxn:
        csvpath = os.path.join(os.path.expanduser("~"), "swrelease.csv")
        csvw = csv.writer(open(csvpath, "w"), dialect='excel')
        crs = cnxn.cursor()
        crs.execute("SELECT Os, Software, Available, Date FROM Swrelease")
        rows = crs.fetchall()
        sortedrows = sorted(rows, key=operator.itemgetter(0))
        csvw.writerow(('OS Version', 'Software Release', 'Available', 'Date Modified'))
        csvw.writerows(sortedrows)


@decorators.sql_excepthandler("False")
@decorators.sql_existhandler(prepare_path())
def list_sw_releases(avail=False):
    """
    Return every SW/OS pair in the database.

    :param avail: If we filter out non-available results. Default is false.
    :type avail: bool
    """
    cnxn = sqlite3.connect(prepare_path())
    with cnxn:
        crs = cnxn.cursor()
        query = "SELECT Os, Software, Available, Date FROM Swrelease"
        if avail:
            query += " WHERE Available= 'available'"
        crs.execute(query)
        rows = crs.fetchall()
        return rows
