#!/usr/bin/env python3
"""Test the compat module."""

import os
from shutil import rmtree

import bbarchivist.compat as bc

try:
    import unittest.mock as mock
except ImportError:
    import mock

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2018 Thurask"


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_compat"):
        os.mkdir("temp_compat")
    os.chdir("temp_compat")


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_compat", ignore_errors=True)


def imp_side_effect(*args):
    """
    Side effect for import mocking.
    """
    if args[0] in ["os", "shutil"]:
        raise ImportError
    else:
        pass


class TestClassCompat:
    """
    Test backwards compatibility utilities.
    """

    def test_enum_cpus(self):
        """
        Test implementation of core counting.
        """
        with mock.patch('bbarchivist.compat.enum_cpus', mock.MagicMock(return_value="123")):
            assert bc.enum_cpus() == "123"

    def test_enum_cpus_legacy(self):
        """
        Test implementation of core counting, legacy.
        """
        with mock.patch('bbarchivist.compat.enum_cpus', mock.MagicMock(return_value="123")):
            with mock.patch('builtins.__import__', mock.MagicMock(side_effect=imp_side_effect)):
                assert bc.enum_cpus() == "123"

    def test_where_which(self):
        """
        Test implementation of where.
        """
        with mock.patch("shutil.which", mock.MagicMock(return_value="here")):
            assert bc.where_which("woodo") == "here"

    def test_where_which_legacy(self):
        """
        Test implementation of where, legacy.
        """
        with mock.patch('bbarchivist.compat.where_which', mock.MagicMock(return_value="here")):
            with mock.patch('builtins.__import__', mock.MagicMock(side_effect=imp_side_effect)):
                assert bc.where_which("woodo") == "here"
