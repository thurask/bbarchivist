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
__copyright__ = "Copyright 2015 Thurask"


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


def get_length(url):
    """
    Get content-length header from some URL.

    :param url: The URL to check.
    :type url: str
    """
    os.environ["REQUESTS_CA_BUNDLE"] = grab_pem()
    if url is None:
        return 0
    try:
        heads = requests.head(url)
        fsize = heads.headers['content-length']
        return int(fsize)
    except requests.ConnectionError:
        return 0


def download(url, output_directory=None, lazy=False):
    """
    Download file from given URL.

    :param url: URL to download from.
    :type url: str

    :param output_directory: Download folder. Default is local.
    :type output_directory: str

    :param lazy: Whether or not to have simple output. False by default.
    :type lazy: bool
    """
    if output_directory is None:
        output_directory = os.getcwd()
    local_filename = url.split('/')[-1]
    local_filename = utilities.stripper(local_filename)
    os.environ["REQUESTS_CA_BUNDLE"] = grab_pem()
    req = requests.get(url, stream=True)
    fsize = req.headers['content-length']
    if req.status_code != 404:  # 200 OK
        if not lazy:
            print("DOWNLOADING:",
                  local_filename,
                  "[" + utilities.fsizer(fsize) + "]")
        else:
            if int(fsize) > 90000000:
                print("DOWNLOADING OS",
                      "[" + utilities.fsizer(fsize) + "]")
            else:
                print("DOWNLOADING RADIO",
                      "[" + utilities.fsizer(fsize) + "]")
        fname = output_directory + "/" + os.path.basename(url)
        with open(fname, "wb") as file:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    file.write(chunk)
                    file.flush()


def download_bootstrap(urls, outdir=None, lazy=False, workers=5):
    """
    Run downloaders for each file in given URL iterable.

    :param urls: URLs to download.
    :type urls: list

    :param outdir: Download folder. Default is handled in :func:`download`.
    :type outdir: str

    :param lazy: Whether or not to have simple output. False by default.
    :type lazy: bool

    :param workers: Number of worker processes. Default is 5.
    :type workers: int
    """
    if len(urls) < workers:
        workers = len(urls)
    spinman = utilities.SpinManager()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as xec:
        try:
            spinman.start()
            for url in urls:
                xec.submit(download, url, outdir, lazy)
        except (KeyboardInterrupt, SystemExit):
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
    baseurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/"
    baseurl += hashedsoftwareversion
    return baseurl


def availability(url):
    """
    Check HTTP status code of given URL.
    200 or 301-308 is OK, else is not.

    :param url: URL to check.
    :type url: str
    """
    os.environ["REQUESTS_CA_BUNDLE"] = grab_pem()
    try:
        avlty = requests.head(url)
        status = int(avlty.status_code)
        return (status == 200) or (300 < status <= 308)
    except requests.ConnectionError:
        return False


def carrier_checker(mcc, mnc):
    """
    Query BlackBerry World to map a MCC and a MNC to a country and carrier.

    :param mcc: Country code.
    :type mcc: int

    :param mnc: Network code.
    :type mnc: int
    """
    url = "http://appworld.blackberry.com/ClientAPI/checkcarrier?homemcc="
    url += str(mcc)
    url += "&homemnc="
    url += str(mnc)
    url += "&devicevendorid=-1&pin=0"
    user_agent = {'User-agent': 'AppWorld/5.1.0.60'}
    os.environ["REQUESTS_CA_BUNDLE"] = grab_pem()
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
    return str(mcc).zfill(3) + str(mnc).zfill(3) + "30"


