#!/usr/bin/env python3

from . import bbconstants
from . import networkutils
from . import utilities
import hashlib
import time
import os


def do_magic(osversion, loop=False, log=False):
    """
    Lookup a software release from an OS. Can iterate.

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str:param mcc: Country code.

    :param loop: Whether or not to automatically lookup. Default is false.
    :type loop: bool

    :param log: Whether to log. Default is False
    :type log: bool
    """
    print("~~~AUTOLOOKUP VERSION", bbconstants.VERSION + "~~~")
    print("")
    if log:
        logfile = time.strftime("%Y_%m_%d_%H%M%S") + ".txt"
        record = os.path.join(os.path.expanduser("~"),
                              logfile)
    try:
        while True:
            swrelease = ""
            print("NOW SCANNING:", osversion, end="\r"),
            a1rel = networkutils.software_release_lookup(osversion,
                                                         bbconstants.SERVERS["a1"])  # @IgnorePep8
            if a1rel != "SR not in system" and a1rel is not None:
                a1av = "A1"
            else:
                a1av = "  "
            b1rel = networkutils.software_release_lookup(osversion,
                                                         bbconstants.SERVERS["b1"])  # @IgnorePep8
            if b1rel != "SR not in system" and b1rel is not None:
                b1av = "B1"
            else:
                b1av = "  "
            b2rel = networkutils.software_release_lookup(osversion,
                                                         bbconstants.SERVERS["b2"])  # @IgnorePep8
            if b2rel != "SR not in system" and b2rel is not None:
                b2av = "B2"
            else:
                b2av = "  "
            prel = networkutils.software_release_lookup(osversion,
                                                        bbconstants.SERVERS["p"])  # @IgnorePep8
            if prel != "SR not in system" and prel is not None:
                pav = "PD"
                # Hash software version
                swhash = hashlib.sha1(prel.encode('utf-8'))
                hashedsoftwareversion = swhash.hexdigest()
                # Root of all urls
                baseurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/"
                baseurl += hashedsoftwareversion
                # Check availability of software release
                avail = networkutils.availability(baseurl)
                if avail:
                    available = "Available"
                else:
                    available = "Unavailable"
            else:
                pav = "  "
                available = "Unavailable"
            swrelset = set([a1rel, b1rel, b2rel, prel])
            for i in swrelset:
                if i != "SR not in system" and i is not None:
                    swrelease = i
                    break
            else:
                swrelease = ""
            if swrelease != "":
                out = "OS {} - SR {} - [{}|{}|{}|{}] - {}".format(osversion,
                                                                  swrelease,
                                                                  pav,
                                                                  a1av,
                                                                  b1av,
                                                                  b2av,
                                                                  available)
                if log:
                    with open(record, "a") as rec:
                        rec.write(out+"\n")
                print(out)
            if not loop:
                raise KeyboardInterrupt  # hack, but whateva, I do what I want
            else:
                osversion = utilities.version_incrementer(osversion, 3)
                swrelease = ""
                continue
    except KeyboardInterrupt:
        raise SystemExit
