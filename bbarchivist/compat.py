#!/usr/bin/env python3
"""This module is used for backwards compatibility for older Python 3."""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2018 Thurask"


def perf_clock():
    """
    Backwards compatibility wrapper for system clock.
    """
    try:
        from time import perf_counter as clock
    except ImportError:  # 3.2
        from time import clock
    finally:
        wclock = clock()
    return wclock


def enum_cpus():
    """
    Backwards compatibility wrapper for CPU count.
    """
    try:
        from os import cpu_count
    except ImportError:  # 3.2, 3.3
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
    except ImportError:  # 3.2
        from shutilwhich import which
    finally:
        thepath = which(path)
    return thepath
