#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, R0913, R0912, R0914, R0915
"""This module contains various utilities for the scripts folder."""

__author__ = "Thurask"
__license__ = "Do whatever"
__copyright__ = "2015 Thurask"


import os  # path work
import pprint  # pretty printing
import getpass  # invisible password
from bbarchivist import utilities  # little things
from bbarchivist import barutils  # file system work
from bbarchivist import bbconstants  # constants
from bbarchivist import filehashtools  # gpg
from bbarchivist import networkutils  # network tools


def return_radio_version(osversion, radioversion=None):
    """
    Increment radio version, if need be.

    :param osversion: OS version.
    :type osversion: str

    :param radioversion: Radio version, None if incremented.
    :type radioversion: str
    """
    if radioversion is None:
        radioversion = utilities.version_incrementer(osversion, 1)
    return radioversion


def return_sw_checked(softwareversion, osversion):
    """
    Check software existence, return boolean.

    :param softwareversion: Software release version.
    :type softwareversion: str

    :param osversion: OS version.
    :type osversion: str
    """
    if softwareversion is None:
        serv = bbconstants.SERVERS["p"]
        softwareversion = networkutils.software_release_lookup(osversion, serv)
        if softwareversion == "SR not in system":
            print("SOFTWARE RELEASE NOT FOUND")
            cont = utilities.str2bool(input("INPUT MANUALLY? Y/N: "))
            if cont:
                softwareversion = input("SOFTWARE RELEASE: ")
                swchecked = False
            else:
                print("\nEXITING...")
                raise SystemExit  # bye bye
        else:
            swchecked = True
    else:
        swchecked = True
    return softwareversion, swchecked


def return_radio_sw_checked(altsw, radioversion):
    """
    Check radio software existence, return boolean.

    :param altsw: Software release version.
    :type altsw: str

    :param radioversion: Radio version.
    :type radioversion: str
    """
    if altsw == "checkme":
        serv = bbconstants.SERVERS["p"]
        testos = utilities.version_incrementer(radioversion, -1)
        altsw = networkutils.software_release_lookup(testos, serv)
        if altsw == "SR not in system":
            print("RADIO SOFTWARE RELEASE NOT FOUND")
            cont = utilities.str2bool(input("INPUT MANUALLY? Y/N: "))
            if cont:
                altsw = input("SOFTWARE RELEASE: ")
                altchecked = False
            else:
                print("\nEXITING...")
                raise SystemExit  # bye bye
        else:
            altchecked = True
    else:
        altchecked = True
    return altsw, altchecked


def check_sw(baseurl, softwareversion, swchecked):
    """
    Check existence of software release.

    :param baseurl: Base URL (from http to hashed SW release).
    :type basurl: str

    :param softwareversion: Software release.
    :type softwareversion: str

    :param swchecked: If we checked the sw release already.
    :type swchecked: bool
    """
    print("CHECKING SOFTWARE RELEASE AVAILABILITY...")
    if not swchecked:
        avlty = networkutils.availability(baseurl)
        if avlty:
            print("SOFTWARE RELEASE", softwareversion, "EXISTS")
        else:
            print("SOFTWARE RELEASE", softwareversion, "NOT FOUND")
            cont = utilities.str2bool(input("CONTINUE? Y/N: "))
            if cont:
                pass
            else:
                print("\nEXITING...")
                raise SystemExit
    else:
        print("SOFTWARE RELEASE", softwareversion, "EXISTS")


def check_radio_sw(alturl, altsw):
    """
    Check existence of radio software release.

    :param alturl: Radio base URL (from http to hashed SW release).
    :type alturl: str

    :param altsw: Radio software release.
    :type altsw: str
    """
    if altsw:
        print("CHECKING RADIO SOFTWARE RELEASE...")
        altavlty = networkutils.availability(alturl)
        if altavlty:
            print("SOFTWARE RELEASE", altsw, "EXISTS")
        else:
            print("SOFTWARE RELEASE", altsw, "NOT FOUND")
            cont = utilities.str2bool(input("CONTINUE? Y/N: "))
            if cont:
                pass
            else:
                print("\nEXITING...")
                raise SystemExit


def check_os_single(osurl, osversion, device):
    """
    Check existence of single OS link.

    :param radiourl: Radio URL to check.
    :type radiourl: str

    :param radioversion: Radio version.
    :type radioversion: str

    :param device: Device family.
    :type device: int
    """
    osav = networkutils.availability(osurl)
    if not osav:
        print(osversion, "NOT AVAILABLE FOR", bbconstants.DEVICES[device])
        cont = utilities.str2bool(input("CONTINUE? Y/N: "))
        if cont:
            pass
        else:
            print("\nEXITING...")
            raise SystemExit


def check_os_bulk(osurls, osversion):
    """
    Check existence of list of OS links.

    :param osurls: OS URLs to check.
    :type osurls: list(str)

    :param osversion: OS version.
    :type osversion: str
    """
    for url in osurls:
        osav = networkutils.availability(url)
        if osav:
            break
    else:
        print("OS VERSION NOT FOUND")
        cont = utilities.str2bool(input("CONTINUE? Y/N: "))
        if cont:
            pass
        else:
            print("\nEXITING...")
            raise SystemExit


