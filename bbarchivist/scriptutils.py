#!/usr/bin/env python3
"""This module contains various utilities for the scripts folder."""

import argparse  # generic parser
import collections  # defaultdict
import getpass  # invisible password
import glob  # file lookup
import hashlib  # hashes
import os  # path work
import shutil  # folder removal
import subprocess  # running cfp/cap
import sys  # getattr
import threading  # run stuff in background

import requests  # session
from bbarchivist import archiveutils  # archive support
from bbarchivist import barutils  # file system work
from bbarchivist import bbconstants  # constants
from bbarchivist import decorators  # decorating functions
from bbarchivist import gpgutils  # gpg
from bbarchivist import hashutils  # file hashes
from bbarchivist import networkutils  # network tools
from bbarchivist import smtputils  # email
from bbarchivist import sqlutils  # sql
from bbarchivist import textgenerator  # writing text to file
from bbarchivist import utilities  # little things

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2018 Thurask"


def shortversion():
    """
    Get short app version (Git tag).
    """
    if not getattr(sys, 'frozen', False):
        ver = bbconstants.VERSION
    else:
        verfile = glob.glob(os.path.join(os.getcwd(), "version.txt"))[0]
        with open(verfile) as afile:
            ver = afile.read()
    return ver


def longversion():
    """
    Get long app version (Git tag + commits + hash).
    """
    if not getattr(sys, 'frozen', False):
        ver = (bbconstants.LONGVERSION, bbconstants.COMMITDATE)
    else:
        verfile = glob.glob(os.path.join(os.getcwd(), "longversion.txt"))[0]
        with open(verfile) as afile:
            ver = afile.read().split("\n")
    return ver


def default_parser_vers(vers=None):
    """
    Prepare version for default parser.

    :param vers: Versions: [git commit hash, git commit date]
    :param vers: list(str)
    """
    if vers is None:
        vers = longversion()
    return vers


def default_parser_flags(parser, flags=None):
    """
    Handle flags for default parser.

    :param parser: Parser to modify.
    :type parser: argparse.ArgumentParser

    :param flags: Tuple of sections to add.
    :type flags: tuple(str)
    """
    if flags is not None:
        parser = dpf_flags_folder(parser, flags)
        parser = dpf_flags_osr(parser, flags)
    return parser


def dpf_flags_folder(parser, flags=None):
    """
    Add generic folder flag to parser.

    :param parser: Parser to modify.
    :type parser: argparse.ArgumentParser

    :param flags: Tuple of sections to add.
    :type flags: tuple(str)
    """
    if "folder" in flags:
        parser.add_argument("-f", "--folder", dest="folder", help="Working folder", default=None, metavar="DIR", type=utilities.file_exists)
    return parser


def dpf_flags_osr(parser, flags=None):
    """
    Add generic OS/radio/software flags to parser.

    :param parser: Parser to modify.
    :type parser: argparse.ArgumentParser

    :param flags: Tuple of sections to add.
    :type flags: tuple(str)
    """
    if "osr" in flags:
        parser.add_argument("os", help="OS version")
        parser.add_argument("radio", help="Radio version, 10.x.y.zzzz", nargs="?", default=None)
        parser.add_argument("swrelease", help="Software version, 10.x.y.zzzz", nargs="?", default=None)
    return parser


def default_parser(name=None, desc=None, flags=None, vers=None):
    """
    A generic form of argparse's ArgumentParser.

    :param name: App name.
    :type name: str

    :param desc: App description.
    :type desc: str

    :param flags: Tuple of sections to add.
    :type flags: tuple(str)

    :param vers: Versions: [git commit hash, git commit date]
    :param vers: list(str)
    """
    vers = default_parser_vers(vers)
    parser = argparse.ArgumentParser(prog=name, description=desc, epilog="https://github.com/thurask/bbarchivist")
    parser.add_argument("-v", "--version", action="version", version="{0} {1} committed {2}".format(parser.prog, vers[0], vers[1]))
    parser = default_parser_flags(parser, flags)
    return parser


def generic_windows_shim(scriptname, scriptdesc, target, version):
    """
    Generic CFP/CAP runner; Windows only.

    :param scriptname: Script name, 'bb-something'.
    :type scriptname: str

    :param scriptdesc: Script description, i.e. scriptname -h.
    :type scriptdesc: str

    :param target: Path to file to execute.
    :type target: str

    :param version: Version of target.
    :type version: str
    """
    parser = default_parser(scriptname, scriptdesc)
    capver = "|{0}".format(version)
    parser = external_version(parser, capver)
    parser.parse_known_args(sys.argv[1:])
    if utilities.is_windows():
        subprocess.call([target] + sys.argv[1:])
    else:
        print("Sorry, Windows only.")


def arg_verify_none(argval, message):
    """
    Check if an argument is None, error out if it is.

    :param argval: Argument to check.
    :type argval: str

    :param message: Error message to print.
    :type message: str
    """
    if argval is None:
        raise argparse.ArgumentError(argument=None, message=message)


def external_version(parser, addition):
    """
    Modify the version string of argparse.ArgumentParser, adding something.

    :param parser: Parser to modify.
    :type parser: argparse.ArgumentParser

    :param addition: What to add.
    :type addition: str
    """
    verarg = [arg for arg in parser._actions if isinstance(arg, argparse._VersionAction)][0]
    verarg.version = "{1}{0}".format(addition, verarg.version)
    return parser


def return_radio_version(osversion, radioversion=None):
    """
    Increment radio version, if need be.

    :param osversion: OS version.
    :type osversion: str

    :param radioversion: Radio version, None if incremented.
    :type radioversion: str
    """
    if radioversion is None:
        radioversion = utilities.increment(osversion, 1)
    return radioversion


