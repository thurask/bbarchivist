#!/usr/bin/env python3
"""This module is used for network connections; APIs, downloading, etc."""

import os  # filesystem read
import xml.etree.ElementTree  # XML parsing
import re  # regexes
import hashlib  # base url creation
import concurrent.futures  # multiprocessing/threading
import glob  # pem file lookup
import requests  # downloading
from bs4 import BeautifulSoup  # scraping
from bbarchivist import utilities  # parse filesize
from bbarchivist.bbconstants import SERVERS  # lookup servers

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def grab_pem():
    """
    Work with either local cacerts or system cacerts. Since cx_freeze is dumb.
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


@pem_wrapper
def get_length(url):
    """
    Get content-length header from some URL.

    :param url: The URL to check.
    :type url: str
    """
    if url is None:
        return 0
    try:
        heads = requests.head(url)
        fsize = heads.headers['content-length']
        return int(fsize)
    except requests.ConnectionError:
        return 0


@pem_wrapper
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
    sname = utilities.stripper(lfname)
    fname = os.path.join(output_directory, lfname)
    with open(fname, "wb") as file:
        req = requests.get(url, stream=True)
        clength = req.headers['content-length']
        fsize = utilities.fsizer(clength)
        if req.status_code == 200:  # 200 OK
            print("DOWNLOADING {0} [{1}]".format(sname, fsize))
            for chunk in req.iter_content(chunk_size=1024):
                file.write(chunk)
        else:
            print("ERROR: HTTP {0} IN {1}".format(req.status_code, lfname))
    if os.stat(fname).st_size == 0:
        os.remove(fname)

def download_bootstrap(urls, outdir=None, workers=5):
    """
    Run downloaders for each file in given URL iterable.

    :param urls: URLs to download.
    :type urls: list

    :param outdir: Download folder. Default is handled in :func:`download`.
    :type outdir: str

    :param workers: Number of worker processes. Default is 5.
    :type workers: int
    """
    workers = len(urls) if len(urls) < workers else workers
    spinman = utilities.SpinManager()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as xec:
        try:
            spinman.start()
            for url in urls:
                xec.submit(download, url, outdir)
        except (KeyboardInterrupt, SystemExit):  # pragma: no cover
            xec.shutdown()
            spinman.stop()
    spinman.stop()
    utilities.spinner_clear()
    utilities.line_begin()


def create_base_url(softwareversion):
    """
    Make the root URL for production server files.

    :param softwareversion: Software version to hash.
    :type softwareversion: str
    """
    # Hash software version
    swhash = hashlib.sha1(softwareversion.encode('utf-8'))
    hashedsoftwareversion = swhash.hexdigest()
    # Root of all urls
    baseurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/" + hashedsoftwareversion
    return baseurl


@pem_wrapper
def availability(url):
    """
    Check HTTP status code of given URL.
    200 or 301-308 is OK, else is not.

    :param url: URL to check.
    :type url: str
    """
    try:
        avlty = requests.head(url)
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
def carrier_checker(mcc, mnc):
    """
    Query BlackBerry World to map a MCC and a MNC to a country and carrier.

    :param mcc: Country code.
    :type mcc: int

    :param mnc: Network code.
    :type mnc: int
    """
    url = "http://appworld.blackberry.com/ClientAPI/checkcarrier?homemcc={0}&homemnc={1}&devicevendorid=-1&pin=0".format(
        mcc, mnc)
    user_agent = {'User-agent': 'AppWorld/5.1.0.60'}
    req = requests.get(url, headers=user_agent)
    root = xml.etree.ElementTree.fromstring(req.text)
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
def carrier_query(npc, device, upgrade=False, blitz=False, forced=None):
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
    """
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
    req = requests.post(url, headers=header, data=query)
    return parse_carrier_xml(req.text, blitz)


