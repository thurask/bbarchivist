#!/usr/bin/env python3
"""Only download OS/radio bar files."""

import os  # filesystem read
import sys  # load arguments
from bbarchivist import scriptutils  # script stuff
from bbarchivist import bbconstants  # versions/constants
from bbarchivist import utilities  # input validation
from bbarchivist import networkutils  # download/lookup

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke downloader from :func:`archivist.archivist_main` with arguments.
    """
    if len(sys.argv) > 1:
        parser = scriptutils.default_parser("bb-downloader",
                                            "Download bar files")
        parser.add_argument(
            "os",
            help="OS version, 10.x.y.zzzz")
        parser.add_argument(
            "radio",
            help="Radio version, 10.x.y.zzzz",
            nargs="?",
            default=None)
        parser.add_argument(
            "swrelease",
            help="Software version, 10.x.y.zzzz",
            nargs="?",
            default=None)
        parser.add_argument(
            "-f",
            "--folder",
            dest="folder",
            help="Working folder",
            default=None,
            metavar="DIR")
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
        parser.add_argument(
            "-ni",
            "--no-integrity",
            dest="integrity",
            help="Don't test bar files after download",
            action="store_false",
            default=True)
        parser.set_defaults()
        args = parser.parse_args(sys.argv[1:])
        if args.folder is None:
            args.folder = os.getcwd()
        downloader_main(args.os, args.radio, args.swrelease,
                        args.folder, args.debricks, args.radios,
                        args.cores, args.integrity, args.altsw)
    else:
        localdir = os.getcwd()
        osversion = input("OS VERSION: ")
        radioversion = input("RADIO VERSION: ")
        softwareversion = input("SOFTWARE RELEASE: ")
        debricks = utilities.s2b(input("DOWNLOAD DEBRICKS? Y/N: "))
        radios = utilities.s2b(input("DOWNLOAD RADIOS? Y/N: "))
        if not radios:
            radios = False
        cores = utilities.s2b(input("DOWNLOAD CORES? Y/N: "))
        if not cores:
            cores = False
        integrity = True
        altsw = None
        print(" ")
        downloader_main(osversion, radioversion, softwareversion,
                        localdir, debricks, radios, cores,
                        integrity, altsw)
        smeg = input("Press Enter to exit")
        if smeg or not smeg:
            raise SystemExit


def downloader_main(osversion, radioversion=None, softwareversion=None,
                    localdir=None, debricks=True, radios=True, cores=False,
                    integrity=True, altsw=None):
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

    :param integrity: Whether to test downloaded bar files. True by default.
    :type integrity: bool

    :param altsw: Radio software release, if not the same as OS.
    :type altsw: str
    """
    swchecked = False  # if we checked sw release already
    radioversion = scriptutils.return_radio_version(osversion, radioversion)
    softwareversion, swchecked = scriptutils.return_sw_checked(softwareversion,
                                                               osversion)
    if altsw:
        altsw, altchecked = scriptutils.return_radio_sw_checked(altsw,
                                                                radioversion)
    if localdir is None:
        localdir = os.getcwd()
    print("~~~DOWNLOADER VERSION", bbconstants.VERSION + "~~~")
    print("OS VERSION:", osversion)
    print("OS SOFTWARE VERSION:", softwareversion)
    print("RADIO VERSION:", radioversion)
    if altsw is not None:
        print("RADIO SOFTWARE VERSION:", altsw)

    baseurl = networkutils.create_base_url(softwareversion)
    if altsw:
        alturl = networkutils.create_base_url(altsw)
    osurls, radiourls, coreurls = utilities.generate_urls(baseurl,
                                                          osversion,
                                                          radioversion,
                                                          cores)
    vzwos, vzwrad = utilities.generate_lazy_urls(baseurl,
                                                 osversion,
                                                 radioversion,
                                                 2)  # Verizon
    osurls.append(vzwos)
    radiourls.append(vzwrad)
    vzwcore = vzwos.replace("sfi.desktop", "sfi")
    coreurls.append(vzwcore)
    if not networkutils.availability(osurls[1]):  # fallback to VZW
        osurls[1] = vzwos
        coreurls[1] = vzwcore
    osurls = list(set(osurls))  # pop duplicates
    radiourls = list(set(radiourls))
    coreurls = list(set(coreurls))
    if altsw:
        radiourls2 = []
        for rad in radiourls:
            radiourls2.append(rad.replace(baseurl, alturl))
        radiourls = radiourls2
        del radiourls2

    # Check availability of software releases
    scriptutils.check_sw(baseurl, softwareversion, swchecked)
    if altsw:
        scriptutils.check_radio_sw(alturl, altsw, altchecked)

    # Check availability of OS, radio
    if debricks:
        scriptutils.check_os_bulk(osurls)
    if cores:
        scriptutils.check_os_bulk(coreurls)
    if radios:
        radiourls, radioversion = scriptutils.check_radio_bulk(radiourls,
                                                               radioversion)

    # Download files
    print("BEGIN DOWNLOADING...")
    urllist = []
    if debricks:
        urllist += osurls
    if radios:
        urllist += radiourls
    if cores:
        urllist += coreurls
    if urllist:
        networkutils.download_bootstrap(urllist, localdir, workers=5)
        print("ALL FILES DOWNLOADED")
    else:
        print("NO FILES TO DOWNLOAD!")
        raise SystemExit

    # Test bar files
    if integrity:
        scriptutils.test_bar_files(localdir, urllist, True)