def sw_check_contingency(softwareversion):
    """
    Ask in the event software release isn't found.

    :param softwareversion: Software release version.
    :type softwareversion: str
    """
    if softwareversion == "SR not in system":
        print("SOFTWARE RELEASE NOT FOUND")
        cont = utilities.i2b("INPUT MANUALLY? Y/N: ")
        if cont:
            softwareversion = input("SOFTWARE RELEASE: ")
            swchecked = False
        else:
            print("\nEXITING...")
            raise SystemExit  # bye bye
    else:
        swchecked = True
    return softwareversion, swchecked


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
        softwareversion = networkutils.sr_lookup(osversion, serv)
        softwareversion, swchecked = sw_check_contingency(softwareversion)
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
        testos = utilities.increment(radioversion, -1)
        altsw = networkutils.sr_lookup(testos, serv)
        altsw, altchecked = sw_check_contingency(altsw)
    else:
        altchecked = True
    return altsw, altchecked


def check_sw(baseurl, softwareversion, swchecked, altsw=False):
    """
    Check existence of software release.

    :param baseurl: Base URL (from http to hashed SW release).
    :type baseurl: str

    :param softwareversion: Software release.
    :type softwareversion: str

    :param swchecked: If we checked the sw release already.
    :type swchecked: bool

    :param altsw: If this is the radio-only release. Default is false.
    :type altsw: bool
    """
    message = "CHECKING RADIO SOFTWARE RELEASE..." if altsw else "CHECKING SOFTWARE RELEASE..."
    print(message)
    if not swchecked:
        check_sw_actual(baseurl, softwareversion)
    else:
        print("SOFTWARE RELEASE {0} EXISTS".format(softwareversion))


def check_sw_actual(baseurl, softwareversion):
    """
    Get the status of a software release.

    :param baseurl: Base URL (from http to hashed SW release).
    :type baseurl: str

    :param softwareversion: Software release.
    :type softwareversion: str
    """
    avlty = networkutils.availability(baseurl)
    if avlty:
        print("SOFTWARE RELEASE {0} EXISTS".format(softwareversion))
    else:
        check_sw_handle(softwareversion)


def check_sw_handle(softwareversion):
    """
    Handle non-existent software release.

    :param softwareversion: Software release.
    :type softwareversion: str
    """
    print("SOFTWARE RELEASE {0} NOT FOUND".format(softwareversion))
    cont = utilities.i2b("CONTINUE? Y/N: ")
    if not cont:
        print("\nEXITING...")
        raise SystemExit


def check_radio_sw(alturl, altsw, altchecked):
    """
    Check existence of radio software release.

    :param alturl: Radio base URL (from http to hashed SW release).
    :type alturl: str

    :param altsw: Radio software release.
    :type altsw: str

    :param altchecked: If we checked the sw release already.
    :type altchecked: bool
    """
    return check_sw(alturl, altsw, altchecked, True)


def check_altsw(altcheck=False):
    """
    Ask for and return alternate software release, if needed.

    :param altcheck: If we're using an alternate software release.
    :type altcheck: bool
    """
    if altcheck:
        altsw = input("RADIO SOFTWARE RELEASE (PRESS ENTER TO GUESS): ")
        if not altsw:
            altsw = "checkme"
    else:
        altsw = None
    return altsw


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
        print("{0} NOT AVAILABLE FOR {1}".format(osversion, bbconstants.DEVICES[device]))
        cont = utilities.i2b("CONTINUE? Y/N: ")
        if not cont:
            print("\nEXITING...")
            raise SystemExit


def check_os_bulk(osurls):
    """
    Check existence of list of OS links.

    :param osurls: OS URLs to check.
    :type osurls: list(str)
    """
    sess = requests.Session()
    for url in osurls:
        osav = networkutils.availability(url, sess)
        if osav:
            break
    else:
        check_os_bulk_handle()


def check_os_bulk_handle():
    """
    Handle no existing OS links.
    """
    print("OS VERSION NOT FOUND")
    cont = utilities.i2b("CONTINUE? Y/N: ")
    if not cont:
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
        cont = utilities.i2b("INPUT MANUALLY? Y/N: ")
        if cont:
            rad2 = input("RADIO VERSION: ")
            radiourl = radiourl.replace(radioversion, rad2)
            radioversion = rad2
        else:
            going = utilities.i2b("KEEP GOING? Y/N: ")
            if not going:
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
    sess = requests.Session()
    for url in radiourls:
        radav = networkutils.availability(url, sess)
        if radav:
            break
    else:
        radiourls, radioversion = check_radio_bulk_notfound(radiourls, radioversion)
    return radiourls, radioversion


def check_radio_bulk_notfound(radiourls, radioversion):
    """
    What to do if radio links aren't found.

    :param radiourls: Radio URLs to check.
    :type radiourls: list(str)

    :param radioversion: Radio version.
    :type radioversion: str
    """
    print("RADIO VERSION NOT FOUND")
    cont = utilities.i2b("INPUT MANUALLY? Y/N: ")
    if cont:
        radiourls, radioversion = check_radio_bulk_go(radiourls, radioversion)
    else:
        check_radio_bulk_stop()
    return radiourls, radioversion


def check_radio_bulk_go(radiourls, radioversion):
    """
    Replace radio version and URLs, and keep going.

    :param radiourls: Radio URLs to check.
    :type radiourls: list(str)

    :param radioversion: Radio version.
    :type radioversion: str
    """
    rad2 = input("RADIO VERSION: ")
    radiourls = [url.replace(radioversion, rad2) for url in radiourls]
    radioversion = rad2
    return radiourls, radioversion


def check_radio_bulk_stop():
    """
    Ask if we should keep going once no radio has been found.
    """
    going = utilities.i2b("KEEP GOING? Y/N: ")
    if not going:
        print("\nEXITING...")
        raise SystemExit


def bulk_avail(urllist):
    """
    Filter 404 links out of URL list.

    :param urllist: URLs to check.
    :type urllist: list(str)
    """
    sess = requests.Session()
    url2 = [x for x in urllist if networkutils.availability(x, sess)]
    return url2


def get_baseurls(softwareversion, altsw=None):
    """
    Generate base URLs for bar links.

    :param softwareversion: Software version.
    :type softwareversion: str

    :param altsw: Radio software version, if necessary.
    :type altsw: str
    """
    baseurl = utilities.create_base_url(softwareversion)
    alturl = utilities.create_base_url(altsw) if altsw else None
    return baseurl, alturl


