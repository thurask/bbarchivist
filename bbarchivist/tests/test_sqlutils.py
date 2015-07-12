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
    if not os.path.exists("temp"):
        os.mkdir("temp")
    os.chdir("temp")
    if os.path.exists("bbarchivist.db"):
        os.remove("bbarchivist.db")


def teardown_module(module):
    if os.path.exists("bbarchivist.db"):
        os.remove("bbarchivist.db")
    if os.path.exists("swrelease.csv"):
        os.remove("swrelease.csv")
    os.chdir("..")
    rmtree("temp")


class TestClassSQLUtils:

    def test_prepare_sw_db(self):
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.path.abspath(os.getcwd()))): #@IgnorePep8
            bs.prepare_sw_db()
        sqlpath = os.path.join(os.path.abspath(os.getcwd()), "bbarchivist.db")
        assert file_exists(sqlpath)

    def test_insert_sw_release(self):
        sqlpath = os.path.join(os.path.abspath(os.getcwd()), "bbarchivist.db")
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.path.abspath(os.getcwd()))): #@IgnorePep8
            try:
                cnxn = sqlite3.connect(sqlpath)
                with cnxn:
                    crsr = cnxn.cursor()
                    crsr.execute("DROP TABLE Swrelease")
                    table = "Swrelease(Id INTEGER PRIMARY KEY, Os TEXT NOT NULL UNIQUE COLLATE NOCASE, Software TEXT NOT NULL UNIQUE COLLATE NOCASE)" #@IgnorePep8
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

    def test_export_sql_db(self):
        if os.getenv("TRAVIS", "false") == "true":
            pass
        else:
            sqlpath = os.path.join(os.path.abspath(os.getcwd()), "bbarchivist.db") #@IgnorePep8
            csvpath = os.path.join(os.path.abspath(os.getcwd()), "swrelease.csv") #@IgnorePep8
            with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.path.abspath(os.getcwd()))): #@IgnorePep8
                try:
                    cnxn = sqlite3.connect(sqlpath)
                    with cnxn:
                        crsr = cnxn.cursor()
                        crsr.execute("DROP TABLE Swrelease")
                        table = "Swrelease(Id INTEGER PRIMARY KEY, Os TEXT NOT NULL UNIQUE COLLATE NOCASE, Software TEXT NOT NULL UNIQUE COLLATE NOCASE)" #@IgnorePep8
                        crsr.execute("CREATE TABLE IF NOT EXISTS " + table)
                        crsr.execute("INSERT INTO Swrelease(Os, Software) VALUES (?,?)", #@IgnorePep8
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
