#!/usr/bin/env python3
"""Test the compat module."""

import os
import sys
from shutil import rmtree
from argparse import ArgumentError
from platform import system
try:
    import unittest.mock as mock
except ImportError:
    import mock
import pytest
import bbarchivist.compat as bc

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


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

    def test_where_which(self):
        """
        Test implementation of where.
        """
        with mock.patch("shutil.which", mock.MagicMock(return_value="here")):
            assert bc.where_which("woodo") == "here"