def carrier_update_request(npc, device,
                           upgrade=False,
                           blitz=False,
                           forced=None):
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
    if upgrade:
        upg = "upgrade"
    else:
        upg = "repair"
    if forced is None:
        forced = "latest"
    url = "https://cs.sl.blackberry.com/cse/updateDetails/2.2/"
    query = '<?xml version="1.0" encoding="UTF-8"?>'
    query += '<updateDetailRequest version="2.2.1"'
    query += ' authEchoTS="1366644680359">'
    query += "<clientProperties>"
    query += "<hardware>"
    query += "<pin>0x2FFFFFB3</pin><bsn>1128121361</bsn>"
    query += "<imei>004401139269240</imei>"
    query += "<id>0x" + device + "</id>"
    query += "</hardware>"
    query += "<network>"
    query += "<homeNPC>0x" + str(npc) + "</homeNPC>"
    query += "<iccid>89014104255505565333</iccid>"
    query += "</network>"
    query += "<software>"
    query += "<currentLocale>en_US</currentLocale>"
    query += "<legalLocale>en_US</legalLocale>"
    query += "</software>"
    query += "</clientProperties>"
    query += "<updateDirectives>"
    query += '<allowPatching type="REDBEND">true</allowPatching>'
    query += "<upgradeMode>" + upg + "</upgradeMode>"
    query += "<provideDescriptions>false</provideDescriptions>"
    query += "<provideFiles>true</provideFiles>"
    query += "<queryType>NOTIFICATION_CHECK</queryType>"
    query += "</updateDirectives>"
    query += "<pollType>manual</pollType>"
    query += "<resultPackageSetCriteria>"
    query += '<softwareRelease softwareReleaseVersion="'
    query += forced
    query += '" />'
    query += "<releaseIndependent>"
    query += '<packageType operation="include">application</packageType>'
    query += "</releaseIndependent>"
    query += "</resultPackageSetCriteria>"
    query += "</updateDetailRequest>"
    header = {"Content-Type": "text/xml;charset=UTF-8"}
    os.environ["REQUESTS_CA_BUNDLE"] = grab_pem()
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
    swver = ""
    if sw_exists is None:
        swver = "N/A"
    else:
        for child in root.iter("softwareReleaseMetadata"):
            swver = child.get("softwareReleaseVersion")
    files = []
    osver = ""
    radver = ""
    package_exists = root.find('./data/content/fileSets/fileSet')
    if package_exists is not None:
        baseurl = package_exists.get("url") + "/"
        for child in root.iter("package"):
            if not blitz:
                files.append(baseurl + child.get("path"))
            else:
                if child.get("type") not in ["system:radio",
                                             "system:desktop",
                                             "system:os"]:
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
    query += '<osVersion>'
    query += osver
    query += '</osVersion><omadmEnabled>false</omadmEnabled>'
    query += '</software></clientProperties>'
    query += '</srVersionLookupRequest>'
    header = {"Content-Type": "text/xml;charset=UTF-8"}
    os.environ["REQUESTS_CA_BUNDLE"] = grab_pem()
    try:
        req = requests.post(server, headers=header, data=query, timeout=1)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        return "SR not in system"
    root = xml.etree.ElementTree.fromstring(req.text)
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
            results = {"p": None,
                       "a1": None,
                       "a2": None,
                       "b1": None,
                       "b2": None}
            for key in results:
                results[key] = xec.submit(sr_lookup,
                                          osv,
                                          SERVERS[key]).result()
            return results
        except KeyboardInterrupt:
            xec.shutdown(wait=False)


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
    query += '<clientProperties><hardware><id>0x'
    query += device
    query += '</id><isBootROMSecure>true</isBootROMSecure></hardware>'
    query += '<network><vendorId>0x0</vendorId><homeNPC>0x'
    query += npc
    query += '</homeNPC><currentNPC>0x'
    query += npc
    query += '</currentNPC></network><software>'
    query += '<currentLocale>en_US</currentLocale>'
    query += '<legalLocale>en_US</legalLocale>'
    query += '<osVersion>10.0.0.0</osVersion>'
    query += '<radioVersion>10.0.0.0</radioVersion></software>'
    query += '</clientProperties><updateDirectives><bundleVersionFilter>'
    query += '</bundleVersionFilter></updateDirectives>'
    query += '</availableBundlesRequest>'
    header = {"Content-Type": "text/xml;charset=UTF-8"}
    os.environ["REQUESTS_CA_BUNDLE"] = grab_pem()
    req = requests.post(server, headers=header, data=query)
    root = xml.etree.ElementTree.fromstring(req.text)
    package = root.find('./data/content')
    bundlelist = []
    adder = bundlelist.append
    for child in package:
        adder(child.attrib["version"])
    return bundlelist


def ptcrb_scraper(ptcrbid):
    """
    Get the PTCRB results for a given device.

    :param ptcrbid: Numerical ID from PTCRB (end of URL).
    :type ptcrbid: str
    """
    baseurl = "https://ptcrb.com/vendor/complete/"
    baseurl += "view_complete_request_guest.cfm?modelid=" + ptcrbid
    os.environ["REQUESTS_CA_BUNDLE"] = grab_pem()
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


def kernel_scraper():
    """
    Scrape BlackBerry's GitHub kernel repo for available branches.
    """
    url = "https://github.com/blackberry/android-linux-kernel/branches/all"
    os.environ["REQUESTS_CA_BUNDLE"] = grab_pem()
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    text = soup.get_text()
    kernlist = re.findall(r"msm[0-9]{4}\/[A-Z0-9]{6}", text, re.IGNORECASE)
    return kernlist
