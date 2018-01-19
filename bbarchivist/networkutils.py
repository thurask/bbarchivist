#!/usr/bin/env python3
"""This module is used for network connections; APIs, downloading, etc."""

import base64  # encoding
import binascii  # encoding
import concurrent.futures  # multiprocessing/threading
import glob  # pem file lookup
import hashlib  # salt
import os  # filesystem read
import random  # salt
import re  # regexes
import time  # salt
import zlib  # encoding

import requests  # downloading
from bbarchivist import utilities  # parse filesize
from bbarchivist.bbconstants import SERVERS, TCLMASTERS  # lookup servers
from bs4 import BeautifulSoup  # scraping

try:
    from defusedxml import ElementTree  # safer XML parsing
except (ImportError, AttributeError):
    from xml.etree import ElementTree  # XML parsing

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2018 Thurask"


def grab_pem():
    """
    Work with either local cacerts or system cacerts.
    """
    try:
        pemfile = glob.glob(os.path.join(os.getcwd(), "cacert.pem"))[0]
    except IndexError:
        return requests.certs.where()  # no local cacerts
    else:
        return os.path.abspath(pemfile)  # local cacerts


def pem_wrapper(method):
    """
    Decorator to set REQUESTS_CA_BUNDLE.

    :param method: Method to use.
    :type method: function
    """
    def wrapper(*args, **kwargs):
        """
        Set REQUESTS_CA_BUNDLE before doing function.
        """
        os.environ["REQUESTS_CA_BUNDLE"] = grab_pem()
        return method(*args, **kwargs)
    return wrapper


def generic_session(session=None):
    """
    Create a Requests session object on the fly, if need be.

    :param session: Requests session object, created if this is None.
    :type session: requests.Session()
    """
    sess = requests.Session() if session is None else session
    return sess


def generic_soup_parser(url, session=None):
    """
    Get a BeautifulSoup HTML parser for some URL.

    :param url: The URL to check.
    :type url: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    session = generic_session(session)
    req = session.get(url)
    soup = BeautifulSoup(req.content, "html.parser")
    return soup


@pem_wrapper
def get_length(url, session=None):
    """
    Get content-length header from some URL.

    :param url: The URL to check.
    :type url: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    session = generic_session(session)
    if url is None:
        return 0
    try:
        heads = session.head(url)
        fsize = heads.headers['content-length']
        return int(fsize)
    except requests.ConnectionError:
        return 0


@pem_wrapper
def download(url, output_directory=None, session=None):
    """
    Download file from given URL.

    :param url: URL to download from.
    :type url: str

    :param output_directory: Download folder. Default is local.
    :type output_directory: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    session = generic_session(session)
    output_directory = utilities.dirhandler(output_directory, os.getcwd())
    lfname = url.split('/')[-1]
    sname = utilities.stripper(lfname)
    fname = os.path.join(output_directory, lfname)
    download_writer(url, fname, lfname, sname, session)
    remove_empty_download(fname)


def remove_empty_download(fname):
    """
    Remove file if it's empty.

    :param fname: File path.
    :type fname: str
    """
    if os.stat(fname).st_size == 0:
        os.remove(fname)


def download_writer(url, fname, lfname, sname, session=None):
    """
    Download file and write to disk.

    :param url: URL to download from.
    :type url: str

    :param fname: File path.
    :type fname: str

    :param lfname: Long filename.
    :type lfname: str

    :param sname: Short name, for printing to screen.
    :type sname: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    with open(fname, "wb") as file:
        req = session.get(url, stream=True)
        clength = req.headers['content-length']
        fsize = utilities.fsizer(clength)
        if req.status_code == 200:  # 200 OK
            print("DOWNLOADING {0} [{1}]".format(sname, fsize))
            for chunk in req.iter_content(chunk_size=1024):
                file.write(chunk)
        else:
            print("ERROR: HTTP {0} IN {1}".format(req.status_code, lfname))


def download_bootstrap(urls, outdir=None, workers=5, session=None):
    """
    Run downloaders for each file in given URL iterable.

    :param urls: URLs to download.
    :type urls: list

    :param outdir: Download folder. Default is handled in :func:`download`.
    :type outdir: str

    :param workers: Number of worker processes. Default is 5.
    :type workers: int

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    workers = len(urls) if len(urls) < workers else workers
    spinman = utilities.SpinManager()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as xec:
        try:
            spinman.start()
            for url in urls:
                xec.submit(download, url, outdir, session)
        except (KeyboardInterrupt, SystemExit):
            xec.shutdown()
            spinman.stop()
    spinman.stop()
    utilities.spinner_clear()
    utilities.line_begin()


def download_android_tools(downloaddir=None):
    """
    Download Android SDK platform tools.

    :param downloaddir: Directory name, default is "plattools".
    :type downloaddir: str
    """
    if downloaddir is None:
        downloaddir = "plattools"
    if os.path.exists(downloaddir):
        os.removedirs(downloaddir)
    os.mkdir(downloaddir)
    platforms = ("windows", "linux", "darwin")
    dlurls = ["https://dl.google.com/android/repository/platform-tools-latest-{0}.zip".format(plat) for plat in platforms]
    sess = generic_session()
    download_bootstrap(dlurls, outdir="plattools", session=sess)


@pem_wrapper
def getcode(url, session=None):
    """
    Return status code of given URL.

    :param url: URL to check.
    :type url: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    session = generic_session(session)
    try:
        shead = session.head(url)
        status = int(shead.status_code)
        return status
    except requests.ConnectionError:
        return 404


