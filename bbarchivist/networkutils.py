#!/usr/bin/env python3

import os  # filesystem read
import requests  # downloading
import time  # time for downloader
import queue  # downloader multithreading
import threading  # downloader multithreading
import binascii  # downloader thread naming
import math  # rounding of floats
import xml.etree.ElementTree  # XML parsing
import re  # regexes
import hashlib  # base url creation


class Downloader(threading.Thread):
    """
    Downloads files attached to supplied threads from DownloadManager.
    Based on:
    http://pipe-devnull.com/2012/09/13/queued-threaded-http-downloader-in-python.html
    """

    def __init__(self, dlqueue, output_directory):
        """
        Initiate downloader thread.
        :param queue: What to download.
        :type queue: dict

        :param output_directory: Where to output.
        :type output_directory: str
        """
        threading.Thread.__init__(self, name=binascii.hexlify(os.urandom(8)))
        self.queue = dlqueue
        self.output_directory = output_directory

    def run(self):
        """
        Download files from queue.
        """
        while True:
            # gets the url from the queue
            url = self.queue.get()
            # download the file
            self.download(url)
            # send a signal to the queue that the job is done
            self.queue.task_done()

    def download(self, url):
        """
        Download file from given URL.

        :param url: URL to download from.
        :type url: str
        """
        t_start = time.clock()
        local_filename = url.split('/')[-1]
        print("Downloading:", local_filename)
        req = requests.get(url, stream=True)
        if req.status_code != 404:  # 200 OK
            fname = self.output_directory + "/" + os.path.basename(url)
            with open(fname, "wb") as file:
                for chunk in req.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        file.write(chunk)
                        file.flush()
            t_elapsed = time.clock() - t_start
            t_elapsed_proper = math.ceil(t_elapsed * 100) / 100
            print(
                "Downloaded " +
                local_filename +
                " in " +
                str(t_elapsed_proper) +
                " seconds")
        else:
            print("* Thread: " + self.name + " Bad URL: " + url)
            return


class DownloadManager():
    """
    Class that handles queued downloads.
    Based on:
    http://pipe-devnull.com/2012/09/13/queued-threaded-http-downloader-in-python.html
    """

    def __init__(self, download_dict, output_directory, thread_count=5):
        """
        Initiate download manager.

        :param download_dict: Dictionary of download URLs.
        :type download_dict: dict

        :param output_directory: Where to output.
        :type output_directory: str

        :param thread_count: Number of threads. 5 by default.
        :type thread_count: int
        """
        self.thread_count = thread_count
        self.download_dict = download_dict
        self.output_directory = output_directory\

    # Start the downloader threads, fill the queue with the URLs and
    # then feed the threads URLs via the queue

    def begin_downloads(self):
        """
        Start :class:`Downloader` threads for queued downloads.
        """
        dlqueue = queue.Queue()
        # Create i thread pool and give them a queue
        for thr in range(self.thread_count):
            thr = Downloader(dlqueue, self.output_directory)
            thr.setDaemon(True)
            thr.start()
        # Load the queue from the download dict
        for linkname in self.download_dict:
            # print uri
            dlqueue.put(self.download_dict[linkname])

        # Wait for the queue to finish
        dlqueue.join()
        return


def create_base_url(softwareversion):
    '''
    Make the root URL for production server files.
    :param softwareversion: Software version to hash.
    :type softwareversion: str
    '''
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
    try:
        avlty = requests.head(str(url))
    except requests.ConnectionError:
        return False
    else:
        status = int(avlty.status_code)
        if (status == 200) or (300 < status <= 308):
            return True
        else:
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


def carrier_update_request(mcc, mnc, device,
                           upgrade=False,
                           blitz=False):
    """
    Query BlackBerry servers, check which update is out for a carrier.

    :param mcc: Country code.
    :type mcc: int

    :param mnc: Network code.
    :type mnc: int

    :param device: Hexadecimal hardware ID.
    :type device: str

    :param upgrade: Whether to use upgrade files. False by default.
    :type upgrade: bool

    :param blitz: Whether or not to create a blitz package. False by default.
    :type blitz: bool
    """
    if upgrade:
        upg = "upgrade"
    else:
        upg = "repair"
    url = "https://cs.sl.blackberry.com/cse/updateDetails/2.2/"
    npc = return_npc(mcc, mnc)
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
    query += "<homeNPC>0x" + npc + "</homeNPC>"
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
    query += '<softwareRelease softwareReleaseVersion="latest" />'
    query += "<releaseIndependent>"
    query += '<packageType operation="include">application</packageType>'
    query += "</releaseIndependent>"
    query += "</resultPackageSetCriteria>"
    query += "</updateDetailRequest>"
    header = {"Content-Type": "text/xml;charset=UTF-8"}
    req = requests.post(url, headers=header, data=query)
    root = xml.etree.ElementTree.fromstring(req.text)
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


def software_release_lookup(osver, server):
    """
    Software release lookup, with choice of server.
    :data:`bbarchivist.bbconstants.SERVERLIST` for server list.

    :param osver: OS version to lookup, 10.x.y.zzzz.
    :type osver: str

    :param server: Server to use.
    :type server: str
    """
    reg = re.compile("(\d{1,4}\.)(\d{1,4}\.)(\d{1,4}\.)(\d{1,4})")
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
    req = requests.post(server, headers=header, data=query)
    root = xml.etree.ElementTree.fromstring(req.text)
    packages = root.findall('./data/content/')
    for package in packages:
        if package.text is not None:
            match = reg.match(package.text)
            if match:
                return package.text
            else:
                return "SR not in system"


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
    req = requests.post(server, headers=header, data=query, verify=True)
    root = xml.etree.ElementTree.fromstring(req.text)
    package = root.find('./data/content')
    bundlelist = []
    for child in package:
        bundlelist.append(child.attrib["version"])
    return bundlelist
