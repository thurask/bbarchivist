#!/usr/bin/env python3

"""This module is used for generation of URLs and related text files."""

__author__ = "Thurask"
__license__ = "Do whatever"
__copyright__ = "2015 Thurask"

from bbarchivist.networkutils import create_base_url, get_content_length
from bbarchivist.utilities import filesize_parser, generate_urls


def write_links(softwareversion, osversion, radioversion,
                osurls, coreurls, radiourls, avlty=False,
                appendbars=False, appurls=None):
    """
    Write lookup links to file. Check for availability, can include app bars.

    :param softwareversion: Software release version.
    :type softwareversion: str

    :param osversion: OS version.
    :type osversion: str

    :param radioversion: Radio version.
    :type radioversion: str

    :param osurls: Pre-formed debrick OS URLs.
    :type osurls: dict{str:str}

    :param coreurls: Pre-formed core OS URLs.
    :type coreurls: dict{str:str}

    :param radiourls: Pre-formed radio URLs.
    :type radiourls: dict{str:str}

    :param avlty: Availability of links to download. Default is false.
    :type avlty: bool

    :param appendbars: Whether to add app bars to this file. Default is false.
    :type appendbars: bool

    :param appurls: App bar URLs to add.
    :type softwareversion: list
    """
    thename = softwareversion
    if appendbars:
        thename += "plusapps"
    with open(thename + ".txt", "w") as target:
        target.write("OS VERSION: " + osversion + "\n")
        target.write("RADIO VERSION: " + radioversion + "\n")
        target.write("SOFTWARE RELEASE: " + softwareversion + "\n")
        if not avlty:
            target.write("\n!!EXISTENCE NOT GUARANTEED!!\n")
        target.write("\nDEBRICK URLS:\n")
        for key, value in osurls.items():
            if avlty:
                thesize = get_content_length(value)
            else:
                thesize = None
            target.write(key + " [" + filesize_parser(thesize) + "] " + value + "\n")
        target.write("\nCORE URLS:\n")
        for key, value in coreurls.items():
            if avlty:
                thesize = get_content_length(value)
            else:
                thesize = None
            target.write(key + " [" + filesize_parser(thesize) + "] " + value + "\n")
        target.write("\nRADIO URLS:\n")
        for key, value in radiourls.items():
            if avlty:
                thesize = get_content_length(value)
            else:
                thesize = None
            target.write(key + " [" + filesize_parser(thesize) + "] " + value + "\n")
        if appendbars:
            target.write("\nAPP URLS:\n")
            for app in appurls:
                stoppers = ["8960", "8930", "8974", "m5730", "winchester"]
                if all(word not in app for word in stoppers):
                    thesize = get_content_length(app)
                    target.write(app + " [" + filesize_parser(thesize) + "]\n")


def url_generator(osversion, radioversion, softwareversion):
    """
    Return all debrick, core radio URLs from given OS, radio software.

    :param softwareversion: Software release version.
    :type softwareversion: str

    :param osversion: OS version.
    :type osversion: str

    :param radioversion: Radio version.
    :type radioversion: str
    """
    baseurl = create_base_url(softwareversion)
    radlist = ["STL100-1", "STL100-X/P9982", "STL100-4", "Q10/Q5/P9983", "Z30/LEAP/CLASSIC", "Z3", "PASSPORT"]
    oslist = ["STL100-1", "QC8960", "VERIZON QC8960", "Z3", "PASSPORT"]
    osurls, radiourls, coreurls = generate_urls(baseurl, osversion, radioversion, True)
    osurls.insert(2, baseurl + "/qc8960.verizon_sfi.desktop-" + osversion + "-nto+armle-v7+signed.bar")
    coreurls.insert(2, baseurl + "/qc8960.verizon_sfi-" + osversion + "-nto+armle-v7+signed.bar")
    ospairs = {}
    for title, url in zip(oslist, osurls):
        ospairs[title] = url
    corepairs = {}
    for title, url in zip(oslist, coreurls):
        corepairs[title] = url
    radiopairs = {}
    for title, url in zip(radlist, radiourls):
        radiopairs[title] = url
    return ospairs, corepairs, radiopairs