@pem_wrapper
def availability(url, session=None):
    """
    Check HTTP status code of given URL.
    200 or 301-308 is OK, else is not.

    :param url: URL to check.
    :type url: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    status = getcode(url, session)
    return status == 200 or 300 < status <= 308


def clean_availability(results, server):
    """
    Clean availability for autolookup script.

    :param results: Result dict.
    :type results: dict(str: str)

    :param server: Server, key for result dict.
    :type server: str
    """
    marker = "PD" if server == "p" else server.upper()
    rel = results[server.lower()]
    avail = marker if rel != "SR not in system" and rel is not None else "  "
    return rel, avail


def tcl_master():
    """
    Get a random master server.
    """
    return random.choice(TCLMASTERS)


def tcl_default_id(devid):
    """
    Get an IMEI or a serial number or something.

    :param devid: Return default if this is None.
    :type devid: str
    """
    if devid is None:
        devid = "543212345000000"
    return devid


def check_prep(curef, mode=4, fvver="AAA000", cltp=2010, cktp=2, rtd=1, chnl=2, devid=None):
    """
    Prepare variables for TCL update check.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param mode: 4 if downloading autoloaders, 2 if downloading OTA deltas.
    :type mode: int

    :param fvver: Initial software version, must be specific if downloading OTA deltas.
    :type fvver: str

    :param cltp: 2010 to always show latest version, 10 to show actual updates. Default is 2010.
    :type cltp: int

    :param cktp: 2 if checking manually, 1 if checking automatically. Default is 2.
    :type cktp: int

    :param rtd: 2 if rooted, 1 if not. Default is 1.
    :type rtd: int

    :param chnl: 2 if checking on WiFi, 1 if checking on mobile. Default is 2.
    :type chnl: int

    :param devid: Serial number/IMEI. Default is fake, not that it matters.
    :type devid: str
    """
    devid = tcl_default_id(devid)
    geturl = "http://{0}/check.php".format(tcl_master())
    params = {"id": devid, "curef": curef, "fv": fvver, "mode": mode, "type": "Firmware", "cltp": cltp, "cktp": cktp, "rtd": rtd, "chnl": chnl}
    return geturl, params


@pem_wrapper
def tcl_check(curef, session=None, mode=4, fvver="AAA000", export=False):
    """
    Check TCL server for updates.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()

    :param mode: 4 if downloading autoloaders, 2 if downloading OTA deltas.
    :type mode: int

    :param fvver: Initial software version, must be specific if downloading OTA deltas.
    :type fvver: str

    :param export: Whether to export XML response to file. Default is False.
    :type export: bool
    """
    sess = generic_session(session)
    geturl, params = check_prep(curef, mode, fvver)
    req = sess.get(geturl, params=params)
    if req.status_code == 200:
        req.encoding = "utf-8"
        response = req.text
        if export:
            dump_tcl_xml(response)
    else:
        response = None
    return response


def parse_tcl_check(data):
    """
    Extract version and file info from TCL update server response.

    :param data: The data to parse.
    :type data: str
    """
    root = ElementTree.fromstring(data)
    tvver = root.find("VERSION").find("TV").text
    fwid = root.find("FIRMWARE").find("FW_ID").text
    fileinfo = root.find("FIRMWARE").find("FILESET").find("FILE")
    filename = fileinfo.find("FILENAME").text
    filesize = fileinfo.find("SIZE").text
    filehash = fileinfo.find("CHECKSUM").text
    return tvver, fwid, filename, filesize, filehash


def tcl_salt():
    """
    Generate salt value for TCL server tools.
    """
    millis = round(time.time() * 1000)
    tail = "{0:06d}".format(random.randint(0, 999999))
    return "{0}{1}".format(str(millis), tail)


def dump_tcl_xml(xmldata):
    """
    Write XML responses to output directory.

    :param xmldata: Response XML.
    :type xmldata: str
    """
    outfile = os.path.join(os.getcwd(), "logs", "{0}.xml".format(tcl_salt()))
    if not os.path.exists(os.path.dirname(outfile)):
        os.makedirs(os.path.dirname(outfile))
    with open(outfile, "w", encoding="utf-8") as afile:
        afile.write(xmldata)


def unpack_vdkey():
    """
    Draw the curtain back.
    """
    vdkey = b"eJwdjwEOwDAIAr8kKFr//7HhmqXp8AIIDrYAgg8byiUXrwRJRXja+d6iNxu0AhUooDCN9rd6rDLxmGIakUVWo3IGCTRWqCAt6X4jGEIUAxgN0eYWnp+LkpHQAg/PsO90ELsy0Npm/n2HbtPndFgGEV31R9OmT4O4nrddjc3Qt6nWscx7e+WRHq5UnOudtjw5skuV09pFhvmqnOEIs4ljPeel1wfLYUF4\n"
    vdk = zlib.decompress(binascii.a2b_base64(vdkey))
    return vdk.decode("utf-8")


def vkhash(curef, tvver, fwid, salt, mode=4, fvver="AAA000", cltp=2010, devid=None):
    """
    Generate hash from TCL update server variables.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param tvver: Target software version.
    :type tvver: str

    :param fwid: Firmware ID for desired download file.
    :type fwid: str

    :param salt: Salt hash.
    :type salt: str

    :param mode: 4 if downloading autoloaders, 2 if downloading OTA deltas.
    :type mode: int

    :param fvver: Initial software version, must be specific if downloading OTA deltas.
    :type fvver: str

    :param cltp: 2010 to always show latest version, 10 to show actual updates. Default is 2010.
    :type cltp: int

    :param devid: Serial number/IMEI. Default is fake, not that it matters.
    :type devid: str
    """
    vdk = unpack_vdkey()
    devid = tcl_default_id(devid)
    query = "id={0}&salt={1}&curef={2}&fv={3}&tv={4}&type={5}&fw_id={6}&mode={7}&cltp={8}{9}".format(devid, salt, curef, fvver, tvver, "Firmware", fwid, mode, cltp, vdk)
    engine = hashlib.sha1()
    engine.update(bytes(query, "utf-8"))
    return engine.hexdigest()


def download_request_prep(curef, tvver, fwid, salt, vkh, mode=4, fvver="AAA000", cltp=2010, devid=None):
    """
    Prepare variables for download server check.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param tvver: Target software version.
    :type tvver: str

    :param fwid: Firmware ID for desired download file.
    :type fwid: str

    :param salt: Salt hash.
    :type salt: str

    :param vkh: VDKey-based hash.
    :type vkh: str

    :param mode: 4 if downloading autoloaders, 2 if downloading OTA deltas.
    :type mode: int

    :param fvver: Initial software version, must be specific if downloading OTA deltas.
    :type fvver: str

    :param cltp: 2010 to always show latest version, 10 to show actual updates. Default is 2010.
    :type cltp: int

    :param devid: Serial number/IMEI. Default is fake, not that it matters.
    :type devid: str
    """
    devid = tcl_default_id(devid)
    posturl = "http://{0}/download_request.php".format(tcl_master())
    params = {"id": devid, "curef": curef, "fv": fvver, "mode": mode, "type": "Firmware", "tv": tvver, "fw_id": fwid, "salt": salt, "vk": vkh, "cltp": cltp}
    if mode == 4:
        params["foot"] = 1
    return posturl, params


@pem_wrapper
def tcl_download_request(curef, tvver, fwid, salt, vkh, session=None, mode=4, fvver="AAA000", export=False):
    """
    Check TCL server for download URLs.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param tvver: Target software version.
    :type tvver: str

    :param fwid: Firmware ID for desired download file.
    :type fwid: str

    :param salt: Salt hash.
    :type salt: str

    :param vkh: VDKey-based hash.
    :type vkh: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()

    :param mode: 4 if downloading autoloaders, 2 if downloading OTA deltas.
    :type mode: int

    :param fvver: Initial software version, must be specific if downloading OTA deltas.
    :type fvver: str

    :param export: Whether to export XML response to file. Default is False.
    :type export: bool
    """
    sess = generic_session(session)
    posturl, params = download_request_prep(curef, tvver, fwid, salt, vkh, mode, fvver)
    req = sess.post(posturl, data=params)
    if req.status_code == 200:
        req.encoding = "utf-8"
        response = req.text
        if export:
            dump_tcl_xml(response)
    else:
        response = None
    return response


def parse_tcl_download_request(body, mode=4):
    """
    Extract file URL and encrypt slave URL from TCL update server response.

    :param data: The data to parse.
    :type data: str

    :param mode: 4 if downloading autoloaders, 2 if downloading OTA deltas.
    :type mode: int
    """
    root = ElementTree.fromstring(body)
    slavelist = root.find("SLAVE_LIST").findall("SLAVE")
    slave = random.choice(slavelist).text
    dlurl = root.find("FILE_LIST").find("FILE").find("DOWNLOAD_URL").text
    eslave = root.find("SLAVE_LIST").findall("ENCRYPT_SLAVE")
    encslave = None if mode == 2 or not eslave else random.choice(eslave).text
    return "http://{0}{1}".format(slave, dlurl), encslave


def encrypt_header_prep(address, encslave):
    """
    Prepare variables for encrypted header check.

    :param address: File URL minus host.
    :type address: str

    :param encslave: Server hosting header script.
    :type encslave: str
    """
    encs = {b"YWNjb3VudA==" : b"emhlbmdodWEuZ2Fv", b"cGFzc3dvcmQ=": b"cWFydUQ0b2s="}
    params = {base64.b64decode(key): base64.b64decode(val) for key, val in encs.items()}
    params[b"address"] = bytes(address, "utf-8")
    posturl = "http://{0}/encrypt_header.php".format(encslave)
    return posturl, params


@pem_wrapper
def encrypt_header(address, encslave, session=None):
    """
    Check encrypted header.

    :param address: File URL minus host.
    :type address: str

    :param encslave: Server hosting header script.
    :type encslave: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    sess = generic_session(session)
    posturl, params = encrypt_header_prep(address, encslave)
    req = sess.post(posturl, data=params)
    if req.status_code == 206:  # partial
        contentlength = int(req.headers["Content-Length"])
        sentinel = "HEADER FOUND" if contentlength == 4194320 else "NO HEADER FOUND"
        return sentinel
    else:
        return None