def get_sz_executable(compmethod):
    """
    Get 7z executable.

    :param compmethod: Compression method.
    :type compmethod: str
    """
    if compmethod != "7z":
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
            cont = utilities.i2b("CONTINUE? Y/N ")
            if cont:
                print("FALLING BACK TO ZIP...")
                compmethod = "zip"
            else:
                print("\nEXITING...")
                raise SystemExit  # bye bye
    return compmethod, szexe


def test_bar_files(localdir, urllist):
    """
    Test bar files after download.

    :param localdir: Directory.
    :type localdir: str

    :param urllist: List of URLs to check.
    :type urllist: list(str)
    """
    print("TESTING BAR FILES...")
    brokenlist = []
    for file in os.listdir(localdir):
        brokenlist = test_bar_files_individual(file, localdir, urllist, brokenlist)
    if brokenlist:
        print("SOME FILES ARE BROKEN!")
        utilities.lprint(brokenlist)
        raise SystemExit
    else:
        print("BAR FILES DOWNLOADED OK")


def test_bar_files_individual(file, localdir, urllist, brokenlist):
    """
    Test bar file after download.

    :param file: Bar file to check.
    :type file: str

    :param localdir: Directory.
    :type localdir: str

    :param urllist: List of URLs to check.
    :type urllist: list(str)

    :param brokenlist: List of URLs to download later.
    :type brokenlist: list(str)
    """
    if file.endswith(".bar"):
        print("TESTING: {0}".format(file))
        thepath = os.path.abspath(os.path.join(localdir, file))
        brokens = barutils.bar_tester(thepath)
        brokenlist = bar_broken_individual(brokens, urllist, brokenlist)
    return brokenlist


def bar_broken_individual(brokens, urllist, brokenlist):
    """
    What to do if a downloaded bar file is broken.

    :param brokens: None if bar is OK, filename if it is not.
    :type brokens: str

    :param urllist: List of URLs to check.
    :type urllist: list(str)

    :param brokenlist: List of URLs to download later.
    :type brokenlist: list(str)
    """
    if brokens is not None:
        os.remove(brokens)
        for url in urllist:
            if brokens in url:
                brokenlist.append(url)
    return brokenlist


def test_signed_files(localdir):
    """
    Test signed files after extract.

    :param localdir: Directory.
    :type localdir: str
    """
    print("TESTING SIGNED FILES...")
    for file in os.listdir(localdir):
        if file.endswith(".bar"):
            print("TESTING: {0}".format(file))
            signname, signhash = barutils.retrieve_sha512(os.path.join(localdir, file))
            sha512ver = barutils.verify_sha512(os.path.join(localdir, signname.decode("utf-8")), signhash)
            if not sha512ver:
                print("{0} IS BROKEN".format((file)))
                break
    else:
        print("ALL FILES EXTRACTED OK")


def test_loader_files(localdir):
    """
    Test loader files after creation.

    :param localdir: Directory.
    :type localdir: str
    """
    if not utilities.is_windows():
        pass
    else:
        print("TESTING LOADER FILES...")
        brokens = utilities.verify_bulk_loaders(localdir)
        if brokens:
            print("BROKEN FILES:")
            utilities.lprint(brokens)
            raise SystemExit
        else:
            print("ALL FILES CREATED OK")


def test_single_loader(loaderfile):
    """
    Test single loader file after creation.

    :param loaderfile: File to check.
    :type loaderfile: str
    """
    if not utilities.is_windows():
        pass
    else:
        print("TESTING LOADER...")
        if not utilities.verify_loader_integrity(loaderfile):
            print("{0} IS BROKEN!".format(os.path.basename(loaderfile)))
            raise SystemExit
        else:
            print("LOADER CREATED OK")


def prod_avail(results, mailer=False, osversion=None, password=None):
    """
    Clean availability for production lookups for autolookup script.

    :param results: Result dict.
    :type results: dict(str: str)

    :param mailer: If we're mailing links. Default is false.
    :type mailer: bool

    :param osversion: OS version.
    :type osversion: str

    :param password: Email password.
    :type password: str
    """
    prel = results['p']
    if prel != "SR not in system" and prel is not None:
        pav = "PD"
        baseurl = utilities.create_base_url(prel)
        avail = networkutils.availability(baseurl)
        is_avail = "Available" if avail else "Unavailable"
        prod_avail_mailprep(prel, avail, osversion, mailer, password)
    else:
        pav = "  "
        is_avail = "Unavailable"
    return prel, pav, is_avail


def prod_avail_mailprep(prel, avail, osversion=None, mailer=False, password=None):
    """
    Do SQL/SMTP prep work after a good production lookup hit.

    :param prel: Software lookup result.
    :type prel: str

    :param avail: If software lookup result is available for download.
    :type avail: bool

    :param osversion: OS version.
    :type osversion: str

    :param mailer: If we're mailing links. Default is false.
    :type mailer: bool

    :param password: Email password.
    :type password: str
    """
    if avail and mailer:
        sqlutils.prepare_sw_db()
        if not sqlutils.check_exists(osversion, prel):
            rad = utilities.increment(osversion, 1)
            linkgen(osversion, rad, prel, temp=True)
            smtputils.prep_email(osversion, prel, password)


def comp_joiner(rootdir, localdir, filelist):
    """
    Join rootdir, localdir to every file in filelist.

    :param rootdir: Root directory.
    :type rootdir: str

    :param localdir: Subfolder inside rootdir.
    :type localdir: str

    :param filelist: List of files to return this path for.
    :type filelist: list(str)
    """
    joinedfiles = [os.path.join(rootdir, localdir, os.path.basename(x)) for x in filelist]
    return joinedfiles


def kernchecker_prep(kernlist):
    """
    Prepare output from kernel list.

    :param kernlist: List of kernel branches.
    :type kernlist: list(str)
    """
    splitkerns = [x.split("/") for x in kernlist]
    platforms = list({x[0] for x in splitkerns})
    kerndict = kernchecker_dict(splitkerns, platforms)
    return kerndict


