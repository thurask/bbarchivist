#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301
"""Test the sqlutils module."""

import os
import csv
from shutil import rmtree
import sqlite3
import bbarchivist.sqlutils as bs
from bbarchivist.utilities import file_exists
try:
    import unittest.mock as mock
except ImportError:
    import mock


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp"):
        os.mkdir("temp")
    os.chdir("temp")
    if os.path.exists("bbarchivist.db"):
        os.remove("bbarchivist.db")


def teardown_module(module):
    """
    Delete necessary files.
    """
    if os.path.exists("bbarchivist.db"):
        os.remove("bbarchivist.db")
    if os.path.exists("swrelease.csv"):
        os.remove("swrelease.csv")
    os.chdir("..")
    rmtree("temp")


class TestClassSQLUtils:
    """
    Test SQL-related tools.
    """
    def test_prepare_sw_db(self):
        """
        Test preparing SQL database.
        """
        apath = os.path.abspath(os.getcwd())
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=apath)):
            bs.prepare_sw_db()
        sqlpath = os.path.join(os.path.abspath(os.getcwd()), "bbarchivist.db")
        assert file_exists(sqlpath)

    def test_insert_sw_release(self):
        """
        Test adding software release to SQL database.
        """
        apath = os.path.abspath(os.getcwd())
        sqlpath = os.path.join(apath, "bbarchivist.db")
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=apath)):
            try:
                cnxn = sqlite3.connect(sqlpath)
                with cnxn:
                    crsr = cnxn.cursor()
                    crsr.execute("DROP TABLE Swrelease")
                    reqs = "TEXT NOT NULL UNIQUE COLLATE NOCASE"
                    prim = "INTEGER PRIMARY KEY"
                    table = "Swrelease(Id " + prim + ", Os " + reqs + ", Software " + reqs + ")"
                    crsr.execute("CREATE TABLE IF NOT EXISTS " + table)
            except sqlite3.Error:
                assert False
            bs.insert_sw_release("70.OSVERSION", "80.SWVERSION")
            try:
                cnxn = sqlite3.connect(sqlpath)
                with cnxn:
                    crsr = cnxn.cursor()
                    crsr.execute("SELECT Os,Software FROM Swrelease")
                    rows = crsr.fetchall()
                assert ("70.OSVERSION", "80.SWVERSION") in rows
            except sqlite3.Error:
                assert False
            try:
                cnxn = sqlite3.connect(sqlpath)
                with cnxn:
                    crsr = cnxn.cursor()
                    crsr.execute("SELECT Os,Software FROM Swrelease")
                    rows = crsr.fetchall()
                assert ("70.OSVERSION", "80.SWVERSION") in rows
            except sqlite3.IntegrityError:
                assert True

    def test_export_sql_db(self):
        """
        Test exporting SQL database to csv file.
        """
        if os.getenv("TRAVIS", "false") == "true":
            pass
        else:
            sqlpath = os.path.join(os.path.abspath(os.getcwd()), "bbarchivist.db")
            csvpath = os.path.join(os.path.abspath(os.getcwd()), "swrelease.csv")
            with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.path.abspath(os.getcwd()))):
                try:
                    cnxn = sqlite3.connect(sqlpath)
                    with cnxn:
                        crsr = cnxn.cursor()
                        crsr.execute("DROP TABLE Swrelease")
                        table = "Swrelease(Id INTEGER PRIMARY KEY, Os TEXT NOT NULL UNIQUE COLLATE NOCASE, Software TEXT NOT NULL UNIQUE COLLATE NOCASE)"
                        crsr.execute("CREATE TABLE IF NOT EXISTS " + table)
                        crsr.execute("INSERT INTO Swrelease(Os, Software) VALUES (?,?)",
                                     ("120.OSVERSION", "130.SWVERSION"))
                except sqlite3.Error:
                    assert False
                bs.export_sql_db()
                with open(csvpath, 'r') as csvfile:
                    csvr = csv.reader(csvfile)
                    arow = []
                    for idx, row in enumerate(csvr):
                        if idx == 2:
                            arow = row
                    assert arow[0].strip() == "120.OSVERSION"