def cchecker_get_tags(root):
    """
    Get country and carrier from XML.

    :param root: ElementTree we're barking up.
    :type root: xml.etree.ElementTree.ElementTree
    """
    for child in root:
        if child.tag == "country":
            country = child.get("name")
        if child.tag == "carrier":
            carrier = child.get("name")
    return country, carrier


@pem_wrapper
def carrier_checker(mcc, mnc, session=None):
    """
    Query BlackBerry World to map a MCC and a MNC to a country and carrier.

    :param mcc: Country code.
    :type mcc: int

    :param mnc: Network code.
    :type mnc: int

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    session = generic_session(session)
    url = "http://appworld.blackberry.com/ClientAPI/checkcarrier?homemcc={0}&homemnc={1}&devicevendorid=-1&pin=0".format(mcc, mnc)
    user_agent = {'User-agent': 'AppWorld/5.1.0.60'}
    req = session.get(url, headers=user_agent)
    root = ElementTree.fromstring(req.text)
    country, carrier = cchecker_get_tags(root)
    return country, carrier


def return_npc(mcc, mnc):
    """
    Format MCC and MNC into a NPC.

    :param mcc: Country code.
    :type mcc: int

    :param mnc: Network code.
    :type mnc: int
    """
    return "{0}{1}30".format(str(mcc).zfill(3), str(mnc).zfill(3))


@pem_wrapper
def carrier_query(npc, device, upgrade=False, blitz=False, forced=None, session=None):
    """
    Query BlackBerry servers, check which update is out for a carrier.

    :param npc: MCC + MNC (see `func:return_npc`)
    :type npc: int

    :param device: Hexadecimal hardware ID.
    :type device: str

    :param upgrade: Whether to use upgrade files. False by default.
    :type upgrade: bool

    :param blitz: Whether or not to create a blitz package. False by default.
    :type blitz: bool

    :param forced: Force a software release.
    :type forced: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    session = generic_session(session)
    upg = "upgrade" if upgrade else "repair"
    forced = "latest" if forced is None else forced
    url = "https://cs.sl.blackberry.com/cse/updateDetails/2.2/"
    query = '<?xml version="1.0" encoding="UTF-8"?>'
    query += '<updateDetailRequest version="2.2.1" authEchoTS="1366644680359">'
    query += "<clientProperties>"
    query += "<hardware>"
    query += "<pin>0x2FFFFFB3</pin><bsn>1128121361</bsn>"
    query += "<imei>004401139269240</imei>"
    query += "<id>0x{0}</id>".format(device)
    query += "</hardware>"
    query += "<network>"
    query += "<homeNPC>0x{0}</homeNPC>".format(npc)
    query += "<iccid>89014104255505565333</iccid>"
    query += "</network>"
    query += "<software>"
    query += "<currentLocale>en_US</currentLocale>"
    query += "<legalLocale>en_US</legalLocale>"
    query += "</software>"
    query += "</clientProperties>"
    query += "<updateDirectives>"
    query += '<allowPatching type="REDBEND">true</allowPatching>'
    query += "<upgradeMode>{0}</upgradeMode>".format(upg)
    query += "<provideDescriptions>false</provideDescriptions>"
    query += "<provideFiles>true</provideFiles>"
    query += "<queryType>NOTIFICATION_CHECK</queryType>"
    query += "</updateDirectives>"
    query += "<pollType>manual</pollType>"
    query += "<resultPackageSetCriteria>"
    query += '<softwareRelease softwareReleaseVersion="{0}" />'.format(forced)
    query += "<releaseIndependent>"
    query += '<packageType operation="include">application</packageType>'
    query += "</releaseIndependent>"
    query += "</resultPackageSetCriteria>"
    query += "</updateDetailRequest>"
    header = {"Content-Type": "text/xml;charset=UTF-8"}
    req = session.post(url, headers=header, data=query)
    return parse_carrier_xml(req.text, blitz)


