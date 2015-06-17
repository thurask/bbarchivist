#!/usr/bin/env python3

from bbarchivist import networkutils  # lookup, if sw not specified
from bbarchivist import utilities  # increment version, if radio not specified
from bbarchivist import bbconstants  # versions/constants
from bbarchivist import textgenerator  # actually writing


def do_magic(osversion, radioversion=None, softwareversion=None):
    """
    Generate debrick/core/radio links for given OS, radio, software release.

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz. Can be guessed.
    :type radioversion: str

    :param softwareversion: Software version, 10.x.y.zzzz. Can be guessed.
    :type softwareversion: str
    """
    if radioversion is None:
        radioversion = utilities.version_incrementer(osversion, 1)
    if softwareversion is None:
        serv = bbconstants.SERVERS["p"]
        softwareversion = networkutils.software_release_lookup(osversion, serv)
        if softwareversion == "SR not in system":
            print("SOFTWARE RELEASE NOT FOUND")
            cont = utilities.str2bool(input("INPUT MANUALLY? Y/N "))
            if cont:
                softwareversion = input("SOFTWARE RELEASE: ")
            else:
                print("\nEXITING...")
                raise SystemExit  # bye bye
    baseurl = networkutils.create_base_url(softwareversion)

    # List of debrick urls
    osurls, coreurls, radiourls = textgenerator.url_generator(osversion, radioversion, softwareversion) #@IgnorePep8

    avlty = networkutils.availability(baseurl)
    textgenerator.write_links(softwareversion, osversion, radioversion,
                              osurls, coreurls, radiourls,
                              avlty, False, None)