def kernchecker_dict(splitkerns, platforms):
    """
    Prepare results dictionary.

    :param splitkerns: Split kernel branches.
    :type splitkerns: list(str)

    :param platforms: List of platform dicts.
    :type platforms: list(dict)
    """
    kerndict = {x: [] for x in platforms}
    for kernel in splitkerns:
        kerndict[kernel[0]].append("\t{0}".format(kernel[1]))
    return kerndict


def tclloader_prep(loaderfile, directory=False):
    """
    Prepare directory name and OS version.

    :param loaderfile: Path to input file/folder.
    :type loaderfile: str

    :param directory: If the input file is a folder. Default is False.
    :type directory: bool
    """
    loaderdir = loaderfile if directory else loaderfile.replace(".zip", "")
    osver = loaderdir.split("-")[-1]
    return loaderdir, osver


def tclloader_filename(loaderdir, osver, loadername=None):
    """
    Prepare platform and filename.

    :param loaderdir: Path to input folder.
    :type loaderdir: str

    :param osver: OS version.
    :type osver: str

    :param loadername: Name of final autoloader. Default is auto-generated.
    :type loadername: str
    """
    platform = os.listdir(os.path.join(loaderdir, "target", "product"))[0]
    if loadername is None:
        loadername = "{0}_autoloader_user-all-{1}".format(platform, osver)
    return loadername, platform


def tcl_download(downloadurl, filename, filesize, filehash):
    """
    Download autoloader file, rename, and verify.

    :param downloadurl: Download URL.
    :type downloadurl: str

    :param filename: Name of autoloader file.
    :type filename: str

    :param filesize: Size of autoloader file.
    :type filesize: str

    :param filehash: SHA-1 hash of autoloader file.
    :type filehash: str
    """
    print("FILENAME: {0}".format(filename))
    print("LENGTH: {0}".format(utilities.fsizer(filesize)))
    networkutils.download(downloadurl)
    print("DOWNLOAD COMPLETE")
    os.rename(downloadurl.split("/")[-1], filename)
    method = hashutils.get_engine("sha1")
    shahash = hashutils.hashlib_hash(filename, method)
    if shahash == filehash:
        print("HASH CHECK OK")
    else:
        print(shahash)
        print("HASH FAILED!")


def tcl_prd_scan(curef, download=False, mode=4, fvver="AAA000", original=True, export=False):
    """
    Scan one PRD and produce download URL and filename.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param download: If we'll download the file that this returns. Default is False.
    :type download: bool

    :param mode: 4 if downloading autoloaders, 2 if downloading OTA deltas.
    :type mode: int

    :param fvver: Initial software version, must be specific if downloading OTA deltas.
    :type fvver: str

    :param original: If we'll download the file with its original filename instead of delta-safe. Default is True.
    :type original: bool

    :param export: Whether to export XML response to file. Default is False.
    :type export: bool
    """
    sess = requests.Session()
    ctext = networkutils.tcl_check(curef, sess, mode, fvver, export)
    if ctext is None:
        raise SystemExit
    tvver, firmwareid, filename, filesize, filehash = networkutils.parse_tcl_check(ctext)
    salt = networkutils.tcl_salt()
    vkhsh = networkutils.vkhash(curef, tvver, firmwareid, salt, mode, fvver)
    updatetext = networkutils.tcl_download_request(curef, tvver, firmwareid, salt, vkhsh, sess, mode, fvver, export)
    downloadurl, encslave = networkutils.parse_tcl_download_request(updatetext)
    statcode = networkutils.getcode(downloadurl, sess)
    filename = tcl_delta_filename(curef, fvver, tvver, filename, original)
    tcl_prd_print(downloadurl, filename, statcode, encslave, sess)
    if statcode == 200 and download:
        tcl_download(downloadurl, filename, filesize, filehash)


def tcl_delta_filename(curef, fvver, tvver, filename, original=True):
    """
    Generate compatible filenames for deltas, if needed.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param fvver: Initial software version.
    :type fvver: str

    :param tvver: Target software version.
    :type tvver: str

    :param filename: File name from download URL, passed through if not changing filename.
    :type filename: str

    :param original: If we'll download the file with its original filename instead of delta-safe. Default is True.
    :type original: bool
    """
    if not original:
        prdver = curef.split("-")[1]
        filename = "JSU_PRD-{0}-{1}to{2}.zip".format(prdver, fvver, tvver)
    return filename


def tcl_prd_print(downloadurl, filename, statcode, encslave, session):
    """
    Print output from PRD scanning.

    :param downloadurl: File to download.
    :type downloadurl: str

    :param filename: File name from download URL.
    :type filename: str

    :param statcode: Status code of download URL.
    :type statcode: int

    :param encslave: Server hosting header script.
    :type encslave: str

    :param session: Session object.
    :type session: requests.Session
    """
    print("{0}: HTTP {1}".format(filename, statcode))
    print(downloadurl)
    if encslave is not None:
        address = "/{0}".format(downloadurl.split("/", 3)[3:][0])
        print("CHECKING HEADER...")
        sentinel = networkutils.encrypt_header(address, encslave, session)
        if sentinel is not None:
            print(sentinel)


def tcl_prep_otaver(ota=None):
    """
    Prepare variables for OTA versus full check.

    :param ota: The starting version if we're checking OTA updates, None if we're not. Default is None.
    :type ota: str
    """
    if ota is not None:
        mode = 2
        fvver = ota
    else:
        mode = 4
        fvver = "AAA000"
    return mode, fvver


def tcl_mainscan_preamble(ota=None):
    """
    Prepare preamble for TCL scanning.

    :param ota: The starting version if we're checking OTA updates, None if we're not. Default is None.
    :type ota: str
    """
    slim_preamble("TCLSCAN")
    if ota is not None:
        print("PRDs with OTA from OS {0}".format(ota.upper()))