def carrier_swver_get(root):
    """
    Get software release from carrier XML.

    :param root: ElementTree we're barking up.
    :type root: xml.etree.ElementTree.ElementTree
    """
    for child in root.iter("softwareReleaseMetadata"):
        swver = child.get("softwareReleaseVersion")
    return swver


def carrier_child_fileappend(child, files, baseurl, blitz=False):
    """
    Append bar file links to a list from a child element.

    :param child: Child element in use.
    :type child: xml.etree.ElementTree.Element

    :param files: Filelist.
    :type files: list(str)

    :param baseurl: Base URL, URL minus the filename.
    :type baseurl: str

    :param blitz: Whether or not to create a blitz package. False by default.
    :type blitz: bool
    """
    if not blitz:
        files.append(baseurl + child.get("path"))
    else:
        if child.get("type") not in ["system:radio", "system:desktop", "system:os"]:
            files.append(baseurl + child.get("path"))
    return files


def carrier_child_finder(root, files, baseurl, blitz=False):
    """
    Extract filenames, radio and OS from child elements.

    :param root: ElementTree we're barking up.
    :type root: xml.etree.ElementTree.ElementTree

    :param files: Filelist.
    :type files: list(str)

    :param baseurl: Base URL, URL minus the filename.
    :type baseurl: str

    :param blitz: Whether or not to create a blitz package. False by default.
    :type blitz: bool
    """
    osver = radver = ""
    for child in root.iter("package"):
        files = carrier_child_fileappend(child, files, baseurl, blitz)
        if child.get("type") == "system:radio":
            radver = child.get("version")
        elif child.get("type") == "system:desktop":
            osver = child.get("version")
        elif child.get("type") == "system:os":
            osver = child.get("version")
    return osver, radver, files


def parse_carrier_xml(data, blitz=False):
    """
    Parse the response to a carrier update request and return the juicy bits.

    :param data: The data to parse.
    :type data: xml

    :param blitz: Whether or not to create a blitz package. False by default.
    :type blitz: bool
    """
    root = ElementTree.fromstring(data)
    sw_exists = root.find('./data/content/softwareReleaseMetadata')
    swver = "N/A" if sw_exists is None else ""
    if sw_exists is not None:
        swver = carrier_swver_get(root)
    files = []
    package_exists = root.find('./data/content/fileSets/fileSet')
    osver = radver = ""
    if package_exists is not None:
        baseurl = "{0}/".format(package_exists.get("url"))
        osver, radver, files = carrier_child_finder(root, files, baseurl, blitz)
    return(swver, osver, radver, files)


