#!/usr/bin/env python3

"""Manually download dat files, if Git-LFS isn't working or something."""

import os
import requests
from bbarchivist.bbconstants import CAP, CFP

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def download(url, output_directory=None):
    """
    Download file from given URL.

    :param url: URL to download from.
    :type url: str

    :param output_directory: Download folder. Default is local.
    :type output_directory: str
    """
    if output_directory is None:
        output_directory = os.getcwd()
    lfname = url.split('/')[-1]
    fname = os.path.join(output_directory, lfname)
    with open(fname, "wb") as file:
        req = requests.get(url, stream=True)
        if req.status_code == 200:  # 200 OK
            print("DOWNLOADING {0} [{1}]".format(lfname, fsize))
            for chunk in req.iter_content(chunk_size=1024):
                file.write(chunk)
        else:
            print("ERROR: HTTP {0} IN {1}".format(req.status_code, lfname))


def main():
    """
    Download cap and cfp files, in lieu of Git-LFS.
    """
    basename = "https://github.com/thurask/bbarchivist/raw/master/bbarchivist/"
    files = []
    capfile = os.path.basename(CAP.location)
    try:
        if os.path.getsize(CAP.location) != CAP.size:
            files.append(basename + capfile)
    except FileNotFoundError:
        files.append(basename + capfile)
    cfpfile = os.path.basename(CFP.location)
    try:
        if os.path.getsize(CFP.location) != CFP.size:
            files.append(basename + cfpfile)
    except FileNotFoundError:
        files.append(basename + cfpfile)
    outdir = os.path.join(os.getcwd(), "bbarchivist")
    if files:
        for file in files:
            download(file, outdir)
    else:
        print("NOTHING TO DOWNLOAD!")


if __name__ == "__main__":
    main()
