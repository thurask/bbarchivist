#!/usr/bin/env python3
"""This module is used to handle/provide exceptions."""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def handle_exception(exc, msg="SOMETHING WENT WRONG", xit=SystemExit):
    """
    Print msg, then text of exception exc, then raise exception xit.

    :param exc: Exception to handle.
    :type exc: Exception

    :param msg: Message to raise, "SOMETHING WENT WRONG" by default.
    :type msg: str

    :param xit: Exception to raise upon exit, SystemExit by default.
    :type xit: Exception
    """
    print(msg)
    print(str(exc))
    if xit != DummyException:
        raise xit


class DummyException(Exception):
    """
    Exception that is not raised at all.
    """
    pass