@pem_wrapper
def sr_lookup(osver, server, session=None):
    """
    Software release lookup, with choice of server.
    :data:`bbarchivist.bbconstants.SERVERLIST` for server list.

    :param osver: OS version to lookup, 10.x.y.zzzz.
    :type osver: str

    :param server: Server to use.
    :type server: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    query = '<?xml version="1.0" encoding="UTF-8"?>'
    query += '<srVersionLookupRequest version="2.0.0"'
    query += ' authEchoTS="1366644680359">'
    query += '<clientProperties><hardware>'
    query += '<pin>0x2FFFFFB3</pin><bsn>1140011878</bsn>'
    query += '<imei>004402242176786</imei><id>0x8D00240A</id>'
    query += '<isBootROMSecure>true</isBootROMSecure>'
    query += '</hardware>'
    query += '<network>'
    query += '<vendorId>0x0</vendorId><homeNPC>0x60</homeNPC>'
    query += '<currentNPC>0x60</currentNPC><ecid>0x1</ecid>'
    query += '</network>'
    query += '<software><currentLocale>en_US</currentLocale>'
    query += '<legalLocale>en_US</legalLocale>'
    query += '<osVersion>{0}</osVersion>'.format(osver)
    query += '<omadmEnabled>false</omadmEnabled>'
    query += '</software></clientProperties>'
    query += '</srVersionLookupRequest>'
    reqtext = sr_lookup_poster(query, server, session)
    packtext = sr_lookup_xmlparser(reqtext)
    return packtext


def sr_lookup_poster(query, server, session=None):
    """
    Post the XML payload for a software release lookup.

    :param query: XML payload.
    :type query: str

    :param server: Server to use.
    :type server: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    session = generic_session(session)
    header = {"Content-Type": "text/xml;charset=UTF-8"}
    try:
        req = session.post(server, headers=header, data=query, timeout=1)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        reqtext = "SR not in system"
    else:
        reqtext = req.text
    return reqtext


def sr_lookup_xmlparser(reqtext):
    """
    Take the text of a software lookup request response and parse it as XML.

    :param reqtext: Response text, hopefully XML formatted.
    :type reqtext: str
    """
    try:
        root = ElementTree.fromstring(reqtext)
    except ElementTree.ParseError:
        packtext = "SR not in system"
    else:
        packtext = sr_lookup_extractor(root)
    return packtext


def sr_lookup_extractor(root):
    """
    Take an ElementTree and extract a software release from it.

    :param root: ElementTree we're barking up.
    :type root: xml.etree.ElementTree.ElementTree
    """
    reg = re.compile(r"(\d{1,4}\.)(\d{1,4}\.)(\d{1,4}\.)(\d{1,4})")
    packages = root.findall('./data/content/')
    for package in packages:
        if package.text is not None:
            match = reg.match(package.text)
            packtext = package.text if match else "SR not in system"
            return packtext


def sr_lookup_bootstrap(osv, session=None, no2=False):
    """
    Run lookups for each server for given OS.

    :param osv: OS to check.
    :type osv: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()

    :param no2: Whether to skip Alpha2/Beta2 servers. Default is false.
    :type no2: bool
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as xec:
        try:
            results = {
                "p": None,
                "a1": None,
                "a2": None,
                "b1": None,
                "b2": None
            }
            if no2:
                del results["a2"]
                del results["b2"]
            for key in results:
                results[key] = xec.submit(sr_lookup, osv, SERVERS[key], session).result()
            return results
        except KeyboardInterrupt:
            xec.shutdown(wait=False)


@pem_wrapper
def available_bundle_lookup(mcc, mnc, device, session=None):
    """
    Check which software releases were ever released for a carrier.

    :param mcc: Country code.
    :type mcc: int

    :param mnc: Network code.
    :type mnc: int

    :param device: Hexadecimal hardware ID.
    :type device: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    session = generic_session(session)
    server = "https://cs.sl.blackberry.com/cse/availableBundles/1.0.0/"
    npc = return_npc(mcc, mnc)
    query = '<?xml version="1.0" encoding="UTF-8"?>'
    query += '<availableBundlesRequest version="1.0.0" '
    query += 'authEchoTS="1366644680359">'
    query += '<deviceId><pin>0x2FFFFFB3</pin></deviceId>'
    query += '<clientProperties><hardware><id>0x{0}</id>'.format(device)
    query += '<isBootROMSecure>true</isBootROMSecure></hardware>'
    query += '<network><vendorId>0x0</vendorId><homeNPC>0x{0}</homeNPC>'.format(npc)
    query += '<currentNPC>0x{0}</currentNPC></network><software>'.format(npc)
    query += '<currentLocale>en_US</currentLocale>'
    query += '<legalLocale>en_US</legalLocale>'
    query += '<osVersion>10.0.0.0</osVersion>'
    query += '<radioVersion>10.0.0.0</radioVersion></software>'
    query += '</clientProperties><updateDirectives><bundleVersionFilter>'
    query += '</bundleVersionFilter></updateDirectives>'
    query += '</availableBundlesRequest>'
    header = {"Content-Type": "text/xml;charset=UTF-8"}
    req = session.post(server, headers=header, data=query)
    root = ElementTree.fromstring(req.text)
    package = root.find('./data/content')
    bundlelist = [child.attrib["version"] for child in package]
    return bundlelist


