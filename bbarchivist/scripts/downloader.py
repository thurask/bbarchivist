#!/usr/bin/env python3
"""Only download OS/radio bar files."""

import os  # filesystem read
import sys  # load arguments

import requests  # session
from bbarchivist import argutils  # arguments
from bbarchivist import decorators  # enter to exit
from bbarchivist import networkutils  # download/lookup
from bbarchivist import scriptutils  # script stuff
from bbarchivist import utilities  # input validation

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2019 Thurask"


@decorators.timer
def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke downloader from :func:`archivist.archivist_main` with arguments.
    """
    if len(sys.argv) > 1:
        parser = argutils.default_parser("bb-downloader", "Download bar files", ("folder", "osr"))
        parser.add_argument(
            "-a",
            "--altsw",
            dest="altsw",
            metavar="SW",
            help="Radio software version, if not same as OS",
            nargs="?",
            default=None)
        parser.add_argument(
            "-d",
            "--debricks",
            dest="debricks",
            help="Download debricks",
            default=False,
            action="store_true")
        parser.add_argument(
            "-c",
            "--cores",
            dest="cores",
            help="Download debricks",
            default=False,
            action="store_true")
        parser.add_argument(
            "-r",
            "--radios",
            dest="radios",
            help="Download radios",
            default=False,
            action="store_true")
        parser.set_defaults()
        args = parser.parse_args(sys.argv[1:])
        args.folder = utilities.dirhandler(args.folder, os.getcwd())
        downloader_main(args.os, args.radio, args.swrelease,
                        args.folder, args.debricks, args.radios,
                        args.cores, args.altsw)
    else:
        questionnaire()


def questionnaire():
    """
    Questions to ask if no arguments given.
    """
    localdir = os.getcwd()
    osversion = input("OS VERSION: ")
    radioversion = input("RADIO VERSION: ")
    softwareversion = input("SOFTWARE RELEASE: ")
    debricks = utilities.i2b("DOWNLOAD DEBRICKS? Y/N: ")
    radios = utilities.i2b("DOWNLOAD RADIOS? Y/N: ")
    if not radios:
        radios = False
    cores = utilities.i2b("DOWNLOAD CORES? Y/N: ")
    if not cores:
        cores = False
    altsw = None
    print(" ")
    downloader_main(osversion, radioversion, softwareversion,
                    localdir, debricks, radios, cores, altsw)
    decorators.enter_to_exit(True)


def downloader_main(osversion, radioversion=None, softwareversion=None,
                    localdir=None, debricks=True, radios=True, cores=False, altsw=None):
    """
    Archivist's download function, abstracted out.

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz. Can be guessed.
    :type radioversion: str

    :param softwareversion: Software release, 10.x.y.zzzz. Can be guessed.
    :type softwareversion: str

    :param localdir: Working directory. Local by default.
    :type localdir: str

    :param debricks: Whether to download debrick OS files. True by default.
    :type debricks: bool

    :param radios: Whether to download radio files. True by default.
    :type radios: bool

    :param cores: Whether to download core OS files. False by default.
    :type cores: bool

    :param altsw: Radio software release, if not the same as OS.
    :type altsw: str
    """
    radioversion = scriptutils.return_radio_version(osversion, radioversion)
    softwareversion, swchecked = scriptutils.return_sw_checked(softwareversion, osversion)
    if altsw:
        altsw, altchecked = scriptutils.return_radio_sw_checked(altsw, radioversion)
    localdir = utilities.dirhandler(localdir, os.getcwd())
    argutils.standard_preamble("downloader", osversion, softwareversion, radioversion, altsw)
    if not any((debricks, radios, cores)):
        print("NO FILES SPECIFIED, DEFAULTING TO DEBRICKS + RADIOS")
        debricks = True
        radios = True
    baseurl, alturl = scriptutils.get_baseurls(softwareversion, altsw)
    osurls, corurls, radurls = utilities.bulk_urls(softwareversion, osversion, radioversion, cores, altsw)

    # Check availability of software releases
    scriptutils.check_sw(baseurl, softwareversion, swchecked)
    if altsw:
        scriptutils.check_radio_sw(alturl, altsw, altchecked)

    # Check availability of OS, radio
    if debricks:
        scriptutils.check_os_bulk(osurls)
        osurls = scriptutils.bulk_avail(osurls)
    if cores:
        scriptutils.check_os_bulk(corurls)
        corurls = scriptutils.bulk_avail(corurls)
    if radios:
        radurls, radioversion = scriptutils.check_radio_bulk(radurls, radioversion)
        radurls = scriptutils.bulk_avail(radurls)

    # Download files
    print("BEGIN DOWNLOADING...")
    urllist = []
    if debricks:
        urllist += osurls
    if radios:
        urllist += radurls
    if cores:
        urllist += corurls
    urllist = list(set(urllist))  # pop duplicates
    if urllist:
        sess = requests.Session()
        networkutils.download_bootstrap(urllist, localdir, workers=5, session=sess)
        print("ALL FILES DOWNLOADED")
    else:
        print("NO FILES TO DOWNLOAD!")
        raise SystemExit

    # Test bar files
    scriptutils.test_bar_files(localdir, urllist)


if __name__ == "__main__":
    grab_args()
