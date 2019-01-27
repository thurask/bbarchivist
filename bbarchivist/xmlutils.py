#!/usr/bin/env python3
"""This module is used for XML handling."""

import re  # regexes

try:
    from defusedxml import ElementTree  # safer XML parsing
except (ImportError, AttributeError):
    from xml.etree import ElementTree  # XML parsing

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2018-2019 Thurask"


def cchecker_get_tags(roottext):
    """
    Get country and carrier from XML.

    :param roottext: XML text.
    :type roottext: str
    """
    root = ElementTree.fromstring(roottext)
    for child in root:
        if child.tag == "country":
            country = child.get("name")
        if child.tag == "carrier":
            carrier = child.get("name")
    return country, carrier


def prep_available_bundle(device, npc):
    """
    Prepare bundle query XML.

    :param device: Hexadecimal hardware ID.
    :type device: str

    :param npc: MCC + MNC (see `func:bbarchivist.networkutils.return_npc`)
    :type npc: int
    """
    query = '<?xml version="1.0" encoding="UTF-8"?><availableBundlesRequest version="1.0.0" authEchoTS="1366644680359"><deviceId><pin>0x2FFFFFB3</pin></deviceId><clientProperties><hardware><id>0x{0}</id><isBootROMSecure>true</isBootROMSecure></hardware><network><vendorId>0x0</vendorId><homeNPC>0x{1}</homeNPC><currentNPC>0x{1}</currentNPC></network><software><currentLocale>en_US</currentLocale><legalLocale>en_US</legalLocale><osVersion>10.0.0.0</osVersion><radioVersion>10.0.0.0</radioVersion></software></clientProperties><updateDirectives><bundleVersionFilter></bundleVersionFilter></updateDirectives></availableBundlesRequest>'.format(device, npc)
    return query


def parse_available_bundle(roottext):
    """
    Get bundles from XML.

    :param roottext: XML text.
    :type roottext: str
    """
    root = ElementTree.fromstring(roottext)
    package = root.find('./data/content')
    bundlelist = [child.attrib["version"] for child in package]
    return bundlelist


def carrier_swver_get(root):
    """
    Get software release from carrier XML.

    :param root: ElementTree we're barking up.
    :type root: xml.etree.ElementTree.ElementTree
    """
    for child in root.iter("softwareReleaseMetadata"):
        swver = child.get("softwareReleaseVersion")
    return swver


def carrier_child_fileappend(child, files, baseurl, blitz=False):
    """
    Append bar file links to a list from a child element.

    :param child: Child element in use.
    :type child: xml.etree.ElementTree.Element

    :param files: Filelist.
    :type files: list(str)

    :param baseurl: Base URL, URL minus the filename.
    :type baseurl: str

    :param blitz: Whether or not to create a blitz package. False by default.
    :type blitz: bool
    """
    if not blitz:
        files.append(baseurl + child.get("path"))
    else:
        if child.get("type") not in ["system:radio", "system:desktop", "system:os"]:
            files.append(baseurl + child.get("path"))
    return files


def carrier_child_finder(root, files, baseurl, blitz=False):
    """
    Extract filenames, radio and OS from child elements.

    :param root: ElementTree we're barking up.
    :type root: xml.etree.ElementTree.ElementTree

    :param files: Filelist.
    :type files: list(str)

    :param baseurl: Base URL, URL minus the filename.
    :type baseurl: str

    :param blitz: Whether or not to create a blitz package. False by default.
    :type blitz: bool
    """
    osver = radver = ""
    for child in root.iter("package"):
        files = carrier_child_fileappend(child, files, baseurl, blitz)
        if child.get("type") == "system:radio":
            radver = child.get("version")
        elif child.get("type") == "system:desktop":
            osver = child.get("version")
        elif child.get("type") == "system:os":
            osver = child.get("version")
    return osver, radver, files


