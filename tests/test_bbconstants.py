#!/usr/bin/env python3
"""Test the bbcconstants module: specifically, frozen version info."""

import os
import sys
from shutil import rmtree
try:
    import unittest.mock as mock
except ImportError:
    import mock
import pytest

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2016 Thurask"


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_bbconstants"):
        os.mkdir("temp_bbconstants")
    os.chdir("temp_bbconstants")


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_bbconstants", ignore_errors=True)


class TestClassBBConstants:
    """
    Test frozen imports.
    """

    def test_frozen_import(self, monkeypatch):
        """
        Test if UselessStdout is a terminal.
        """
        monkeypatch.setattr("sys.frozen", True, raising=False)
        with open("longversion.txt", "w") as afile:
            afile.write("2.5.1+devel-ga392773\n2016-05-16T20:43:31-0400")
        import bbarchivist.bbconstants as bb
        assert bb.frozen_versions() == ("2.5.1+devel", "+devel", "ga392773",
                                        "2.5.1+devel-ga392773", "2016-05-16T20:43:31-0400")
        monkeypatch.setattr("sys.frozen", False, raising=False)