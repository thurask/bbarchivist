#!/usr/bin/env python3
"""This module is used for backwards compatibility for older Python 3."""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def enum_cpus():
    """
    Backwards compatibility wrapper for CPU count.
    """
    try:
        from os import cpu_count
    except ImportError:
        from multiprocessing import cpu_count
    finally:
        cpus = cpu_count()
    return cpus


def where_which(path):
    """
    Backwards compatibility wrapper for approximating which/where.

    :param path: Path to a file.
    :type path: str
    """
    try:
        from shutil import which
    except ImportError:
        from shutilwhich import which
    finally:
        thepath = which(path)
    return thepath