def check_radio_single(radiourl, radioversion):
    """
    Check existence of single radio link.

    :param radiourl: Radio URL to check.
    :type radiourl: str

    :param radioversion: Radio version.
    :type radioversion: str
    """
    radav = networkutils.availability(radiourl)
    if not radav:
        print("RADIO VERSION NOT FOUND")
        cont = utilities.str2bool(input("INPUT MANUALLY? Y/N: "))
        if cont:
            rad2 = input("RADIO VERSION: ")
            radiourl = radiourl.replace(radioversion, rad2)
            radioversion = rad2
        else:
            going = utilities.str2bool(input("KEEP GOING? Y/N: "))
            if going:
                pass
            else:
                print("\nEXITING...")
                raise SystemExit
    return radiourl, radioversion


def check_radio_bulk(radiourls, radioversion):
    """
    Check existence of list of radio links.

    :param radiourls: Radio URLs to check.
    :type radiourls: list(str)

    :param radioversion: Radio version.
    :type radioversion: str
    """
    for url in radiourls:
        radav = networkutils.availability(url)
        if radav:
            break
    else:
        print("RADIO VERSION NOT FOUND")
        cont = utilities.str2bool(input("INPUT MANUALLY? Y/N: "))
        if cont:
            rad2 = input("RADIO VERSION: ")
            radiourls = [url.replace(radioversion, rad2) for url in radiourls]
            radioversion = rad2
        else:
            going = utilities.str2bool(input("KEEP GOING? Y/N: "))
            if going:
                pass
            else:
                print("\nEXITING...")
                raise SystemExit
    return radiourls, radioversion


def get_sz_executable(compmethod):
    """
    Get 7z executable.

    :param compmethod: Compression method.
    :type compmethod: str
    """
    if not compmethod == "7z":
        szexe = ""
    else:
        print("CHECKING PRESENCE OF 7ZIP...")
        psz = utilities.prep_seven_zip(True)
        if psz:
            print("7ZIP OK")
            szexe = utilities.get_seven_zip(False)
        else:
            szexe = ""
            print("7ZIP NOT FOUND")
            cont = utilities.str2bool(input("CONTINUE? Y/N "))
            if cont:
                print("FALLING BACK TO ZIP...")
                compmethod = "zip"
            else:
                print("\nEXITING...")
                raise SystemExit  # bye bye
    return compmethod, szexe


def test_bar_files(localdir, urllist, download):
    """
    Test bar files after download.

    :param localdir: Directory.
    :type localdir: str

    :param urllist: List of URLs to check.
    :type urllist: list(str)

    :param download: If we downloaded these files ourselves.
    :type download: bool
    """
    brokenlist = []
    print("TESTING BAR FILES...")
    for file in os.listdir(localdir):
        if file.endswith(".bar"):
            print("TESTING:", file)
            thepath = os.path.abspath(os.path.join(localdir, file))
            brokens = barutils.bar_tester(thepath)
            if brokens is not None:
                os.remove(brokens)
                for url in urllist:
                    if brokens in url:
                        brokenlist.append(url)
    if brokenlist and download:
        print("REDOWNLOADING BROKEN FILES...")
        if len(brokenlist) > 5:
            workers = 5
        else:
            workers = len(brokenlist)
        networkutils.download_bootstrap(brokenlist,
                                        outdir=localdir,
                                        lazy=False,
                                        workers=workers)
        for file in os.listdir(localdir):
            if file.endswith(".bar"):
                thepath = os.path.abspath(os.path.join(localdir, file))
                brokens = barutils.bar_tester(thepath)
                if brokens is not None:
                    print(file, "STILL BROKEN")
                    raise SystemExit
    elif brokenlist and not download:
        print("SOME FILES ARE BROKEN!")
        pprint.pprint(brokenlist)
        raise SystemExit
    else:
        print("BAR FILES DOWNLOADED OK")


def test_signed_files(localdir):
    """
    Test signed files after extract.

    :param localdir: Directory.
    :type localdir: str
    """
    print("TESTING SIGNED FILES...")
    for file in os.listdir(localdir):
        if file.endswith(".bar"):
            print("TESTING:", file)
            signname, signhash = barutils.retrieve_sha512(file)
            sha512ver = barutils.verify_sha512(signname, signhash)
            if not sha512ver:
                print("{0} IS BROKEN".format((file)))
                break
    else:
        print("ALL FILES EXTRACTED OK")


def verify_gpg_credentials():
    """
    Read GPG key/pass from file, verify if incomplete.
    """
    gpgkey, gpgpass = filehashtools.gpg_config_loader()
    if gpgkey is None or gpgpass is None:
        print("NO PGP KEY/PASS FOUND")
        cont = utilities.str2bool(input("CONTINUE (Y/N)?: "))
        if cont:
            if gpgkey is None:
                gpgkey = input("PGP KEY (0x12345678): ")
                if gpgkey[:2] != "0x":
                    gpgkey = "0x" + gpgkey  # add preceding 0x
            if gpgpass is None:
                gpgpass = getpass.getpass(prompt="PGP PASSPHRASE: ")
                writebool = utilities.str2bool(input("WRITE PASSWORD TO FILE (Y/N)?:"))
            if writebool:
                gpgpass2 = gpgpass
            else:
                gpgpass2 = None
            filehashtools.gpg_config_writer(gpgkey, gpgpass2)
        else:
            gpgkey = None
    return gpgkey, gpgpass
