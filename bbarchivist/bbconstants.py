#!/usr/bin/env python3

"""This module is used to define constants for the program."""

import os.path  # for producing cap location constant

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"

#: App version.
VERSION = "2.4.1"
#: File location.
LOCATION = os.path.abspath(__file__)
#: File folder.
DIRECTORY = os.path.dirname(LOCATION)
#: Version of cap.exe bundled with app.
CAPVERSION = "3.11.0.22"
#: Version of cfp.exe bundled with app.
CFPVERSION = "3.10.0.57"
#: cap filename.
CAPFILENAME = "cap-" + CAPVERSION + ".dat"
#: cfp filename.
CFPFILENAME = "cfp-" + CFPVERSION + ".dat"
#: Where cap.exe is. Should be in site-packages.
CAPLOCATION = os.path.join(DIRECTORY, CAPFILENAME)
#: Where cfp.exe is. Should be in site-packages.
CFPLOCATION = os.path.join(DIRECTORY, CFPFILENAME)
#: cap filesize.
CAPSIZE = 9252400
#: cfp filesize.
CFPSIZE = 16361984
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
DEVICES = ("STL100-1", "STL100-2/3/P9982", "STL100-4", "Q10/Q5/P9983", "Z30/CLASSIC/LEAP", "Z3", "PASSPORT")
#: Priv variants for autoloaders.
PRIVVARS = ("common", "vzw-vzw", "na-tmo", "na-att", "apac-amx")
#: 7z exit codes.
SZCODES = {
    0: "NO ERRORS",
    1: "COMPLETED WITH WARNINGS",
    2: "FATAL ERROR",
    7: "COMMAND LINE ERROR",
    8: "OUT OF MEMORY ERROR",
    255: "USER STOPPED PROCESS"
    }