@pem_wrapper
def ptcrb_scraper(ptcrbid, session=None):
    """
    Get the PTCRB results for a given device.

    :param ptcrbid: Numerical ID from PTCRB (end of URL).
    :type ptcrbid: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    baseurl = "https://www.ptcrb.com/certified-devices/device-details/?model={0}".format(ptcrbid)
    sess = generic_session(session)
    sess.headers.update({"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36"})
    soup = generic_soup_parser(baseurl, sess)
    certtable = soup.find_all("table")[1]
    tds = certtable.find_all("td")[1::2]  # every other
    prelimlist = [tdx.text for tdx in tds]
    cleanlist = [ptcrb_item_cleaner(item.strip()) for item in prelimlist]
    return cleanlist


def space_pad(instring, minlength):
    """
    Pad a string with spaces until it's the minimum length.

    :param instring: String to pad.
    :type instring: str

    :param minlength: Pad while len(instring) < minlength.
    :type minlength: int
    """
    while len(instring) < minlength:
        instring += " "
    return instring


def ptcrb_cleaner_multios(item):
    """
    Discard multiple entries for "OS".

    :param item: The item to clean.
    :type item: str
    """
    if item.count("OS") > 1:
        templist = item.split("OS")
        templist[0] = "OS"
        item = "".join([templist[0], templist[1]])
    return item


def ptcrb_cleaner_spaces(item):
    """
    Pad item with spaces to the right length.

    :param item: The item to clean.
    :type item: str
    """
    spaclist = item.split(" ")
    if len(spaclist) > 1:
        spaclist[1] = space_pad(spaclist[1], 11)
    if len(spaclist) > 3:
        spaclist[3] = space_pad(spaclist[3], 11)
    item = " ".join(spaclist)
    return item


def ptcrb_item_cleaner(item):
    """
    Cleanup poorly formatted PTCRB entries written by an intern.

    :param item: The item to clean.
    :type item: str
    """
    item = item.replace("<td>", "")
    item = item.replace("</td>", "")
    item = item.replace("\n", "")
    item = item.replace("SW: OS", "OS")
    item = item.replace("Software Version: OS", "OS")
    item = item.replace(" (SR", ", SR")
    item = re.sub(r"\s?\((.*)$", "", item)
    item = re.sub(r"\sSV.*$", "", item)
    item = item.replace(")", "")
    item = item.replace(". ", ".")
    item = item.replace(";", "")
    item = item.replace("version", "Version")
    item = item.replace("Verison", "Version")
    item = ptcrb_cleaner_multios(item)
    item = item.replace("SR10", "SR 10")
    item = item.replace("SR", "SW Release")
    item = item.replace(" Version:", ":")
    item = item.replace("Version ", " ")
    item = item.replace(":1", ": 1")
    item = item.replace(", ", " ")
    item = item.replace(",", " ")
    item = item.replace("Software", "SW")
    item = item.replace("  ", " ")
    item = item.replace("OS ", "OS: ")
    item = item.replace("Radio ", "Radio: ")
    item = item.replace("Release ", "Release: ")
    item = ptcrb_cleaner_spaces(item)
    item = item.strip()
    item = item.replace("\r", "")
    if item.startswith("10"):
        item = "OS: {0}".format(item)
    item = item.replace(":    ", ": ")
    item = item.replace(":   ", ": ")
    return item


@pem_wrapper
def kernel_scraper(utils=False, session=None):
    """
    Scrape BlackBerry's GitHub kernel repo for available branches.

    :param utils: Check android-utils repo instead of android-linux-kernel. Default is False.
    :type utils: bool

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    repo = "android-utils" if utils else "android-linux-kernel"
    kernlist = []
    sess = generic_session(session)
    for page in range(1, 10):
        url = "https://github.com/blackberry/{0}/branches/all?page={1}".format(repo, page)
        soup = generic_soup_parser(url, sess)
        if soup.find("div", {"class": "no-results-message"}):
            break
        else:
            text = soup.get_text()
            kernlist.extend(re.findall(r"msm[0-9]{4}\/[A-Z0-9]{6}", text, re.IGNORECASE))
    return kernlist


def root_generator(folder, build, variant="common"):
    """
    Generate roots for the SHAxxx hash lookup URLs.

    :param folder: Dictionary of variant: loader name pairs.
    :type folder: dict(str: str)

    :param build: Build to check, 3 letters + 3 numbers.
    :type build: str

    :param variant: Autoloader variant. Default is "common".
    :type variant: str
    """
    #Priv specific
    privx = "bbfoundation/hashfiles_priv/{0}".format(folder[variant])
    #DTEK50 specific
    dtek50x = "bbSupport/DTEK50" if build[:3] == "AAF" else "bbfoundation/hashfiles_priv/dtek50"
    #DTEK60 specific
    dtek60x = dtek50x  # still uses dtek50 folder, for some reason
    #Pack it up
    roots = {"Priv": privx, "DTEK50": dtek50x, "DTEK60": dtek60x}
    return roots


def make_droid_skeleton_bbm(method, build, device, variant="common"):
    """
    Make an Android autoloader/hash URL, on the BB Mobile site.

    :param method: None for regular OS links, "sha256/512" for SHA256 or 512 hash.
    :type method: str

    :param build: Build to check, 3 letters + 3 numbers.
    :type build: str

    :param device: Device to check.
    :type device: str

    :param variant: Autoloader variant. Default is "common".
    :type variant: str
    """
    devices = {"KEYone": "qc8953", "Motion": "qc8953"}
    base = "bbry_{2}_autoloader_user-{0}-{1}".format(variant, build.upper(), devices[device])
    if method is None:
        skel = "http://54.247.87.13/softwareupgrade/BBM/{0}.zip".format(base)
    else:
        skel = "http://54.247.87.13/softwareupgrade/BBM/{0}.{1}sum".format(base, method.lower())
    return skel


