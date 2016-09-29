#!/usr/bin/env python3

"""This module is used to define constants for the program."""

import os.path  # for producing cap location constant
import sys
from ._version import get_versions

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


class Datafile(object):
    """Structure for information about a data file included with this app."""

    def __init__(self, version, datatype, size):
        self.version = version
        self.filename = "{0}-{1}.dat".format(datatype, version)
        self.location = os.path.join(DIRECTORY, self.filename)
        self.size = size


def frozen_versions():
    """
    Version grabbing when frozen with cx_Freeze.
    """
    with open("longversion.txt", "r") as longv:
        DATA = longv.read().split("\n")
        VER = DATA[0].split("-")
    #: App version.
    VERSION = VER[0]
    #: If we're in a development build.
    DIRTY = "+devel" if DATA[0] != VERSION else ""
    #: Git commit hash.
    COMMITHASH = VER[1]
    #: App version, tag + commits.
    LONGVERSION = "-".join(VER)
    #: Git commit timestamp.
    COMMITDATE = DATA[1]
    return VERSION, DIRTY, COMMITHASH, LONGVERSION, COMMITDATE


if not getattr(sys, 'frozen', False):  # regular
    #: App version.
    VERSION = get_versions()["version"].split("-")[0]
    #: If we're in a development build.
    DIRTY = "+devel" if get_versions()["version"] != VERSION else ""
    #: Git commit hash.
    COMMITHASH = "g{0}".format(get_versions()["full-revisionid"][0:7])
    #: App version, tag + commits.
    LONGVERSION = "-".join((VERSION + DIRTY, COMMITHASH))
    #: Git commit timestamp.
    COMMITDATE = get_versions()["date"]
else:  # cx_freeze support
    VERSION, DIRTY, COMMITHASH, LONGVERSION, COMMITDATE = frozen_versions()
#: File location.
LOCATION = os.path.abspath(__file__)
#: File folder.
DIRECTORY = os.path.dirname(LOCATION)
#: CAP
CAP = Datafile("3.11.0.27", "cap", 9252412)
#: CFP
CFP = Datafile("3.10.0.57", "cfp", 16361984)
#: JSON storage file.
JSONFILE = os.path.join(DIRECTORY, "bbconstants.json")
#: Lookup server list.
SERVERS = {
    "p": "https://cs.sl.blackberry.com/cse/srVersionLookup/2.0.0/",
    "b1": "https://beta.sl.eval.blackberry.com/slscse/srVersionLookup/2.0.0/",
    "b2": "https://beta2.sl.eval.blackberry.com/slscse/srVersionLookup/2.0.0/",
    "a1": "https://alpha.sl.eval.blackberry.com/slscse/srVersionLookup/2.0.0/",
    "a2": "https://alpha2.sl.eval.blackberry.com/slscse/srVersionLookup/2.0.0/"
}
#: Archive files.
ARCS = (".7z", ".tar.xz", ".tar.bz2", ".tar.gz", ".tar", ".zip", ".txz", ".tbz", ".tgz", ".bar")
#: Archive files plus executables.
ARCSPLUS = (".7z", ".tar.xz", ".tar.bz2", ".tar.gz", ".zip", ".tar", ".exe")
#: Compression methods.
METHODS = ("7z", "tbz", "tgz", "zip", "txz", "tar")
#: Autoloader/archive filename beginnings.
PREFIXES = ("Q10", "Z10", "Z30", "Z3", "Passport")
#: Support files.
SUPPS = (".asc", ".cksum")
#: Devices.
DEVICES = (
    "STL100-1",
    "STL100-2/3/P9982",
    "STL100-4",
    "Q10/Q5/P9983",
    "Z30/CLASSIC/LEAP",
    "Z3",
    "PASSPORT")