def parse_carrier_xml(data, blitz=False):
    """
    Parse the response to a carrier update request and return the juicy bits.

    :param data: The data to parse.
    :type data: xml

    :param blitz: Whether or not to create a blitz package. False by default.
    :type blitz: bool
    """
    root = xml.etree.ElementTree.fromstring(data)
    sw_exists = root.find('./data/content/softwareReleaseMetadata')
    swver = "N/A" if sw_exists is None else ""
    if sw_exists is not None:
        for child in root.iter("softwareReleaseMetadata"):
            swver = child.get("softwareReleaseVersion")
    files = []
    osver = ""
    radver = ""
    package_exists = root.find('./data/content/fileSets/fileSet')
    if package_exists is not None:
        baseurl = "{0}/".format(package_exists.get("url"))
        for child in root.iter("package"):
            if not blitz:
                files.append(baseurl + child.get("path"))
            else:
                if child.get("type") not in ["system:radio", "system:desktop", "system:os"]:
                    files.append(baseurl + child.get("path"))
            if child.get("type") == "system:radio":
                radver = child.get("version")
            if child.get("type") == "system:desktop":
                osver = child.get("version")
            if child.get("type") == "system:os":
                osver = child.get("version")
            else:
                pass
    return(swver, osver, radver, files)


@pem_wrapper
def sr_lookup(osver, server):
    """
    Software release lookup, with choice of server.
    :data:`bbarchivist.bbconstants.SERVERLIST` for server list.

    :param osver: OS version to lookup, 10.x.y.zzzz.
    :type osver: str

    :param server: Server to use.
    :type server: str
    """
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
        req = requests.post(server, headers=header, data=query, timeout=1)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        return "SR not in system"
    try:
        root = xml.etree.ElementTree.fromstring(req.text)
    except xml.etree.ElementTree.ParseError:
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


