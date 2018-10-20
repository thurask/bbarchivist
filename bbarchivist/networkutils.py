#!/usr/bin/env python3
"""This module is used for network connections; APIs, downloading, etc."""

import concurrent.futures  # multiprocessing/threading
import glob  # pem file lookup
import os  # filesystem read
import re  # regexes

import requests  # downloading
import user_agent  # user agent
from bs4 import BeautifulSoup  # scraping
from bbarchivist import utilities  # parse filesize
from bbarchivist import xmlutils  # xml work
from bbarchivist.bbconstants import SERVERS  # lookup servers

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


def try_try_again(method):
    """
    Decorator to absorb timeouts, proxy errors, and other common exceptions.

    :param method: Method to use.
    :type method: function
    """
    def wrapper(*args, **kwargs):
        """
        Try function, try it again up to five times, and leave gracefully.
        """
        tries = 5
        for _ in range(tries):
            try:
                result = method(*args, **kwargs)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.ProxyError):
                continue
            else:
                break
        else:
            result = None
        return result
    return wrapper


def generic_session(session=None, uagent_type=None):
    """
    Create a Requests session object on the fly, if need be.

    :param session: Requests session object, created if this is None.
    :type session: requests.Session()

    :param uagent_type: To force a desktop/tablet/smartphone User-Agent. Default is None.
    :type uagent_type: string
    """
    sess = requests.Session() if session is None else session
    uagent = user_agent.generate_user_agent(device_type=uagent_type)
    sess.headers.update({"User-Agent": uagent})
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
    baseurl = "https://dl.google.com/android/repository/platform-tools-latest"
    dlurls = ["{1}-{0}.zip".format(plat, baseurl) for plat in platforms]
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
    baseurl = "http://appworld.blackberry.com/ClientAPI/checkcarrier"
    url = "{2}?homemcc={0}&homemnc={1}&devicevendorid=-1&pin=0".format(mcc, mnc, baseurl)
    uagent = {'User-Agent': 'AppWorld/5.1.0.60'}
    req = session.get(url, headers=uagent)
    country, carrier = xmlutils.cchecker_get_tags(req.text)
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
    query = xmlutils.prep_carrier_query(npc, device, upg, forced)
    header = {"Content-Type": "text/xml;charset=UTF-8"}
    req = session.post(url, headers=header, data=query)
    return xmlutils.parse_carrier_xml(req.text, blitz)


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
    query = xmlutils.prep_sr_lookup(osver)
    reqtext = sr_lookup_poster(query, server, session)
    packtext = xmlutils.parse_sr_lookup(reqtext)
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
    query = xmlutils.prep_available_bundle(device, npc)
    header = {"Content-Type": "text/xml;charset=UTF-8"}
    req = session.post(server, headers=header, data=query)
    bundlelist = xmlutils.parse_available_bundle(req.text)
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
    sess = generic_session(session, uagent_type="desktop")
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
    devices = {"KEYone": "qc8953", "Motion": "qc8953krypton", "KEY2": "sdm660"}
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
        baseurl = "https://bbapps.download.blackberry.com/Priv"
        skel = "{1}/{0}.zip".format(base, baseurl)
    else:
        baseurl = "https://ca.blackberry.com/content/dam"
        skel = "{3}/{1}/{0}.{2}sum".format(base, roots[device], method.lower(), baseurl)
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
    bbmlist = ("KEYone", "Motion", "KEY2", "KEY2LE")   # BB Mobile
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


def base_metadata_url(alternate=None):
    """
    Return metadata URL.

    :param alternate: If the URL is for the simulator metadata. Default is False.
    :type alternate: str
    """
    baseurl = "http://downloads.blackberry.com/upr/developers/update/bbndk"
    tail = "{0}/{0}_metadata".format(alternate) if alternate is not None else "metadata"
    return "{0}/{1}".format(baseurl, tail)


def ndk_metadata(session=None):
    """
    Get BBNDK target metadata.

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    ndkurl = base_metadata_url()
    data = base_metadata(ndkurl, session)
    metadata = [entry for entry in data if entry.startswith(("10.0", "10.1", "10.2"))]
    return metadata


def sim_metadata(session=None):
    """
    Get BBNDK simulator metadata.

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    simurl = base_metadata_url("simulator")
    metadata = base_metadata(simurl, session)
    return metadata


def runtime_metadata(session=None):
    """
    Get BBNDK runtime metadata.

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    rturl = base_metadata_url("runtime")
    metadata = base_metadata(rturl, session)
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
    baseurl = "http://downloads.blackberry.com/upr/developers/downloads"
    url = "{2}/{0}{1}.exe".format(skel, osversion, baseurl)
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
