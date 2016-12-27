#!/usr/bin/env python3
"""This module is used for generation of URLs and related text files."""

from bbarchivist.networkutils import get_length  # network
from bbarchivist.utilities import create_bar_url, fsizer, generate_urls, stripper  # utils

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def system_link_writer(target, urls, avlty=False):
    """
    Write OS/radio links to file.

    :param target: File to write to.
    :type target: file

    :param urls: Dictionary of URLs; name: URL
    :type urls: dict(str: str)

    :param avlty: If this OS release is available. Default is false.
    :type avlty: bool
    """
    for key, val in urls.items():
        if avlty:
            fsize = get_length(val)
        else:
            fsize = None
        target.write("{0} [{1}] {2}\n".format(key, fsizer(fsize), val))


def app_link_writer(target, urls):
    """
    Write app links to file.

    :param target: File to write to.
    :type target: file

    :param urls: Dictionary of URLs; name: URL
    :type urls: dict(str: str)
    """
    for app in urls:
        stoppers = ["8960", "8930", "8974", "m5730", "winchester"]
        if all(word not in app for word in stoppers):
            fsize = get_length(app)
            base = app.split('/')[-1]
            base = stripper(base)
            target.write("{0} [{1}] {2}\n".format(base, fsizer(fsize), app))


def dev_link_writer(target, finals):
    """
    Write Dev Alpha autooloader links to file.

    :param target: File to write to.
    :type target: file

    :param finals: Dict of URL:content-length pairs.
    :type finals: dict(str: str)
    """
    for key, val in finals.items():
        target.write("{0} [{1}]\n".format(key, fsizer(int(val))))


def prep_thename(softwareversion, appendbars=False, temp=False):
    """
    Generate name for output file.

    :param softwareversion: Software release version.
    :type softwareversion: str

    :param appendbars: Whether to add app bars to file. Default is false.
    :type appendbars: bool

    :param temp: If file we write to is temporary. Default is false.
    :type temp: bool
    """
    thename = softwareversion
    if appendbars:
        thename += "plusapps"
    if temp:
        thename = "TEMPFILE"
    return thename


def write_altsw(target, altsw):
    """
    Write alternate software release to file.

    :param target: File to write to.
    :type target: file

    :param altsw: Radio software release version, if different.
    :type altsw: str
    """
    if altsw is not None:
        target.write("RADIO SOFTWARE RELEASE: {0}\n".format(altsw))


def write_disclaimer(target, avlty):
    """
    Write availability disclaimer to file.

    :param target: File to write to.
    :type target: file

    :param avlty: Availability of links to download. Default is false.
    :type avlty: bool
    """
    if not avlty:
        target.write("\n!!EXISTENCE NOT GUARANTEED!!\n")


def write_appbars(target, appendbars, appurls):
    """
    Write app bar links to file.

    :param target: File to write to.
    :type target: file

    :param appendbars: Whether to add app bars to file. Default is false.
    :type appendbars: bool

    :param appurls: App bar URLs to add.
    :type softwareversion: list    
    """
    if appendbars:
        target.write("\nAPP URLS:\n")
        app_link_writer(target, appurls)


def write_signedbars(target, urllist, avlty, message):
    """
    Write debrick/core/radio URLs to file.

    :param target: File to write to.
    :type target: file

    :param urllist: List of URLs to write.
    :type urllist: list(str)

    :param avlty: Availability of links to download. Default is false.
    :type avlty: bool

    :param message: Header for this section: debrick, core or radio.
    :type message: str
    """
    target.write("\n{0}:\n".format(message))
    system_link_writer(target, urllist, avlty)


def write_header(target, softwareversion, osversion, radioversion):
    """
    Write header for file.

    :param target: File to write to.
    :type target: file

    :param softwareversion: Software release version.
    :type softwareversion: str

    :param osversion: OS version.
    :type osversion: str

    :param radioversion: Radio version.
    :type radioversion: str
    """
    target.write("OS VERSION: {0}\n".format(osversion))
    target.write("RADIO VERSION: {0}\n".format(radioversion))
    target.write("SOFTWARE RELEASE: {0}\n".format(softwareversion))


def write_links(softwareversion, osversion, radioversion, osurls, coreurls, radiourls,
                avlty=False, appendbars=False, appurls=None, temp=False, altsw=None):
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

    :param temp: If file we write to is temporary. Default is false.
    :type temp: bool

    :param altsw: Radio software release version, if different.
    :type altsw: str
    """
    thename = prep_thename(softwareversion, appendbars, temp)
    with open("{0}.txt".format(thename), "w") as target:
        write_header(target, softwareversion, osversion, radioversion)
        write_altsw(target, altsw)
        write_disclaimer(target, avlty)
        write_signedbars(target, osurls, avlty, "DEBRICK URLS")
        write_signedbars(target, coreurls, avlty, "CORE URLS")
        write_signedbars(target, radiourls, avlty, "RADIO URLS")
        write_appbars(target, appendbars, appurls)


def export_devloader(osversion, finals):
    """
    Export Dev Alpha URLs to file.

    :param osversion: OS version.
    :type osversion: str

    :param finals: Dict of URL:content-length pairs.
    :type finals: dict(str: str)
    """
    with open("DevAlpha-{0}.txt".format(osversion), "w") as target:
        dev_link_writer(target, finals)


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
    radlist = [
        "STL100-1",
        "STL100-X/P9982",
        "STL100-4",
        "Q10/Q5/P9983",
        "Z30/LEAP/CLASSIC",
        "Z3",
        "PASSPORT"
    ]
    oslist = [
        "STL100-1",
        "QC8960",
        "VERIZON QC8960",
        "Z3",
        "PASSPORT"
    ]
    oses, radios, cores = generate_urls(softwareversion, osversion, radioversion, True)
    vzw = create_bar_url(softwareversion, "qc8960.verizon_sfi.desktop", osversion)
    oses.insert(2, vzw)
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
