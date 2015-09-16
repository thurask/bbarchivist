#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, R0913, R0912, R0914, R0915
"""This module is used for generation of URLs and related text files."""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015 Thurask"


from bbarchivist.networkutils import create_base_url, get_content_length  # base url, get filesize
from bbarchivist.utilities import filesize_parser, generate_urls, barname_stripper  # url creation, filesize mapping, barname cleaning


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

    :param appendbars: Whether to add app bars to this file. Default is false.
    :type appendbars: bool

    :param appurls: App bar URLs to add.
    :type softwareversion: list

    :param temp: If file we write to is temporary.
    :type temp: bool
    """
    thename = softwareversion
    if appendbars:
        thename += "plusapps"
    if temp:  # pragma: no cover
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
                    base = app.split('/')[-1]
                    base = barname_stripper(base)
                    target.write(base + " [" + filesize_parser(thesize) + "] " + app + "\n")


def url_generator(osversion, radioversion, softwareversion):
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
    oses.insert(2,
                baseurl + "/qc8960.verizon_sfi.desktop-" + osversion + "-nto+armle-v7+signed.bar")
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