def sr_lookup_bootstrap(osv):
    """
    Run lookups for each server for given OS.

    :param osv: OS to check.
    :type osv: str
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
            for key in results:
                results[key] = xec.submit(sr_lookup, osv, SERVERS[key]).result()
            return results
        except KeyboardInterrupt:  # pragma: no cover
            xec.shutdown(wait=False)


@pem_wrapper
def available_bundle_lookup(mcc, mnc, device):
    """
    Check which software releases were ever released for a carrier.

    :param mcc: Country code.
    :type mcc: int

    :param mnc: Network code.
    :type mnc: int

    :param device: Hexadecimal hardware ID.
    :type device: str
    """
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
    req = requests.post(server, headers=header, data=query)
    root = xml.etree.ElementTree.fromstring(req.text)
    package = root.find('./data/content')
    bundlelist = [child.attrib["version"] for child in package]
    return bundlelist


@pem_wrapper
def ptcrb_scraper(ptcrbid):
    """
    Get the PTCRB results for a given device.

    :param ptcrbid: Numerical ID from PTCRB (end of URL).
    :type ptcrbid: str
    """
    baseurl = "https://ptcrb.com/vendor/complete/view_complete_request_guest.cfm?modelid={0}".format(
        ptcrbid)
    req = requests.get(baseurl)
    soup = BeautifulSoup(req.content, 'html.parser')
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
        while len(spaclist[1]) < 11:
            spaclist[1] += " "
        while len(spaclist[3]) < 11:
            spaclist[3] += " "
    else:
        spaclist.insert(0, "OS:")
    item = " ".join(spaclist)
    item = item.strip()
    return item


@pem_wrapper
def kernel_scraper(utils=False):
    """
    Scrape BlackBerry's GitHub kernel repo for available branches.

    :param utils: Check android-utils repo instead of android-linux-kernel. Default is False.
    :type utils: bool
    """
    repo = "android-utils" if utils else "android-linux-kernel"
    kernlist = []
    for page in range(1, 10):
        url = "https://github.com/blackberry/{0}/branches/all?page={1}".format(repo, page)
        req = requests.get(url)
        soup = BeautifulSoup(req.content, 'html.parser')
        if soup.find("div", {"class": "no-results-message"}):
            break
        else:
            text = soup.get_text()
            kernlist.extend(re.findall(r"msm[0-9]{4}\/[A-Z0-9]{6}", text, re.IGNORECASE))
    return kernlist


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
    devices = {"Priv": "qc8992", "DTEK50": "qc8952_64_sfi"}
    roots = {"Priv": "bbfoundation/hashfiles_priv/{0}".format(folder[variant]), "DTEK50": "bbSupport/DTEK50"}
    base = "bbry_{2}_autoloader_user-{0}-{1}".format(variant, build.upper(), devices[device])
    if method is None:
        skel = "https://bbapps.download.blackberry.com/Priv/{0}.zip".format(base)
    else:
        skel = "http://ca.blackberry.com/content/dam/{1}/{0}.{2}sum".format(base, roots[device], method.lower())
    return skel


def droid_scanner(build, device, method=None):
    """
    Check for Android autoloaders on BlackBerry's site.

    :param build: Build to check, 3 letters + 3 numbers.
    :type build: str

    :param device: Device to check.
    :type device: str

    :param method: None for regular OS links, "sha256/512" for SHA256 or 512 hash.
    :type method: str
    """
    if isinstance(device, list):
        devs = device
    else:
        devs = []
        devs.append(device)
    carrier_variants = ("common", "vzw-vzw", "na-tmo", "na-att")  # device variants
    common_variants = ("common", )  # no Americans
    skels = []
    for dev in devs:
        varlist = carrier_variants if dev == "Priv" else common_variants
        for var in varlist:
            skel = make_droid_skeleton(method, build, dev, var)
            skels.append(skel)
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(skels)) as xec:
        results = []
        for skel in skels:
            avail = xec.submit(availability, skel)
            if avail.result():
                results.append(skel)
        return results if results else None


def base_metadata(url):
    """
    Get BBNDK metadata, base function.
    """
    req = requests.get(url)
    data = req.content
    entries = data.split(b"\n")
    metadata = [entry.split(b",")[1].decode("utf-8") for entry in entries if entry]
    return metadata


def ndk_metadata():
    """
    Get BBNDK target metadata.
    """
    data = base_metadata("http://downloads.blackberry.com/upr/developers/update/bbndk/metadata")
    metadata = [entry for entry in data if entry.startswith(("10.0", "10.1", "10.2"))]
    return metadata


def sim_metadata():
    """
    Get BBNDK simulator metadata.
    """
    metadata = base_metadata("http://downloads.blackberry.com/upr/developers/update/bbndk/simulator/simulator_metadata")
    return metadata


def runtime_metadata():
    """
    Get BBNDK runtime metadata.
    """
    metadata = base_metadata("http://downloads.blackberry.com/upr/developers/update/bbndk/runtime/runtime_metadata")
    return metadata


def series_generator(osversion):
    """
    Generate series/branch name from OS version.

    :param osversion: OS version.
    :type osversion: str
    """
    splits = osversion.split(".")
    return "BB{0}_{1}_{2}".format(*splits[0:3])


def devalpha_urls(osversion, skel):
    """
    Check individual Dev Alpha autoloader URLs.

    :param osversion: OS version.
    :type osversion: str

    :param skel: Individual skeleton format to try.
    :type skel: str
    """
    url = "http://downloads.blackberry.com/upr/developers/downloads/{0}{1}.exe".format(skel, osversion)
    req = requests.head(url)
    if req.status_code == 200:
        finals = (url, req.headers["content-length"])
    else:
        finals = ()
    return finals


def devalpha_urls_bootstrap(osversion, skeletons):
    """
    Get list of valid Dev Alpha autoloader URLs.

    :param osversion: OS version.
    :type osversion: str

    :param skeletons: List of skeleton formats to try.
    :type skeletons: list
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as xec:
        try:
            finals = {}
            skels = skeletons
            for idx, skel in enumerate(skeletons):
                if "<SERIES>" in skel:
                    skels[idx] = skel.replace("<SERIES>", series_generator(osversion))
            for skel in skels:
                final = xec.submit(devalpha_urls, osversion, skel).result()
                if final:
                    finals[final[0]] = final[1]
            return finals
        except KeyboardInterrupt:  # pragma: no cover
            xec.shutdown(wait=False)


def dev_dupe_cleaner(finals):
    """
    Clean duplicate autoloader entries.

    :param finals: Dict of URL:content-length pairs.
    :type finals: dict(str: str)
    """
    revo = {}
    for key, val in finals.items():
        revo.setdefault(val, set()).add(key)
    dupelist = [val for key, val in revo.items() if len(val) > 1]
    for dupe in dupelist:
        for entry in dupe:
            if "DevAlpha" in entry:
                del finals[entry]
    return finals
