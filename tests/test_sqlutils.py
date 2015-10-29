#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, W0142
"""Test the sqlutils module."""

import os
import csv
import pytest
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
    if not os.path.exists("temp_sqlutils"):
        os.mkdir("temp_sqlutils")
    os.chdir("temp_sqlutils")
    if os.path.exists("bbarchivist.db"):
        os.remove("bbarchivist.db")


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_sqlutils", ignore_errors=True)


class TestClassSQLUtils:
    """
    Test SQL-related tools.
    """
    def test_prepare_sw_db(self, capsys):
        """
        Test preparing SQL database.
        """
        apath = os.path.abspath(os.getcwd())
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=apath)):
            bs.prepare_sw_db()
        sqlpath = os.path.join(os.path.abspath(os.getcwd()), "bbarchivist.db")
        assert file_exists(sqlpath)
        with mock.patch("sqlite3.connect", mock.MagicMock(side_effect=sqlite3.Error)):
            bs.prepare_sw_db()
            assert "\n" in capsys.readouterr()[0]

    def test_insert_sw_release(self, capsys):
        """
        Test adding/updating software release to SQL database, including uniqueness.
        """
        apath = os.path.abspath(os.getcwd())
        sqlpath = os.path.join(apath, "bbarchivist.db")
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=apath)):
            try:
                cnxn = sqlite3.connect(sqlpath)
                with cnxn:
                    crsr = cnxn.cursor()
                    crsr.execute("DROP TABLE IF EXISTS Swrelease")
                    reqid = "INTEGER PRIMARY KEY"
                    reqs = "TEXT NOT NULL UNIQUE COLLATE NOCASE"
                    reqs2 = "TEXT"
                    table = "Swrelease(Id {0}, Os {1}, Software {1}, Available {2}, Date {2})".format(
                        *(reqid, reqs, reqs2))
                    crsr.execute("CREATE TABLE IF NOT EXISTS " + table)
            except sqlite3.Error:
                assert False
            bs.insert_sw_release("70.OSVERSION", "80.SWVERSION", "unavailable")
            with mock.patch("bbarchivist.sqlutils.insert_sw_release", mock.MagicMock(return_value=None,
                                                                                     side_effect=sqlite3.IntegrityError)):
                with pytest.raises(sqlite3.IntegrityError):
                    bs.insert_sw_release("70.OSVERSION", "80.SWVERSION", "unavailable")  # update instead of add
            with mock.patch("sqlite3.connect", mock.MagicMock(side_effect=sqlite3.IntegrityError)):
                assert bs.insert_sw_release("70.OSVERSION", "80.SWVERSION", "unavailable")  is None # integrity error
            try:
                cnxn = sqlite3.connect(sqlpath)
                with cnxn:
                    crsr = cnxn.cursor()
                    crsr.execute("SELECT Os,Software,Available FROM Swrelease")
                    rows = crsr.fetchall()
                assert ("70.OSVERSION", "80.SWVERSION", "unavailable") in rows
            except sqlite3.Error:
                assert False
            bs.insert_sw_release("70.OSVERSION", "80.SWVERSION", "available")
            try:
                cnxn = sqlite3.connect(sqlpath)
                with cnxn:
                    crsr = cnxn.cursor()
                    crsr.execute("SELECT Os,Software,Available FROM Swrelease")
                    rows = crsr.fetchall()
                assert ("70.OSVERSION", "80.SWVERSION", "available") in rows
            except sqlite3.Error:
                assert False
            with mock.patch("sqlite3.connect", mock.MagicMock(side_effect=sqlite3.Error)):
                bs.insert_sw_release("70.OSVERSION", "80.SWVERSION", "available")
                assert "\n" in capsys.readouterr()[0]

    def test_pop_sw_release(self, capsys):
        """
        Test removing software release from SQL database.
        """
        apath = os.path.abspath(os.getcwd())
        sqlpath = os.path.join(apath, "bbarchivist.db")
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=apath)):
            try:
                cnxn = sqlite3.connect(sqlpath)
                with cnxn:
                    crsr = cnxn.cursor()
                    crsr.execute("DROP TABLE IF EXISTS Swrelease")
                    reqid = "INTEGER PRIMARY KEY"
                    reqs = "TEXT NOT NULL UNIQUE COLLATE NOCASE"
                    reqs2 = "TEXT"
                    table = "Swrelease(Id {0}, Os {1}, Software {1}, Available {2}, Date {2})".format(
                        *(reqid, reqs, reqs2))
                    crsr.execute("CREATE TABLE IF NOT EXISTS " + table)
            except sqlite3.Error:
                assert False
            bs.insert_sw_release("70.OSVERSION", "80.SWVERSION", "available")
            try:
                cnxn = sqlite3.connect(sqlpath)
                with cnxn:
                    crsr = cnxn.cursor()
                    crsr.execute("SELECT Os,Software,Available FROM Swrelease")
                    rows = crsr.fetchall()
                assert ("70.OSVERSION", "80.SWVERSION", "available") in rows
            except sqlite3.Error:
                assert False
            bs.pop_sw_release("70.OSVERSION", "80.SWVERSION")
            try:
                cnxn = sqlite3.connect(sqlpath)
                with cnxn:
                    crsr = cnxn.cursor()
                    crsr.execute("SELECT Os,Software FROM Swrelease")
                    rows = crsr.fetchall()
                assert not rows
            except sqlite3.Error:
                assert False
            with mock.patch("sqlite3.connect", mock.MagicMock(side_effect=sqlite3.Error)):
                bs.pop_sw_release("70.OSVERSION", "80.SWVERSION")
                assert "\n" in capsys.readouterr()[0]

    def test_entry_existence(self, capsys):
        """
        Test recognition of already inserted entries.
        """
        apath = os.path.abspath(os.getcwd())
        sqlpath = os.path.join(apath, "bbarchivist.db")
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=apath)):
            try:
                cnxn = sqlite3.connect(sqlpath)
                with cnxn:
                    crsr = cnxn.cursor()
                    crsr.execute("DROP TABLE IF EXISTS Swrelease")
                    reqid = "INTEGER PRIMARY KEY"
                    reqs = "TEXT NOT NULL UNIQUE COLLATE NOCASE"
                    reqs2 = "TEXT"
                    table = "Swrelease(Id {0}, Os {1}, Software {1}, Available {2}, Date {2})".format(
                        *(reqid, reqs, reqs2))
                    crsr.execute("CREATE TABLE IF NOT EXISTS " + table)
            except sqlite3.Error:
                assert False
            assert not bs.check_entry_existence("70.OSVERSION", "80.SWVERSION")
            bs.insert_sw_release("70.OSVERSION", "80.SWVERSION", "available")
            assert bs.check_entry_existence("70.OSVERSION", "80.SWVERSION")
            with mock.patch("sqlite3.connect", mock.MagicMock(side_effect=sqlite3.Error)):
                bs.check_entry_existence("70.OSVERSION", "80.SWVERSION")
                assert "\n" in capsys.readouterr()[0]

    def test_export_sql_db(self, capsys):
        """
        Test exporting SQL database to csv file.
        """
        sqlpath = os.path.join(os.path.abspath(os.getcwd()), "bbarchivist.db")
        csvpath = os.path.join(os.path.abspath(os.getcwd()), "swrelease.csv")
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.path.abspath(os.getcwd()))):
            try:
                cnxn = sqlite3.connect(sqlpath)
                with cnxn:
                    crsr = cnxn.cursor()
                    crsr.execute("DROP TABLE IF EXISTS Swrelease")
                    reqid = "INTEGER PRIMARY KEY"
                    reqs = "TEXT NOT NULL UNIQUE COLLATE NOCASE"
                    reqs2 = "TEXT"
                    table = "Swrelease(Id {0}, Os {1}, Software {1}, Available {2}, Date {2})".format(
                        *(reqid, reqs, reqs2))
                    crsr.execute("CREATE TABLE IF NOT EXISTS " + table)
                    crsr.execute("INSERT INTO Swrelease(Os, Software, Available, Date) VALUES (?,?,?,?)",
                                 ("120.OSVERSION", "130.SWVERSION", "available", "1970 January 1"))
            except sqlite3.Error:
                assert False
            bs.export_sql_db()
            with open(csvpath, 'r', newline="\n") as csvfile:
                csvr = csv.reader(csvfile, dialect='excel')
                for idx, row in enumerate(csvr):
                    if idx == 1:
                        assert "120.OSVERSION" in row[0]
            with mock.patch("sqlite3.connect", mock.MagicMock(side_effect=sqlite3.Error)):
                bs.export_sql_db()
                assert "\n" in capsys.readouterr()[0]
            with mock.patch("os.path.exists", mock.MagicMock(return_value=False)):
                with pytest.raises(SystemExit):
                    bs.export_sql_db()

    def test_list_sw_releases(self, capsys):
        """
        Test returning all rows from SQL database.
        """
        sqlpath = os.path.join(os.path.abspath(os.getcwd()), "bbarchivist.db")
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.path.abspath(os.getcwd()))):
            try:
                cnxn = sqlite3.connect(sqlpath)
                with cnxn:
                    crsr = cnxn.cursor()
                    crsr.execute("DROP TABLE IF EXISTS Swrelease")
                    reqid = "INTEGER PRIMARY KEY"
                    reqs = "TEXT NOT NULL UNIQUE COLLATE NOCASE"
                    reqs2 = "TEXT"
                    table = "Swrelease(Id {0}, Os {1}, Software {1}, Available {2}, Date {2})".format(
                        *(reqid, reqs, reqs2))
                    crsr.execute("CREATE TABLE IF NOT EXISTS " + table)
                    crsr.execute("INSERT INTO Swrelease(Os, Software, Available, Date) VALUES (?,?,?,?)",
                                 ("120.OSVERSION", "130.SWVERSION", "available", "1970 January 1"))
            except sqlite3.Error:
                assert False
            rellist = bs.list_sw_releases()
            assert rellist[0] == ("120.OSVERSION", "130.SWVERSION", "available", "1970 January 1")
            with mock.patch("sqlite3.connect", mock.MagicMock(side_effect=sqlite3.Error)):
                bs.list_sw_releases()
                assert "\n" in capsys.readouterr()[0]
            with mock.patch("os.path.exists", mock.MagicMock(return_value=False)):
                with pytest.raises(SystemExit):
                    bs.list_sw_releases()
