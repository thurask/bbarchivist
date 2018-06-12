#!/usr/bin/env python3
"""This module contains various utilities for TCL tools."""

import collections  # defaultdict
import os  # path work

import requests  # session
from bbarchivist import argutils  # arguments
from bbarchivist import hashutils  # file hashes
from bbarchivist import networkutils  # network tools
from bbarchivist import networkutilstcl  # tcl network tools
from bbarchivist import utilities  # little things
from bbarchivist import xmlutilstcl  # xml handling

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2018 Thurask"


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


def tcl_download(downloadurl, filename, filesize, filehash, verify=True):
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

    :param verify: Whether to verify the file after downloading. Default is True.
    :type verify: bool
    """
    print("FILENAME: {0}".format(filename))
    print("LENGTH: {0}".format(utilities.fsizer(filesize)))
    networkutils.download(downloadurl)
    print("DOWNLOAD COMPLETE")
    os.rename(downloadurl.split("/")[-1], filename)
    if verify:
        method = hashutils.get_engine("sha1")
        shahash = hashutils.hashlib_hash(filename, method)
        if shahash == filehash:
            print("HASH CHECK OK")
        else:
            print(shahash)
            print("HASH FAILED!")


def tcl_prd_scan(curef, download=False, mode=4, fvver="AAA000", original=True, export=False, verify=True):
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

    :param original: If we'll download the file with its original filename. Default is True.
    :type original: bool

    :param export: Whether to export XML response to file. Default is False.
    :type export: bool

    :param verify: Whether to verify the file after downloading. Default is True.
    :type verify: bool
    """
    sess = requests.Session()
    ctext = networkutilstcl.tcl_check(curef, sess, mode, fvver, export)
    if ctext is None:
        raise SystemExit
    tvver, firmwareid, filename, filesize, filehash = xmlutilstcl.parse_tcl_check(ctext)
    salt = networkutilstcl.tcl_salt()
    vkhsh = networkutilstcl.vkhash(curef, tvver, firmwareid, salt, mode, fvver)
    updatetext = networkutilstcl.tcl_download_request(curef, tvver, firmwareid, salt, vkhsh, sess, mode, fvver, export)
    downloadurl, encslave = xmlutilstcl.parse_tcl_download_request(updatetext)
    statcode = networkutils.getcode(downloadurl, sess)
    filename = tcl_delta_filename(curef, fvver, tvver, filename, original)
    tcl_prd_print(tvver, downloadurl, filename, statcode, encslave, sess)
    if statcode == 200 and download:
        tcl_download(downloadurl, filename, filesize, filehash, verify)


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

    :param original: If we'll download the file with its original filename. Default is True.
    :type original: bool
    """
    if not original:
        prdver = curef.split("-")[1]
        filename = "JSU_PRD-{0}-{1}to{2}.zip".format(prdver, fvver, tvver)
    return filename


def tcl_prd_print(tvver, downloadurl, filename, statcode, encslave, session):
    """
    Print output from PRD scanning.

    :param tvver: Target software version.
    :type tvver: str

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
    print("OS: {0}".format(tvver))
    print("{0}: HTTP {1}".format(filename, statcode))
    print(downloadurl)
    if encslave is not None:
        address = "/{0}".format(downloadurl.split("/", 3)[3:][0])
        print("CHECKING HEADER...")
        sentinel = networkutilstcl.encrypt_header(address, encslave, session)
        if sentinel is not None:
            print(sentinel)


def tcl_prep_otaver(ota=None):
    """
    Prepare variables for OTA versus full check.

    :param ota: The starting version if OTA, None if not. Default is None.
    :type ota: str
    """
    if ota is not None:
        mode = 2
        fvver = ota
    else:
        mode = 4
        fvver = "AAA000"
    return mode, fvver


def tcl_delta_remote(curef):
    """
    Prepare remote version for delta scanning.

    :param curef: PRD of the phone variant to check.
    :type curef: str
    """
    remotedict = networkutilstcl.remote_prd_info()
    fvver = remotedict.get(curef, "AAA000")
    if fvver == "AAA000":
        print("NO REMOTE VERSION FOUND!")
        raise SystemExit
    return fvver


