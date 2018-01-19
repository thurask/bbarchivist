#!/usr/bin/env python3
"""Test the iniconfig module."""

import os
from shutil import rmtree, copyfile
try:
    import unittest.mock as mock
except ImportError:
    import mock
import bbarchivist.iniconfig as bi

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2018 Thurask"


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_iniconfig"):
        os.mkdir("temp_iniconfig")
    os.chdir("temp_iniconfig")
    os.makedirs(os.path.join(os.getcwd(), "olddir", "lookuplogs"))
    with open(os.path.join(os.getcwd(), "olddir", "lookuplogs", "2018_01_01_123456.txt"), "w") as targetfile:
        targetfile.write("Jackdaws love my big sphinx of quartz")
    copyfile(os.path.join(os.getcwd(), "olddir", "lookuplogs", "2018_01_01_123456.txt"), os.path.join(os.getcwd(), "olddir", "bbarchivist.ini"))
    copyfile(os.path.join(os.getcwd(), "olddir", "lookuplogs", "2018_01_01_123456.txt"), os.path.join(os.getcwd(), "olddir", "bbarchivist.db"))
    os.makedirs(os.path.join(os.getcwd(), "newdir", "AppData", "bbarchivist"))
    copyfile(os.path.join(os.getcwd(), "olddir", "lookuplogs", "2018_01_01_123456.txt"), os.path.join(os.getcwd(), "newdir", "AppData", "bbarchivist", "bbarchivist.db"))


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_iniconfig", ignore_errors=True)


class TestClassIniconfig:
    """
    Test config file-related things that aren't tested elsewhere.
    """

    def test_migrate_logs(self):
        """
        Test migrating log files.
        """
        with mock.patch("appdirs.user_log_dir", mock.MagicMock(return_value=os.path.join(os.getcwd(), "newdir", "AppData", "bbarchivist", "Logs"))):
            with mock.patch("os.path.expanduser", mock.MagicMock(return_value=os.path.join(os.getcwd(), "olddir"))):
                assert bi.config_homepath(None, True) == os.path.join(os.getcwd(), "newdir", "AppData", "bbarchivist", "Logs")

    def test_migrate_files(self):
        """
        Test migrating config files.
        """
        with mock.patch("appdirs.user_data_dir", mock.MagicMock(return_value=os.path.join(os.getcwd(), "newdir", "AppData", "bbarchivist"))):
            with mock.patch("os.path.expanduser", mock.MagicMock(return_value=os.path.join(os.getcwd(), "olddir"))):
                assert bi.config_homepath(None, False) == os.path.join(os.getcwd(), "newdir", "AppData", "bbarchivist")
