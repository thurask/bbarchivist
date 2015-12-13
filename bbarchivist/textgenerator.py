#!/usr/bin/env python3
"""This module is used for generation of URLs and related text files."""

from bbarchivist.networkutils import create_base_url, get_length  # network
from bbarchivist.utilities import fsizer, generate_urls, stripper  # utils

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015 Thurask"


def write_links(softwareversion, osversion, radioversion,
                osurls, coreurls, radiourls, avlty=False,
                appendbars=False, appurls=None, temp=False):
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

    :param appendbars: Whether to add app bars to file. Default is false.
    :type appendbars: bool

    :param appurls: App bar URLs to add.
    :type softwareversion: list

    :param temp: If file we write to is temporary.
    :type temp: bool
    """
    thename = softwareversion
    if appendbars:
        thename += "plusapps"
    if temp:
        thename = "TEMPFILE"
    with open(thename + ".txt", "w") as target:
        target.write("OS VERSION: " + osversion + "\n")
        target.write("RADIO VERSION: " + radioversion + "\n")
        target.write("SOFTWARE RELEASE: " + softwareversion + "\n")
        if not avlty:
            target.write("\n!!EXISTENCE NOT GUARANTEED!!\n")
        target.write("\nDEBRICK URLS:\n")
        for key, value in osurls.items():
            if avlty:
                thesize = get_length(value)
            else:
                thesize = None
            target.write("{0} [{1}] {2}\n".format(key,
                                                  fsizer(thesize),
                                                  value))
        target.write("\nCORE URLS:\n")
        for key, value in coreurls.items():
            if avlty:
                thesize = get_length(value)
            else:
                thesize = None
            target.write("{0} [{1}] {2}\n".format(key,
                                                  fsizer(thesize),
                                                  value))
        target.write("\nRADIO URLS:\n")
        for key, value in radiourls.items():
            if avlty:
                thesize = get_length(value)
            else:
                thesize = None
            target.write("{0} [{1}] {2}\n".format(key,
                                                  fsizer(thesize),
                                                  value))
        if appendbars:
            target.write("\nAPP URLS:\n")
            for app in appurls:
                stoppers = ["8960", "8930", "8974", "m5730", "winchester"]
                if all(word not in app for word in stoppers):
                    thesize = get_length(app)
                    base = app.split('/')[-1]
                    base = stripper(base)
                    target.write("{0} [{1}] {2}\n".format(base,
                                                          fsizer(thesize),
                                                          app))


def url_gen(osversion, radioversion, softwareversion):
    """
    Return all debrick, core and radio URLs from given OS, radio software.

    :param softwareversion: Software release version.
    :type softwareversion: str

    :param osversion: OS version.
    :type osversion: str

    :param radioversion: Radio version.
    :type radioversion: str
    """
    baseurl = create_base_url(softwareversion)
    radlist = ["STL100-1", "STL100-X/P9982", "STL100-4", "Q10/Q5/P9983",
               "Z30/LEAP/CLASSIC", "Z3", "PASSPORT"]
    oslist = ["STL100-1", "QC8960", "VERIZON QC8960", "Z3", "PASSPORT"]
    oses, radios, cores = generate_urls(baseurl, osversion, radioversion, True)
    vzw = "/{0}-{1}-{2}".format("qc8960.verizon_sfi.desktop",
                                osversion,
                                "nto+armle-v7+signed.bar")
    oses.insert(2,
                baseurl + vzw)
    cores.insert(2, oses[2].replace(".desktop", ""))
    ospairs = {}
    for title, url in zip(oslist, oses):
        ospairs[title] = url
    corepairs = {}
    for title, url in zip(oslist, cores):
        corepairs[title] = url
    radiopairs = {}
    for title, url in zip(radlist, radios):
        radiopairs[title] = url
    return ospairs, corepairs, radiopairs