def tcl_mainscan_preamble(ota=None):
    """
    Prepare preamble for TCL scanning.

    :param ota: The starting version if OTA, None if not. Default is None.
    :type ota: str
    """
    argutils.slim_preamble("TCLSCAN")
    if ota is not None:
        print("PRDs with OTA from OS {0}".format(ota.upper()))


def tcl_mainscan_printer(curef, tvver, ota=None):
    """
    Print output of TCL scanning.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param tvver: Target software version.
    :type tvver: str

    :param ota: The starting version if OTA, None if not. Default is None.
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
    prds = [x.split(" ")[0].replace("PRD-", "").replace("APBI-PRD", "").replace("-", "") for x in prda]
    prdx = list({x[0:5]: x[5:]} for x in prds)
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

    :param tocheck: Specific PRD(s) to check, None if all will be checked. Default is None.
    :type tocheck: list(str)
    """
    prddict2 = prddict
    if tocheck is not None:
        prddict2 = collections.defaultdict(list)
        for toch in tocheck:
            toch = toch.replace("PRD-", "").replace("APBI-PRD", "")
            prddict2[toch] = prddict[toch]
    return prddict2


def tcl_findprd_centerscan(center, prddict, session, floor=0, ceiling=999, export=False, noprefix=False, key2mode=False):
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

    :param noprefix: Whether to skip adding "PRD-" prefix. Default is False.
    :type noprefix: bool

    :param key2mode: Whether to use new-style prefix. Default is False.
    :type key2mode: bool
    """
    tails = [int(i) for i in prddict[center]]
    safes = [g for g in range(floor, ceiling) if g not in tails]
    print("SCANNING ROOT: {0}{1}".format(center, " "*12))
    tcl_findprd_safescan(safes, center, session, export, noprefix, key2mode)


def tcl_findprd_prepcuref(center, tail, noprefix=False, key2mode=False):
    """
    Prepare candidate PRD.

    :param center: PRD-center-tail.
    :type center: str

    :param tail: PRD-center-tail.
    :type tail: int

    :param noprefix: Whether to skip adding "PRD-" prefix. Default is False.
    :type noprefix: bool

    :param key2mode: Whether to use new-style prefix. Default is False.
    :type key2mode: bool
    """
    if key2mode:
        curef = "APBI-PRD{0}{1:03}".format(center, tail)
    else:
        prefix = "" if noprefix else "PRD-"
        curef = "{2}{0}-{1:03}".format(center, tail, prefix)
    return curef


def tcl_findprd_safescan(safes, center, session, export=False, noprefix=False, key2mode=False):
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

    :param noprefix: Whether to skip adding "PRD-" prefix. Default is False.
    :type noprefix: bool

    :param key2mode: Whether to use new-style prefix. Default is False.
    :type key2mode: bool
    """
    for j in safes:
        curef = tcl_findprd_prepcuref(center, j, noprefix, key2mode)
        print("NOW SCANNING: {0}".format(curef), end="\r")
        checktext = networkutilstcl.tcl_check(curef, session, export)
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
    tvver, firmwareid, filename, fsize, fhash = xmlutilstcl.parse_tcl_check(checktext)
    del firmwareid, filename, fsize, fhash
    tvver2 = "{0}{1}".format(tvver, " "*12)
    tcl_mainscan_printer(curef, tvver2)


def tcl_findprd(prddict, floor=0, ceiling=999, export=False, noprefix=False, key2mode=False):
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

    :param noprefix: Whether to skip adding "PRD-" prefix. Default is False.
    :type noprefix: bool

    :param key2mode: Whether to use new-style prefix. Default is False.
    :type key2mode: bool
    """
    sess = requests.Session()
    for center in sorted(prddict.keys()):
        tcl_findprd_centerscan(center, prddict, sess, floor, ceiling, export, noprefix, key2mode)
