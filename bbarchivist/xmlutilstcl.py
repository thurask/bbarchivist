#!/usr/bin/env python3
"""This module is used for XML handling for TCL tools."""

import os  # filesystem read
import random  # choice

try:
    from defusedxml import ElementTree  # safer XML parsing
except (ImportError, AttributeError):
    from xml.etree import ElementTree  # XML parsing

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2018-2019 Thurask"


def parse_tcl_check(data):
    """
    Extract version and file info from TCL update server response.

    :param data: The data to parse.
    :type data: str
    """
    root = ElementTree.fromstring(data)
    tvver = root.find("VERSION").find("TV").text
    fwid = root.find("FIRMWARE").find("FW_ID").text
    fileinfo = root.find("FIRMWARE").find("FILESET").find("FILE")
    filename = fileinfo.find("FILENAME").text
    filesize = fileinfo.find("SIZE").text
    filehash = fileinfo.find("CHECKSUM").text
    return tvver, fwid, filename, filesize, filehash


def dump_tcl_xml(xmldata, salt):
    """
    Write XML responses to output directory.

    :param xmldata: Response XML.
    :type xmldata: str

    :param salt: Salt hash.
    :type salt: str
    """
    outfile = os.path.join(os.getcwd(), "logs", "{0}.xml".format(salt))
    if not os.path.exists(os.path.dirname(outfile)):
        os.makedirs(os.path.dirname(outfile))
    with open(outfile, "w", encoding="utf-8") as afile:
        afile.write(xmldata)


def parse_tcl_download_request(body, mode=4):
    """
    Extract file URL and encrypt slave URL from TCL update server response.

    :param data: The data to parse.
    :type data: str

    :param mode: 4 if downloading autoloaders, 2 if downloading OTA deltas.
    :type mode: int
    """
    root = ElementTree.fromstring(body)
    slavelist = root.find("SLAVE_LIST").findall("SLAVE")
    slave = random.choice(slavelist).text
    dlurl = root.find("FILE_LIST").find("FILE").find("DOWNLOAD_URL").text
    eslave = root.find("SLAVE_LIST").findall("ENCRYPT_SLAVE")
    encslave = None if mode == 2 or not eslave else random.choice(eslave).text
    return "http://{0}{1}".format(slave, dlurl), encslave