def parse_carrier_xml(data, blitz=False):
    """
    Parse the response to a carrier update request and return the juicy bits.

    :param data: The data to parse.
    :type data: xml

    :param blitz: Whether or not to create a blitz package. False by default.
    :type blitz: bool
    """
    root = ElementTree.fromstring(data)
    sw_exists = root.find('./data/content/softwareReleaseMetadata')
    swver = "N/A" if sw_exists is None else ""
    if sw_exists is not None:
        swver = carrier_swver_get(root)
    files = []
    package_exists = root.find('./data/content/fileSets/fileSet')
    osver = radver = ""
    if package_exists is not None:
        baseurl = "{0}/".format(package_exists.get("url"))
        osver, radver, files = carrier_child_finder(root, files, baseurl, blitz)
    return swver, osver, radver, files


def prep_carrier_query(npc, device, upg, forced):
    """
    Prepare carrier query XML.

    :param npc: MCC + MNC (see `func:return_npc`)
    :type npc: int

    :param device: Hexadecimal hardware ID.
    :type device: str

    :param upg: "upgrade" or "repair".
    :type upg: str

    :param forced: Force a software release.
    :type forced: str
    """
    query = '<?xml version="1.0" encoding="UTF-8"?><updateDetailRequest version="2.2.1" authEchoTS="1366644680359"><clientProperties><hardware><pin>0x2FFFFFB3</pin><bsn>1128121361</bsn><imei>004401139269240</imei><id>0x{0}</id></hardware><network><homeNPC>0x{1}</homeNPC><iccid>89014104255505565333</iccid></network><software><currentLocale>en_US</currentLocale><legalLocale>en_US</legalLocale></software></clientProperties><updateDirectives><allowPatching type="REDBEND">true</allowPatching><upgradeMode>{2}</upgradeMode><provideDescriptions>false</provideDescriptions><provideFiles>true</provideFiles><queryType>NOTIFICATION_CHECK</queryType></updateDirectives><pollType>manual</pollType><resultPackageSetCriteria><softwareRelease softwareReleaseVersion="{3}" /><releaseIndependent><packageType operation="include">application</packageType></releaseIndependent></resultPackageSetCriteria></updateDetailRequest>'.format(device, npc, upg, forced)
    return query


def prep_sr_lookup(osver):
    """
    Prepare software lookup XML.

    :param osver: OS version to lookup, 10.x.y.zzzz.
    :type osver: str
    """
    query = '<?xml version="1.0" encoding="UTF-8"?><srVersionLookupRequest version="2.0.0" authEchoTS="1366644680359"><clientProperties><hardware><pin>0x2FFFFFB3</pin><bsn>1140011878</bsn><imei>004402242176786</imei><id>0x8D00240A</id><isBootROMSecure>true</isBootROMSecure></hardware><network><vendorId>0x0</vendorId><homeNPC>0x60</homeNPC><currentNPC>0x60</currentNPC><ecid>0x1</ecid></network><software><currentLocale>en_US</currentLocale><legalLocale>en_US</legalLocale><osVersion>{0}</osVersion><omadmEnabled>false</omadmEnabled></software></clientProperties></srVersionLookupRequest>'.format(osver)
    return query

def parse_sr_lookup(reqtext):
    """
    Take the text of a software lookup request response and parse it as XML.

    :param reqtext: Response text, hopefully XML formatted.
    :type reqtext: str
    """
    try:
        root = ElementTree.fromstring(reqtext)
    except ElementTree.ParseError:
        packtext = "SR not in system"
    else:
        packtext = sr_lookup_extractor(root)
    return packtext


def sr_lookup_extractor(root):
    """
    Take an ElementTree and extract a software release from it.

    :param root: ElementTree we're barking up.
    :type root: xml.etree.ElementTree.ElementTree
    """
    reg = re.compile(r"(\d{1,4}\.)(\d{1,4}\.)(\d{1,4}\.)(\d{1,4})")
    packages = root.findall('./data/content/')
    for package in packages:
        if package.text is not None:
            match = reg.match(package.text)
            packtext = package.text if match else "SR not in system"
            return packtext
