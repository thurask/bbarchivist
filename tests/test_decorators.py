#!/usr/bin/env python3
"""Test the decorators module."""

import os
from shutil import rmtree

import bbarchivist.decorators as bd
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2017-2018 Thurask"


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_decorators"):
        os.mkdir("temp_decorators")
    os.chdir("temp_decorators")


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_decorators", ignore_errors=True)


def dumb_input(instring):
    """
    Mock input function.

    :param instring: Does nothing.
    :type instring: str
    """
    print(instring)
    return "snek"


def kb_interrupt(instring):
    """
    Raise KeyboardInterrupt.

    :param instring: Does nothing.
    :type instring: str
    """
    print(instring)
    raise KeyboardInterrupt


class TestClassDecorators:
    """
    Test function decorators.
    """

    def test_enter_to_exit(self):
        """
        Test pressing Enter to exit.
        """
        with mock.patch('builtins.input', mock.MagicMock(side_effect=dumb_input)):
            with pytest.raises(SystemExit):
                bd.enter_to_exit(False)

    def test_keyboard_except(self):
        """
        Test absorbing keyboard except.
        """
        kbex = bd.wrap_keyboard_except(kb_interrupt)
        kbex("snek")
