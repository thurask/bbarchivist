#!/usr/bin/env python3

import os  # filesystem read
import requests  # downloading
import time  # time for downloader
import queue  # downloader multithreading
import threading  # downloader multithreading
import binascii  # downloader thread naming
import math  # rounding of floats


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
        t_start = time.clock()
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
            t_elapsed = time.clock() - t_start
            t_elapsed_proper = math.ceil(t_elapsed * 100) / 100
            print(
                "Downloaded " +
                url +
                " in " +
                str(t_elapsed_proper) +
                " seconds")
            f.close()
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
