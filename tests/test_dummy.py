#!/usr/bin/env python3
"""Test the compat module."""

import os
from shutil import rmtree
import bbarchivist.dummy as bd

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2018 Thurask"


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_dummy"):
        os.mkdir("temp_dummy")
    os.chdir("temp_dummy")


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_dummy", ignore_errors=True)


class TestClassDummy:
    """
    Test UselessStdout and related things.
    """

    def test_uselessstdout_tty(self):
        """
        Test if UselessStdout is a terminal.
        """
        assert bd.UselessStdout.isatty()
