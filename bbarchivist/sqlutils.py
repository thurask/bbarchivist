#!/usr/bin/env python3

import sqlite3
import csv
import os
from bbarchivist.utilities import file_exists

def prepare_sw_db():
    """
    Create SQLite DB if not already existing.
    """
    thepath = os.path.expanduser("~")
    thepath = os.path.join(thepath, "bbarchivist.db")
    try:
        cnxn = sqlite3.connect(thepath)
        with cnxn:
            crsr = cnxn.cursor()
            table = "Swrelease(Id INTEGER PRIMARY KEY, Os TEXT NOT NULL UNIQUE COLLATE NOCASE, Software TEXT NOT NULL UNIQUE COLLATE NOCASE)" #@IgnorePep8
            crsr.execute("CREATE TABLE IF NOT EXISTS " + table)
    except sqlite3.Error as sqerror:
        print(str(sqerror))


def insert_sw_release(osversion, swrelease):
    """
    Insert values into main SQLite DB.

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
    except sqlite3.Error:
        pass  # avoid dupes


def export_sql_db():
    """
    Export main SQL DB into a CSV file.
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
                csvw.writerow(('osversion', 'swrelease'))
                csvw.writerows(rows)
        except sqlite3.Error as sqerror:
            print(str(sqerror))
    else:
        print("NO SQL DATABASE FOUND!")
        raise SystemExit
