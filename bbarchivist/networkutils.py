#!/usr/bin/env python3
"""This module is used for network connections; APIs, downloading, etc."""

import os  # filesystem read
try:
    from defusedxml import ElementTree  # safer XML parsing
except (ImportError, AttributeError):
    from xml.etree import ElementTree  # XML parsing
import re  # regexes
import concurrent.futures  # multiprocessing/threading
import glob  # pem file lookup
import requests  # downloading
from bs4 import BeautifulSoup  # scraping
from bbarchivist import utilities  # parse filesize
from bbarchivist.bbconstants import SERVERS  # lookup servers

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2017 Thurask"


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
    output_directory = os.getcwd() if output_directory is None else output_directory
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
    session = generic_session(session)
    try:
        avlty = session.head(url)
        status = int(avlty.status_code)
        return status == 200 or 300 < status <= 308
    except requests.ConnectionError:
        return False


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
    url = "http://appworld.blackberry.com/ClientAPI/checkcarrier?homemcc={0}&homemnc={1}&devicevendorid=-1&pin=0".format(
        mcc, mnc)
    user_agent = {'User-agent': 'AppWorld/5.1.0.60'}
    req = session.get(url, headers=user_agent)
    root = ElementTree.fromstring(req.text)
    for child in root:
        if child.tag == "country":
            country = child.get("name")
        if child.tag == "carrier":
            carrier = child.get("name")
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
    session = generic_session(session)
    reg = re.compile(r"(\d{1,4}\.)(\d{1,4}\.)(\d{1,4}\.)(\d{1,4})")
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
    header = {"Content-Type": "text/xml;charset=UTF-8"}
    try:
        req = session.post(server, headers=header, data=query, timeout=1)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        return "SR not in system"
    try:
        root = ElementTree.fromstring(req.text)
    except ElementTree.ParseError:
        return "SR not in system"
    else:
        packages = root.findall('./data/content/')
        for package in packages:
            if package.text is not None:
                match = reg.match(package.text)
                if match:
                    return package.text
                else:
                    return "SR not in system"


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
    baseurl = "https://ptcrb.com/vendor/complete/view_complete_request_guest.cfm?modelid={0}".format(
        ptcrbid)
    sess = generic_session(session)
    sess.headers.update({"Referer": "https://ptcrb.com/vendor/complete/complete_request.cfm"})
    soup = generic_soup_parser(baseurl, sess)
    text = soup.get_text()
    text = text.replace("\r\n", " ")
    prelimlist = re.findall("OS .+[^\\n]", text, re.IGNORECASE)
    if not prelimlist:  # Priv
        prelimlist = re.findall(r"[A-Z]{3}[0-9]{3}[\s]", text)
    cleanlist = []
    for item in prelimlist:
        if not item.endswith("\r\n"):  # they should hire QC people...
            cleanlist.append(ptcrb_item_cleaner(item))
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


def ptcrb_item_cleaner(item):
    """
    Cleanup poorly formatted PTCRB entries written by an intern.

    :param item: The item to clean.
    :type item: str
    """
    item = item.replace("<td>", "")
    item = item.replace("</td>", "")
    item = item.replace("\n", "")
    item = item.replace(" (SR", ", SR")
    item = re.sub(r"\s?\((.*)$", "", item)
    item = re.sub(r"\sSV.*$", "", item)
    item = item.replace(")", "")
    item = item.replace(". ", ".")
    item = item.replace(";", "")
    item = item.replace("version", "Version")
    item = item.replace("Verison", "Version")
    if item.count("OS") > 1:
        templist = item.split("OS")
        templist[0] = "OS"
        item = "".join([templist[0], templist[1]])
    item = item.replace("SR", "SW Release")
    item = item.replace(" Version:", ":")
    item = item.replace("Version ", " ")
    item = item.replace(":1", ": 1")
    item = item.replace(", ", " ")
    item = item.replace("Software", "SW")
    item = item.replace("  ", " ")
    item = item.replace("OS ", "OS: ")
    item = item.replace("Radio ", "Radio: ")
    item = item.replace("Release ", "Release: ")
    spaclist = item.split(" ")
    if len(spaclist) > 1:
        spaclist[1] = space_pad(spaclist[1], 11)
        spaclist[3] = space_pad(spaclist[3], 11)
    else:
        spaclist.insert(0, "OS:")
    item = " ".join(spaclist)
    item = item.strip()
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
    folder = {"vzw-vzw": "verizon", "na-att": "att", "na-tmo": "tmo", "common": "default"}
    devices = {"Priv": "qc8992", "DTEK50": "qc8952_64_sfi", "DTEK60": "qc8996"}
    roots = root_generator(folder, build, variant)
    base = "bbry_{2}_autoloader_user-{0}-{1}".format(variant, build.upper(), devices[device])
    if method is None:
        skel = "https://bbapps.download.blackberry.com/Priv/{0}.zip".format(base)
    else:
        skel = "http://ca.blackberry.com/content/dam/{1}/{0}.{2}sum".format(base, roots[device], method.lower())
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
    carrier_variants = ("common", "vzw-vzw", "na-tmo", "na-att")  # device variants
    common_variants = ("common", )  # no Americans
    carrier_devices = ("Priv", )  # may this list never expand in the future
    skels = []
    for dev in devs:
        varlist = carrier_variants if dev in carrier_devices else common_variants
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
        results = []
        for skel in skels:
            avail = xec.submit(availability, skel, session)
            if avail.result():
                results.append(skel)
    return results if results else None


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
    Return scraped autoloader page.

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    url = "http://ca.blackberry.com/support/smartphones/Android-OS-Reload.html"
    session = generic_session(session)
    soup = generic_soup_parser(url, session)
    tables = soup.find_all("table")
    headers = table_headers(soup.find_all("p"))
    for idx, table in enumerate(tables):
        loader_page_chunker(idx, table, headers)


def loader_page_chunker(idx, table, headers):
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
