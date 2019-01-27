#!/usr/bin/env python3
"""This module is used for dummy exceptions, stdout, etc."""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2019 Thurask"


class UselessStdout(object):
    """
    A dummy IO stream. Does nothing, by design.
    """
    @staticmethod
    def write(inp):
        """
        Do nothing.
        """
        pass

    @staticmethod
    def flush():
        """
        Do nothing.
        """
        pass

    @staticmethod
    def isatty():
        """
        Convince module we're in a terminal.
        """
        return True