def tcl_mainscan_printer(curef, tvver, ota=None):
    """
    Print output of TCL scanning.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param tvver: Target software version.
    :type tvver: str

    :param ota: The starting version if we're checking OTA updates, None if we're not. Default is None.
    :type ota: str
    """
    if ota is not None:
        print("{0}: {2} to {1}".format(curef, tvver, ota.upper()))
    else:
        print("{0}: {1}".format(curef, tvver))


def tcl_findprd_prepd_start(prddict):
    """
    Collect list of PRD entries.

    :param prddict: Device:PRD dictionary.
    :type prddict: dict(str: list)
    """
    prda = []
    for item in prddict.values():
        prda.extend(item)
    return prda


def tcl_findprd_prepd_middle(prda):
    """
    Convert PRD entries to list of center:end entries.

    :param prda: List of PRD-xxxxx-yyy entries.
    :type prda: list(str)
    """
    prds = [x.split(" ")[0].replace("PRD-", "").split("-") for x in prda]
    prdx = list({x[0]: x[1]} for x in prds)
    return prdx


def tcl_findprd_prepd_end(prdx):
    """
    Convert list of center:end entries to final center:[ends] dict.

    :param prdx: List of center:end dict entries.
    :type prdx: list(dict(str: str))
    """
    prdf = collections.defaultdict(list)
    for prdc in prdx:
        for key, value in prdc.items():
            prdf[key].append(value)
    return prdf


def tcl_findprd_prepdict(prddict):
    """
    Prepare dict of center:[ends] entries.

    :param prddict: Device:PRD dictionary.
    :type prddict: dict(str: list)
    """
    prda = tcl_findprd_prepd_start(prddict)
    prdx = tcl_findprd_prepd_middle(prda)
    prdfinal = tcl_findprd_prepd_end(prdx)
    return prdfinal


def tcl_findprd_checkfilter(prddict, tocheck=None):
    """
    Filter PRD dict if needed.

    :param prddict: PRD center:[ends] dictionary.
    :type prddict: collections.defaultdict(str: list)

    :param tocheck: Specific PRD(s) to check, None if we're checking all variants in database. Default is None.
    :type tocheck: list(str)
    """
    prddict2 = prddict
    if tocheck is not None:
        prddict2 = collections.defaultdict(list)
        for toch in tocheck:
            toch = toch.replace("PRD-", "")
            prddict2[toch] = prddict[toch]
    return prddict2


def tcl_findprd_centerscan(center, prddict, session, floor=0, ceiling=999, export=False):
    """
    Individual scanning for the center of a PRD.

    :param center: PRD-center-end.
    :type center: str

    :param prddict: PRD center:[ends] dictionary.
    :type prddict: collections.defaultdict(str: list)

    :param session: Session object.
    :type session: requests.Session

    :param floor: When to start. Default is 0.
    :type floor: int

    :param ceiling: When to stop. Default is 999.
    :type ceiling: int

    :param export: Whether to export XML response to file. Default is False.
    :type export: bool
    """
    tails = [int(i) for i in prddict[center]]
    safes = [g for g in range(floor, ceiling) if g not in tails]
    print("SCANNING ROOT: {0}{1}".format(center, " "*8))
    tcl_findprd_safescan(safes, center, session, export)


def tcl_findprd_safescan(safes, center, session, export=False):
    """
    Scan for PRDs known not to be in database.

    :param safes: List of ends within given range that aren't in database.
    :type safes: list(int)

    :param center: PRD-center-end.
    :type center: str

    :param session: Session object.
    :type session: requests.Session

    :param export: Whether to export XML response to file. Default is False.
    :type export: bool
    """
    for j in safes:
        curef = "PRD-{}-{:03}".format(center, j)
        print("NOW SCANNING: {0}".format(curef), end="\r")
        checktext = networkutils.tcl_check(curef, session, export)
        if checktext is None:
            continue
        else:
            tcl_findprd_safehandle(curef, checktext)


def tcl_findprd_safehandle(curef, checktext):
    """
    Parse API output and print the relevant bits.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param checktext: The XML formatted data returned from the first stage API check.
    :type checktext: str
    """
    tvver, firmwareid, filename, fsize, fhash = networkutils.parse_tcl_check(checktext)
    del firmwareid, filename, fsize, fhash
    tvver2 = "{0}{1}".format(tvver, " "*8)
    tcl_mainscan_printer(curef, tvver2)


def tcl_findprd(prddict, floor=0, ceiling=999, export=False):
    """
    Check for new PRDs based on PRD database.

    :param prddict: PRD center:[ends] dictionary.
    :type prddict: collections.defaultdict(str: list)

    :param floor: When to start. Default is 0.
    :type floor: int

    :param ceiling: When to stop. Default is 999.
    :type ceiling: int

    :param export: Whether to export XML response to file. Default is False.
    :type export: bool
    """
    sess = requests.Session()
    for center in sorted(prddict.keys()):
        tcl_findprd_centerscan(center, prddict, sess, floor, ceiling, export)


def linkgen_sdk_dicter(indict, origtext, newtext):
    """
    Prepare SDK radio/OS dictionaries.

    :param indict: Dictionary of radio and OS pairs.
    :type: dict(str:str)

    :param origtext: String in indict's values that must be replaced.
    :type origtext: str

    :param newtext: What to replace origtext with.
    :type newtext: str
    """
    return {key: val.replace(origtext, newtext) for key, val in indict.items()}


def linkgen_sdk(sdk, oses, cores):
    """
    Generate SDK debrick/core images.

    :param sdk: If we specifically want SDK images. Default is False.
    :type sdk: bool

    :param oses: Dictionary of radio and debrick pairs.
    :type oses: dict(str:str)

    :param cores: Dictionary of radio and core pairs.
    :type cores: dict(str:str)
    """
    if sdk:
        oses2 = linkgen_sdk_dicter(oses, "factory_sfi", "sdk")
        cores2 = linkgen_sdk_dicter(cores, "factory_sfi", "sdk")
        oses = linkgen_sdk_dicter(oses2, "verizon_sfi", "sdk")
        cores = linkgen_sdk_dicter(cores2, "verizon_sfi", "sdk")
    return oses, cores


