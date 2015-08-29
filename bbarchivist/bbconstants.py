#!/usr/bin/env python3

"""This module is used to define constants for the program."""

__author__ = "Thurask"
__license__ = "Do whatever"
__copyright__ = "2015 Thurask"

import os.path  # for producing cap location constant

#: App version.
VERSION = "2.1.0"
#: File location.
LOCATION = os.path.abspath(__file__)
#: File folder.
DIRECTORY = os.path.dirname(LOCATION)
#: Version of cap.exe bundled with app.
CAPVERSION = "3.11.0.22"
#: cap filename.
CAPFILENAME = "cap-" + CAPVERSION + ".dat"
#: Where cap.exe is. Should be in site-packages.
CAPLOCATION = os.path.join(DIRECTORY, CAPFILENAME)
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
ARCS = (".7z", ".tar.xz", ".tar.bz2", ".tar.gz", ".zip")
#: Archive files plus executables.
ARCSPLUS = (".7z", ".tar.xz", ".tar.bz2", ".tar.gz", ".zip", ".exe")
#: Compression methods.
METHODS = ("7z", "tbz", "tgz", "zip", "txz")
#: Autoloader/archive filename beginnings.
PREFIXES = ("Q10", "Z10", "Z30", "Z3", "Passport")
#: Support files.
SUPPS = (".asc", ".cksum")