def make_droid_skeleton_og(method, build, device, variant="common"):
    """
    Make an Android autoloader/hash URL, on the original site.

    :param method: None for regular OS links, "sha256/512" for SHA256 or 512 hash.
    :type method: str

    :param build: Build to check, 3 letters + 3 numbers.
    :type build: str

    :param device: Device to check.
    :type device: str

    :param variant: Autoloader variant. Default is "common".
    :type variant: str
    """
    folder = {"vzw-vzw": "verizon", "na-att": "att", "na-tmo": "tmo", "common": "default"}
    devices = {"Priv": "qc8992", "DTEK50": "qc8952_64_sfi", "DTEK60": "qc8996"}
    roots = root_generator(folder, build, variant)
    base = "bbry_{2}_autoloader_user-{0}-{1}".format(variant, build.upper(), devices[device])
    if method is None:
        skel = "https://bbapps.download.blackberry.com/Priv/{0}.zip".format(base)
    else:
        skel = "https://ca.blackberry.com/content/dam/{1}/{0}.{2}sum".format(base, roots[device], method.lower())
    return skel


def make_droid_skeleton(method, build, device, variant="common"):
    """
    Make an Android autoloader/hash URL.

    :param method: None for regular OS links, "sha256/512" for SHA256 or 512 hash.
    :type method: str

    :param build: Build to check, 3 letters + 3 numbers.
    :type build: str

    :param device: Device to check.
    :type device: str

    :param variant: Autoloader variant. Default is "common".
    :type variant: str
    """
    # No Aurora
    oglist = ("Priv", "DTEK50", "DTEK60")  # BlackBerry
    bbmlist = ("KEYone", "Motion")   # BB Mobile
    if device in oglist:
        skel = make_droid_skeleton_og(method, build, device, variant)
    elif device in bbmlist:
        skel = make_droid_skeleton_bbm(method, build, device, variant)
    return skel


def bulk_droid_skeletons(devs, build, method=None):
    """
    Prepare list of Android autoloader/hash URLs.

    :param devs: List of devices.
    :type devs: list(str)

    :param build: Build to check, 3 letters + 3 numbers.
    :type build: str

    :param method: None for regular OS links, "sha256/512" for SHA256 or 512 hash.
    :type method: str
    """
    carrier_variants = {
        "Priv": ("common", "vzw-vzw", "na-tmo", "na-att"),
        "KEYone": ("common", "usa-sprint", "global-att", "china-china")
    }
    common_variants = ("common", )  # for single-variant devices
    carrier_devices = ("Priv", )  # add KEYone when verified
    skels = []
    for dev in devs:
        varlist = carrier_variants[dev] if dev in carrier_devices else common_variants
        for var in varlist:
            skel = make_droid_skeleton(method, build, dev, var)
            skels.append(skel)
    return skels


def prepare_droid_list(device):
    """
    Convert single devices to a list, if necessary.

    :param device: Device to check.
    :type device: str
    """
    if isinstance(device, list):
        devs = device
    else:
        devs = [device]
    return devs


def droid_scanner(build, device, method=None, session=None):
    """
    Check for Android autoloaders on BlackBerry's site.

    :param build: Build to check, 3 letters + 3 numbers.
    :type build: str

    :param device: Device to check.
    :type device: str

    :param method: None for regular OS links, "sha256/512" for SHA256 or 512 hash.
    :type method: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    devs = prepare_droid_list(device)
    skels = bulk_droid_skeletons(devs, build, method)
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(skels)) as xec:
        results = droid_scanner_worker(xec, skels, session)
    return results if results else None


def droid_scanner_worker(xec, skels, session=None):
    """
    Worker to check for Android autoloaders.

    :param xec: ThreadPoolExecutor instance.
    :type xec: concurrent.futures.ThreadPoolExecutor

    :param skels: List of skeleton formats.
    :type skels: list(str)

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    results = []
    for skel in skels:
        avail = xec.submit(availability, skel, session)
        if avail.result():
            results.append(skel)
    return results


def chunker(iterable, inc):
    """
    Convert an iterable into a list of inc sized lists.

    :param iterable: Iterable to chunk.
    :type iterable: list/tuple/string

    :param inc: Increment; how big each chunk is.
    :type inc: int
    """
    chunks = [iterable[x:x+inc] for x in range(0, len(iterable), inc)]
    return chunks


def unicode_filter(intext):
    """
    Remove Unicode crap.

    :param intext: Text to filter.
    :type intext: str
    """
    return intext.replace("\u2013", "").strip()


def table_header_filter(ptag):
    """
    Validate p tag, to see if it's relevant.

    :param ptag: P tag.
    :type ptag: bs4.element.Tag
    """
    valid = ptag.find("b") and "BlackBerry" in ptag.text and not "experts" in ptag.text
    return valid


def table_headers(pees):
    """
    Generate table headers from list of p tags.

    :param pees: List of p tags.
    :type pees: list(bs4.element.Tag)
    """
    bolds = [x.text for x in pees if table_header_filter(x)]
    return bolds


@pem_wrapper
def loader_page_scraper(session=None):
    """
    Return scraped autoloader pages.

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    session = generic_session(session)
    loader_page_scraper_og(session)
    loader_page_scraper_bbm(session)


def loader_page_scraper_og(session=None):
    """
    Return scraped autoloader page, original site.

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    url = "https://ca.blackberry.com/support/smartphones/Android-OS-Reload.html"
    soup = generic_soup_parser(url, session)
    tables = soup.find_all("table")
    headers = table_headers(soup.find_all("p"))
    for idx, table in enumerate(tables):
        loader_page_chunker_og(idx, table, headers)


