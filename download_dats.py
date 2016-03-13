#!/usr/bin/env python3
#pylint: disable = I0011, C0111, C0103, W0622

"""Manually download dat files, if Git-LFS isn't working or something."""

import os
from bbarchivist.networkutils import download_bootstrap
from bbarchivist.bbconstants import CAPSIZE, CFPSIZE, CAPLOCATION, CFPLOCATION

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def download():
    """
    Download cap and cfp files, in lieu of Git-LFS.
    """
    basename = "https://github.com/thurask/bbarchivist/raw/master/bbarchivist/"
    files = []
    capfile = os.path.basename(CAPLOCATION)
    try:
        if os.path.getsize(CAPLOCATION) != CAPSIZE:
            files.append(basename+capfile)
    except FileNotFoundError:
        files.append(basename+capfile)
    cfpfile = os.path.basename(CFPLOCATION)
    try:
        if os.path.getsize(CFPLOCATION) != CFPSIZE:
            files.append(basename+cfpfile)
    except FileNotFoundError:
        files.append(basename+cfpfile)
    outdir = os.path.join(os.getcwd(), "bbarchivist")
    if files:
        download_bootstrap(files, outdir)
    else:
        print("NOTHING TO DOWNLOAD!")


if __name__ == "__main__":
    download()