def linkgen(osversion, radioversion=None, softwareversion=None, altsw=None, temp=False, sdk=False):
    """
    Generate debrick/core/radio links for given OS, radio, software release.

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz. Can be guessed.
    :type radioversion: str

    :param softwareversion: Software version, 10.x.y.zzzz. Can be guessed.
    :type softwareversion: str

    :param altsw: Radio software release, if not the same as OS.
    :type altsw: str

    :param temp: If file we write to is temporary. Default is False.
    :type temp: bool

    :param sdk: If we specifically want SDK images. Default is False.
    :type sdk: bool
    """
    radioversion = return_radio_version(osversion, radioversion)
    softwareversion, swc = return_sw_checked(softwareversion, osversion)
    del swc
    if altsw is not None:
        altsw, aswc = return_radio_sw_checked(altsw, radioversion)
        del aswc
    baseurl = utilities.create_base_url(softwareversion)
    oses, cores, radios = textgenerator.url_gen(osversion, radioversion, softwareversion)
    if altsw is not None:
        del radios
        dbks, cors, radios = textgenerator.url_gen(osversion, radioversion, altsw)
        del dbks
        del cors
    avlty = networkutils.availability(baseurl)
    oses, cores = linkgen_sdk(sdk, oses, cores)
    prargs = (softwareversion, osversion, radioversion, oses, cores, radios, avlty, False, None, temp, altsw)
    lthr = threading.Thread(target=textgenerator.write_links, args=prargs)
    lthr.start()


def clean_swrel(swrelset):
    """
    Clean a list of software release lookups.

    :param swrelset: List of software releases.
    :type swrelset: set(str)
    """
    for i in swrelset:
        if i != "SR not in system" and i is not None:
            swrelease = i
            break
    else:
        swrelease = ""
    return swrelease


def autolookup_logger(record, out):
    """
    Write autolookup results to file.

    :param record: The file to log to.
    :type record: str

    :param out: Output block.
    :type out: str
    """
    with open(record, "a") as rec:
        rec.write("{0}\n".format(out))


def autolookup_printer(out, avail, log=False, quiet=False, record=None):
    """
    Print autolookup results, logging if specified.

    :param out: Output block.
    :type out: str

    :param avail: Availability. Can be "Available" or "Unavailable".
    :type avail: str

    :param log: If we're logging to file.
    :type log: bool

    :param quiet: If we only note available entries.
    :type quiet: bool

    :param record: If we're logging, the file to log to.
    :type record: str
    """
    if not quiet:
        avail = "Available"  # force things
    if avail.lower() == "available":
        if log:
            lthr = threading.Thread(target=autolookup_logger, args=(record, out))
            lthr.start()
        print(out)


def autolookup_output_sql(osversion, swrelease, avail, sql=False):
    """
    Add OS to SQL database.

    :param osversion: OS version.
    :type osversion: str

    :param swrelease: Software release.
    :type swrelease: str

    :param avail: "Unavailable" or "Available".
    :type avail: str

    :param sql: If we're adding this to our SQL database.
    :type sql: bool
    """
    if sql:
        sqlutils.prepare_sw_db()
        if not sqlutils.check_exists(osversion, swrelease):
            sqlutils.insert(osversion, swrelease, avail.lower())


def autolookup_output(osversion, swrelease, avail, avpack, sql=False):
    """
    Prepare autolookup block, and add to SQL database.

    :param osversion: OS version.
    :type osversion: str

    :param swrelease: Software release.
    :type swrelease: str

    :param avail: "Unavailable" or "Available".
    :type avail: str

    :param avpack: Availabilities: alpha 1 and 2, beta 1 and 2, production.
    :type avpack: list(str)

    :param sql: If we're adding this to our SQL database.
    :type sql: bool
    """
    othr = threading.Thread(target=autolookup_output_sql, args=(osversion, swrelease, avail, sql))
    othr.start()
    avblok = "[{0}|{1}|{2}|{3}|{4}]".format(*avpack)
    out = "OS {0} - SR {1} - {2} - {3}".format(osversion, swrelease, avblok, avail)
    return out


def clean_barlist(cleanfiles, stoppers):
    """
    Remove certain bars from barlist based on keywords.

    :param cleanfiles: List of files to clean.
    :type cleanfiles: list(str)

    :param stoppers: List of keywords (i.e. bar names) to exclude.
    :type stoppers: list(str)
    """
    finals = [link for link in cleanfiles if all(word not in link for word in stoppers)]
    return finals


def prep_export_cchecker(files, npc, hwid, osv, radv, swv, upgrade=False, forced=None):
    """
    Prepare carrierchecker lookup links to write to file.

    :param files: List of file URLs.
    :type files: list(str)

    :param npc: MCC + MNC (ex. 302220).
    :type npc: int

    :param hwid: Device hardware ID.
    :type hwid: str

    :param osv: OS version.
    :type osv: str

    :param radv: Radio version.
    :type radv: str

    :param swv: Software release.
    :type swv: str

    :param upgrade: Whether or not to use upgrade files. Default is false.
    :type upgrade: bool

    :param forced: Force a software release. None to go for latest.
    :type forced: str
    """
    if not upgrade:
        newfiles = networkutils.carrier_query(npc, hwid, True, False, forced)
        cleanfiles = newfiles[3]
    else:
        cleanfiles = files
    osurls, coreurls, radiourls = textgenerator.url_gen(osv, radv, swv)
    stoppers = ["8960", "8930", "8974", "m5730", "winchester"]
    finals = clean_barlist(cleanfiles, stoppers)
    return osurls, coreurls, radiourls, finals


