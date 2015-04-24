#!/usr/bin/env python3

import os  # filesystem read
import requests  # downloading
import queue  # downloader multithreading
import threading  # downloader multithreading
import binascii  # downloader thread naming
import xml.etree.ElementTree  # XML parsing


class Downloader(threading.Thread):
    """
    Downloads files attached to supplied threads from DownloadManager.
    Based on:
    http://pipe-devnull.com/2012/09/13/queued-threaded-http-downloader-in-python.html
    """
    def __init__(self, queue, output_directory):
        threading.Thread.__init__(self, name=binascii.hexlify(os.urandom(8)))
        self.queue = queue
        self.output_directory = output_directory

    def run(self):
        while True:
            # gets the url from the queue
            url = self.queue.get()
            # download the file
            self.download(url)
            # send a signal to the queue that the job is done
            self.queue.task_done()

    def download(self, url):
        local_filename = url.split('/')[-1]
        print("Downloading:", local_filename)
        r = requests.get(url, stream=True)
        if (r.status_code != 404):  # 200 OK
            fname = self.output_directory + "/" + os.path.basename(url)
            with open(fname, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        f.flush()
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
        self.thread_count = thread_count
        self.download_dict = download_dict
        self.output_directory = output_directory
    # Start the downloader threads, fill the queue with the URLs and
    # then feed the threads URLs via the queue

    def begin_downloads(self):
        dlqueue = queue.Queue()
        # Create i thread pool and give them a queue
        for t in range(self.thread_count):
            t = Downloader(dlqueue, self.output_directory)
            t.setDaemon(True)
            t.start()
        # Load the queue from the download dict
        for linkname in self.download_dict:
            # print uri
            dlqueue.put(self.download_dict[linkname])

        # Wait for the queue to finish
        dlqueue.join()
        return


def availability(url):
    """
    Check HTTP status code of given URL.
    200 or 301-308 is OK, else is not.
    :param url: URL to check.
    :type url: http://site.to/check/
    """
    try:
        av = requests.head(str(url))
    except requests.ConnectionError:
        return False
    else:
        status = int(av.status_code)
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
    r = requests.get(url, headers=user_agent)
    root = xml.etree.ElementTree.fromstring(r.text)
    for child in root:
        if child.tag == "country":
            country = child.get("name")
        if child.tag == "carrier":
            carrier = child.get("name")
    return country, carrier


def carrier_update_request(mcc, mnc, device, download=False, upgrade=False):
    """
    Query BlackBerry servers, check which update is out for a carrier.
    :param mcc: Country code.
    :type mcc: int
    :param mnc: Network code.
    :type mnc: int
    :param device: Hexadecimal hardware ID.
    :type device: str
    :param download: Whether to download files. False by default.
    :type download: bool
    :param upgrade: Whether to use upgrade files. False by default.
    :type upgrade: bool
    """
    if upgrade:
        upg = "upgrade"
    else:
        upg = "repair"
    npc = str(mcc).zfill(3) + str(mnc).zfill(3) + "30"
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
    r = requests.post(url, headers=header, data=query)
    root = xml.etree.ElementTree.fromstring(r.text)
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
