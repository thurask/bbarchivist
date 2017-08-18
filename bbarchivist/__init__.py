#!/usr/bin/env python3
"""The library portion of bbarchivist."""

from . import bbconstants  # constants/versions

__title__ = "bbarchivist"
__version__ = bbconstants.VERSION
__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2017 Thurask"

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