def export_cchecker(files, npc, hwid, osv, radv, swv, upgrade=False, forced=None):
    """
    Write carrierchecker lookup links to file.

    :param files: List of file URLs.
    :type files: list(str)

    :param npc: MCC + MNC (ex. 302220).
    :type npc: int

    :param hwid: Device hardware ID.
    :type hwid: str

    :param osv: OS version.
    :type osv: str

    :param radv: Radio version.
    :type radv: str

    :param swv: Software release.
    :type swv: str

    :param upgrade: Whether or not to use upgrade files. Default is false.
    :type upgrade: bool

    :param forced: Force a software release. None to go for latest.
    :type forced: str
    """
    if files:
        osurls, coreurls, radiourls, finals = prep_export_cchecker(files, npc, hwid, osv, radv, swv, upgrade, forced)
        textgenerator.write_links(swv, osv, radv, osurls, coreurls, radiourls, True, True, finals)
        print("\nFINISHED!!!")
    else:
        print("CANNOT EXPORT, NO SOFTWARE RELEASE")


def generate_blitz_links(files, osv, radv, swv):
    """
    Generate blitz URLs (i.e. all OS and radio links).
    :param files: List of file URLs.
    :type files: list(str)

    :param osv: OS version.
    :type osv: str

    :param radv: Radio version.
    :type radv: str

    :param swv: Software release.
    :type swv: str
    """
    coreurls = [
        utilities.create_bar_url(swv, "winchester.factory_sfi", osv),
        utilities.create_bar_url(swv, "qc8960.factory_sfi", osv),
        utilities.create_bar_url(swv, "qc8960.factory_sfi", osv),
        utilities.create_bar_url(swv, "qc8960.factory_sfi_hybrid_qc8974", osv)
    ]
    radiourls = [
        utilities.create_bar_url(swv, "m5730", radv),
        utilities.create_bar_url(swv, "qc8960", radv),
        utilities.create_bar_url(swv, "qc8960.wtr", radv),
        utilities.create_bar_url(swv, "qc8960.wtr5", radv),
        utilities.create_bar_url(swv, "qc8930.wtr5", radv),
        utilities.create_bar_url(swv, "qc8974.wtr2", radv)
    ]
    return files + coreurls + radiourls


def package_blitz(bardir, swv):
    """
    Package and verify a blitz package.

    :param bardir: Path to folder containing bar files.
    :type bardir: str

    :param swv: Software version.
    :type swv: str
    """
    print("\nCREATING BLITZ...")
    barutils.create_blitz(bardir, swv)
    print("\nTESTING BLITZ...")
    zipver = archiveutils.zip_verify("Blitz-{0}.zip".format(swv))
    if not zipver:
        print("BLITZ FILE IS BROKEN")
        raise SystemExit
    else:
        shutil.rmtree(bardir)


def slim_preamble(appname):
    """
    Standard app name header.

    :param appname: Name of app.
    :type appname: str
    """
    print("~~~{0} VERSION {1}~~~".format(appname.upper(), shortversion()))


def standard_preamble(appname, osversion, softwareversion, radioversion, altsw=None):
    """
    Standard app name, OS, radio and software (plus optional radio software) print block.

    :param appname: Name of app.
    :type appname: str

    :param osversion: OS version, 10.x.y.zzzz. Required.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz. Can be guessed.
    :type radioversion: str

    :param softwareversion: Software release, 10.x.y.zzzz. Can be guessed.
    :type softwareversion: str

    :param altsw: Radio software release, if not the same as OS.
    :type altsw: str
    """
    slim_preamble(appname)
    print("OS VERSION: {0}".format(osversion))
    print("OS SOFTWARE VERSION: {0}".format(softwareversion))
    print("RADIO VERSION: {0}".format(radioversion))
    if altsw is not None:
        print("RADIO SOFTWARE VERSION: {0}".format(altsw))


def questionnaire_device(message=None):
    """
    Get device from questionnaire.
    """
    message = "DEVICE (XXX100-#): " if message is None else message
    device = input(message)
    if not device:
        print("NO DEVICE SPECIFIED!")
        decorators.enter_to_exit(True)
        if not getattr(sys, 'frozen', False):
            raise SystemExit
    return device


def verify_gpg_credentials():
    """
    Read GPG key/pass from file, verify if incomplete.
    """
    gpgkey, gpgpass = gpgutils.gpg_config_loader()
    if gpgkey is None or gpgpass is None:
        print("NO PGP KEY/PASS FOUND")
        cont = utilities.i2b("CONTINUE (Y/N)?: ")
        if cont:
            gpgkey = verify_gpg_key(gpgkey)
            gpgpass, writebool = verify_gpg_pass(gpgpass)
            gpgpass2 = gpgpass if writebool else None
            gpgutils.gpg_config_writer(gpgkey, gpgpass2)
        else:
            gpgkey = None
    return gpgkey, gpgpass


def verify_gpg_key(gpgkey=None):
    """
    Verify GPG key.

    :param gpgkey: Key, use None to take from input.
    :type gpgkey: str
    """
    if gpgkey is None:
        gpgkey = input("PGP KEY (0x12345678): ")
        if not gpgkey.startswith("0x"):
            gpgkey = "0x{0}".format(gpgkey)   # add preceding 0x
    return gpgkey


def verify_gpg_pass(gpgpass=None):
    """
    Verify GPG passphrase.

    :param gpgpass: Passphrase, use None to take from input.
    :type gpgpass: str
    """
    if gpgpass is None:
        gpgpass = getpass.getpass(prompt="PGP PASSPHRASE: ")
        writebool = utilities.i2b("SAVE PASSPHRASE (Y/N)?:")
    else:
        writebool = False
    return gpgpass, writebool


def bulk_hash(dirs, compressed=True, deleted=True, radios=True, hashdict=None):
    """
    Hash files in several folders based on flags.

    :param dirs: Folders: [OS_bars, radio_bars, OS_exes, radio_exes, OS_zips, radio_zips]
    :type dirs: list(str)

    :param compressed: Whether to hash compressed files. True by default.
    :type compressed: bool

    :param deleted: Whether to delete uncompressed files. True by default.
    :type deleted: bool

    :param radios: Whether to hash radio autoloaders. True by default.
    :type radios: bool

    :param hashdict: Dictionary of hash rules, in ~\bbarchivist.ini.
    :type hashdict: dict({str: bool})
    """
    print("HASHING LOADERS...")
    utilities.cond_check(hashutils.verifier, utilities.def_args(dirs), [hashdict], radios, compressed, deleted)


