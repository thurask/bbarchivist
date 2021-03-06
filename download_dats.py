#!/usr/bin/env python3
"""Manually download dat files, if Git-LFS isn't working or something."""

import os
import subprocess

import requests
from bbarchivist.bbconstants import CAP, CFP, FLASHBAT, FLASHBATBBF, FLASHSH, FLASHSHBBF

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2019 Thurask"


def prep_download(url, output_directory=None):
    """
    Prepare download.

    :param url: URL to download from.
    :type url: str

    :param output_directory: Download folder. Default is local.
    :type output_directory: str
    """
    if output_directory is None:
        output_directory = os.getcwd()
    lfname = url.split('/')[-1]
    fname = os.path.join(output_directory, lfname)
    sess = requests.Session()
    return lfname, fname, sess


def download_write(req, lfname, file):
    """
    Write downloaded chunks to file.

    :param req: Response object.
    :type req: requests.Response

    :param lfname: Filename.
    :type lfname: str

    :param file: Open (!!!) file handle. Output file.
    :type file: str
    """
    print("DOWNLOADING {0}".format(lfname))
    for chunk in req.iter_content(chunk_size=1024):
        file.write(chunk)


def download(url, output_directory=None):
    """
    Download file from given URL.

    :param url: URL to download from.
    :type url: str

    :param output_directory: Download folder. Default is local.
    :type output_directory: str
    """
    lfname, fname, sess = prep_download(url, output_directory)
    with open(fname, "wb") as file:
        req = sess.get(url, stream=True)
        if req.status_code == 200:  # 200 OK
            download_write(req, lfname, file)
        else:
            print("ERROR: HTTP {0} IN {1}".format(req.status_code, lfname))


def prep_file(datafile, filelist):
    """
    Prepare a file for download if necessary.

    :param datafile: Datafile instance.
    :type datafile: bbarchivist.bbconstants.Datafile

    :param filelist: List of files that need downloading.
    :type filelist: list(str)
    """
    basename = "https://github.com/thurask/bbarchivist/raw/master/bbarchivist/"
    afile = os.path.basename(datafile.location)
    try:
        if os.path.getsize(datafile.location) != datafile.size:
            filelist.append(basename + afile)
    except FileNotFoundError:
        filelist.append(basename + afile)
    return filelist


def git_ignore(datafile):
    """
    Update git index to deal with pesky issues w/r/t datafiles.

    :param datafile: Datafile instance.
    :type datafile: bbarchivist.bbconstants.Datafile
    """
    cmd = "git update-index --assume-unchanged {0}".format(datafile)
    subprocess.call(cmd, shell=True)


def main():
    """
    Download dat files, in lieu of Git-LFS.
    """
    files = []
    files = prep_file(CAP, files)
    files = prep_file(CFP, files)
    files = prep_file(FLASHBAT, files)
    files = prep_file(FLASHSH, files)
    files = prep_file(FLASHBATBBF, files)
    files = prep_file(FLASHSHBBF, files)
    outdir = os.path.join(os.getcwd(), "bbarchivist", "datfiles")
    if files:
        for file in files:
            download(file, outdir)
            git_ignore(os.path.join(outdir, os.path.basename(file)))
        print("GIT INDEX UPDATED, RE-TRACK IF UPDATE NEEDED")
    else:
        print("NOTHING TO DOWNLOAD!")


if __name__ == "__main__":
    main()