def loader_page_scraper_bbm(session=None):
    """
    Return scraped autoloader page, new site.

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    url = "https://www.blackberrymobile.com/support/reload-software/"
    soup = generic_soup_parser(url, session)
    ulls = soup.find_all("ul", {"class": re.compile("list-two special-.")})[1:]
    print("~~~BlackBerry KEYone~~~")
    for ull in ulls:
        loader_page_chunker_bbm(ull)


def loader_page_chunker_og(idx, table, headers):
    """
    Given a loader page table, chunk it into lists of table cells.

    :param idx: Index of enumerating tables.
    :type idx: int

    :param table: HTML table tag.
    :type table: bs4.element.Tag

    :param headers: List of table headers.
    :type headers: list(str)
    """
    print("~~~{0}~~~".format(headers[idx]))
    chunks = chunker(table.find_all("td"), 4)
    for chunk in chunks:
        loader_page_printer(chunk)
    print(" ")


def loader_page_chunker_bbm(ull):
    """
    Given a loader page list, chunk it into lists of list items.

    :param ull: HTML unordered list tag.
    :type ull: bs4.element.Tag
    """
    chunks = chunker(ull.find_all("li"), 3)
    for chunk in chunks:
        loader_page_printer(chunk)


def loader_page_printer(chunk):
    """
    Print individual cell texts given a list of table cells.

    :param chunk: List of td tags.
    :type chunk: list(bs4.element.Tag)
    """
    key = unicode_filter(chunk[0].text)
    ver = unicode_filter(chunk[1].text)
    link = unicode_filter(chunk[2].find("a")["href"])
    print("{0}\n    {1}: {2}".format(key, ver, link))


@pem_wrapper
def base_metadata(url, session=None):
    """
    Get BBNDK metadata, base function.

    :param url: URL to check.
    :type url: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    session = generic_session(session)
    req = session.get(url)
    data = req.content
    entries = data.split(b"\n")
    metadata = [entry.split(b",")[1].decode("utf-8") for entry in entries if entry]
    return metadata


def ndk_metadata(session=None):
    """
    Get BBNDK target metadata.

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    data = base_metadata("http://downloads.blackberry.com/upr/developers/update/bbndk/metadata", session)
    metadata = [entry for entry in data if entry.startswith(("10.0", "10.1", "10.2"))]
    return metadata


def sim_metadata(session=None):
    """
    Get BBNDK simulator metadata.

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    metadata = base_metadata("http://downloads.blackberry.com/upr/developers/update/bbndk/simulator/simulator_metadata", session)
    return metadata


def runtime_metadata(session=None):
    """
    Get BBNDK runtime metadata.

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    metadata = base_metadata("http://downloads.blackberry.com/upr/developers/update/bbndk/runtime/runtime_metadata", session)
    return metadata


def series_generator(osversion):
    """
    Generate series/branch name from OS version.

    :param osversion: OS version.
    :type osversion: str
    """
    splits = osversion.split(".")
    return "BB{0}_{1}_{2}".format(*splits[0:3])


@pem_wrapper
def devalpha_urls(osversion, skel, session=None):
    """
    Check individual Dev Alpha autoloader URLs.

    :param osversion: OS version.
    :type osversion: str

    :param skel: Individual skeleton format to try.
    :type skel: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    session = generic_session(session)
    url = "http://downloads.blackberry.com/upr/developers/downloads/{0}{1}.exe".format(skel, osversion)
    req = session.head(url)
    if req.status_code == 200:
        finals = (url, req.headers["content-length"])
    else:
        finals = ()
    return finals


def devalpha_urls_serieshandler(osversion, skeletons):
    """
    Process list of candidate Dev Alpha autoloader URLs.

    :param osversion: OS version.
    :type osversion: str

    :param skeletons: List of skeleton formats to try.
    :type skeletons: list
    """
    skels = skeletons
    for idx, skel in enumerate(skeletons):
        if "<SERIES>" in skel:
            skels[idx] = skel.replace("<SERIES>", series_generator(osversion))
    return skels


def devalpha_urls_bulk(osversion, skeletons, xec, session=None):
    """
    Construct list of valid Dev Alpha autoloader URLs.

    :param osversion: OS version.
    :type osversion: str

    :param skeletons: List of skeleton formats to try.
    :type skeletons: list

    :param xec: ThreadPoolExecutor instance.
    :type xec: concurrent.futures.ThreadPoolExecutor

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    finals = {}
    skels = devalpha_urls_serieshandler(osversion, skeletons)
    for skel in skels:
        final = xec.submit(devalpha_urls, osversion, skel, session).result()
        if final:
            finals[final[0]] = final[1]
    return finals


def devalpha_urls_bootstrap(osversion, skeletons, session=None):
    """
    Get list of valid Dev Alpha autoloader URLs.

    :param osversion: OS version.
    :type osversion: str

    :param skeletons: List of skeleton formats to try.
    :type skeletons: list

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as xec:
        try:
            return devalpha_urls_bulk(osversion, skeletons, xec, session)
        except KeyboardInterrupt:
            xec.shutdown(wait=False)


def dev_dupe_dicter(finals):
    """
    Prepare dictionary to clean duplicate autoloaders.

    :param finals: Dict of URL:content-length pairs.
    :type finals: dict(str: str)
    """
    revo = {}
    for key, val in finals.items():
        revo.setdefault(val, set()).add(key)
    return revo


def dev_dupe_remover(finals, dupelist):
    """
    Filter dictionary of autoloader entries.

    :param finals: Dict of URL:content-length pairs.
    :type finals: dict(str: str)

    :param dupelist: List of duplicate URLs.
    :type duplist: list(str)
    """
    for dupe in dupelist:
        for entry in dupe:
            if "DevAlpha" in entry:
                del finals[entry]
    return finals


def dev_dupe_cleaner(finals):
    """
    Clean duplicate autoloader entries.

    :param finals: Dict of URL:content-length pairs.
    :type finals: dict(str: str)
    """
    revo = dev_dupe_dicter(finals)
    dupelist = [val for key, val in revo.items() if len(val) > 1]
    finals = dev_dupe_remover(finals, dupelist)
    return finals