def bulk_verify(dirs, compressed=True, deleted=True, radios=True):
    """
    Verify files in several folders based on flags.

    :param dirs: Folders: [OS_bars, radio_bars, OS_exes, radio_exes, OS_zips, radio_zips]
    :type dirs: list(str)

    :param compressed: Whether to hash compressed files. True by default.
    :type compressed: bool

    :param deleted: Whether to delete uncompressed files. True by default.
    :type deleted: bool

    :param radios: Whether to hash radio autoloaders. True by default.
    :type radios: bool
    """
    gpgkey, gpgpass = verify_gpg_credentials()
    if gpgpass is not None and gpgkey is not None:
        print("VERIFYING LOADERS...")
        print("KEY: {0}".format(gpgkey))
        restargs = [gpgkey, gpgpass, True]
        utilities.cond_check(gpgutils.gpgrunner, utilities.def_args(dirs), restargs, radios, compressed, deleted)


def enn_ayy(quant):
    """
    Cheeky way to put a N/A placeholder for a string.

    :param quant: What to check if it's None.
    :type quant: str
    """
    return "N/A" if quant is None else quant


def generate_workfolder(folder=None):
    """
    Check if a folder exists, make it if it doesn't, set it to home if None.

    :param folder: Folder to check.
    :type folder: str
    """
    folder = utilities.dirhandler(folder, os.getcwd())
    if folder is not None and not os.path.exists(folder):
        os.makedirs(folder)
    return folder


def info_header(afile, osver, radio=None, software=None, device=None):
    """
    Write header for info file.

    :param afile: Open file to write to.
    :type afile: File object

    :param osver: OS version, required for both types.
    :type osver: str

    :param radio: Radio version, required for QNX.
    :type radio: str

    :param software: Software release, required for QNX.
    :type software: str

    :param device: Device type, required for Android.
    :type device: str
    """
    afile.write("OS: {0}\n".format(osver))
    if device:
        afile.write("Device: {0}\n".format(enn_ayy(device)))
    else:
        afile.write("Radio: {0}\n".format(enn_ayy(radio)))
        afile.write("Software: {0}\n".format(enn_ayy(software)))
    afile.write("{0}\n".format("~"*40))


def prep_info(filepath, osver, device=None):
    """
    Prepare file list for new-style info file.

    :param filepath: Path to folder to analyze.
    :type filepath: str

    :param osver: OS version, required for both types.
    :type osver: str

    :param device: Device type, required for Android.
    :type device: str
    """
    fileext = ".zip" if device else ".7z"
    files = os.listdir(filepath)
    absfiles = [os.path.join(filepath, x) for x in files if x.endswith((fileext, ".exe"))]
    fname = os.path.join(filepath, "!{0}_OSINFO!.txt".format(osver))
    return fname, absfiles


def make_info(filepath, osver, radio=None, software=None, device=None):
    """
    Create a new-style info (names, sizes and hashes) file.

    :param filepath: Path to folder to analyze.
    :type filepath: str

    :param osver: OS version, required for both types.
    :type osver: str

    :param radio: Radio version, required for QNX.
    :type radio: str

    :param software: Software release, required for QNX.
    :type software: str

    :param device: Device type, required for Android.
    :type device: str
    """
    fname, absfiles = prep_info(filepath, osver, device)
    with open(fname, "w") as afile:
        info_header(afile, osver, radio, software, device)
        for indx, file in enumerate(absfiles):
            write_info(file, indx, len(absfiles), afile)


def write_info(infile, index, filecount, outfile):
    """
    Write a new-style info (names, sizes and hashes) file.

    :param infile: Path to file whose name, size and hash are to be written.
    :type infile: str

    :param index: Which file index out of the list of files we're writing.
    :type index: int

    :param filecount: Total number of files we're to write; for excluding terminal newline.
    :type filecount: int

    :param outfile: Open (!!!) file handle. Output file.
    :type outfile: str
    """
    fsize = os.stat(infile).st_size
    outfile.write("File: {0}\n".format(os.path.basename(infile)))
    outfile.write("\tSize: {0} ({1})\n".format(fsize, utilities.fsizer(fsize)))
    outfile.write("\tHashes:\n")
    outfile.write("\t\tMD5: {0}\n".format(hashutils.hashlib_hash(infile, hashlib.md5()).upper()))
    outfile.write("\t\tSHA1: {0}\n".format(hashutils.hashlib_hash(infile, hashlib.sha1()).upper()))
    outfile.write("\t\tSHA256: {0}\n".format(hashutils.hashlib_hash(infile, hashlib.sha256()).upper()))
    outfile.write("\t\tSHA512: {0}\n".format(hashutils.hashlib_hash(infile, hashlib.sha512()).upper()))
    if index != filecount - 1:
        outfile.write("\n")


def bulk_info(dirs, osv, compressed=True, deleted=True, radios=True, rad=None, swv=None, dev=None):
    """
    Generate info files in several folders based on flags.

    :param dirs: Folders: [OS_bars, radio_bars, OS_exes, radio_exes, OS_zips, radio_zips]
    :type dirs: list(str)

    :param osver: OS version, required for both types.
    :type osver: str

    :param compressed: Whether to hash compressed files. True by default.
    :type compressed: bool

    :param deleted: Whether to delete uncompressed files. True by default.
    :type deleted: bool

    :param radios: Whether to hash radio autoloaders. True by default.
    :type radios: bool

    :param rad: Radio version, required for QNX.
    :type rad: str

    :param swv: Software release, required for QNX.
    :type swv: str

    :param dev: Device type, required for Android.
    :type dev: str
    """
    print("GENERATING INFO FILES...")
    restargs = [osv, rad, swv, dev]
    utilities.cond_check(make_info, utilities.def_args(dirs), restargs, radios, compressed, deleted)
