#!/usr/bin/env python3
"""This module is used for network connections for TCL tools."""

import base64  # encoding
import binascii  # encoding
import hashlib  # salt
import random  # salt
import time  # salt
import zlib  # encoding

import requests  # downloading
from bbarchivist import networkutils  # network tools
from bbarchivist import xmlutilstcl  # xml work
from bbarchivist.bbconstants import TCLMASTERS  # lookup servers

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2018 Thurask"


def tcl_master():
    """
    Get a random master server.
    """
    return random.choice(TCLMASTERS)


def tcl_default_id(devid):
    """
    Get an IMEI or a serial number or something.

    :param devid: Return default if this is None.
    :type devid: str
    """
    if devid is None:
        devid = "543212345000000"
    return devid


def check_prep(curef, mode=4, fvver="AAA000", cltp=2010, cktp=2, rtd=1, chnl=2, devid=None):
    """
    Prepare variables for TCL update check.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param mode: 4 if downloading autoloaders, 2 if downloading OTA deltas.
    :type mode: int

    :param fvver: Initial software version, must be specific if downloading OTA deltas.
    :type fvver: str

    :param cltp: 2010 to always show latest version, 10 to show actual updates. Default is 2010.
    :type cltp: int

    :param cktp: 2 if checking manually, 1 if checking automatically. Default is 2.
    :type cktp: int

    :param rtd: 2 if rooted, 1 if not. Default is 1.
    :type rtd: int

    :param chnl: 2 if checking on WiFi, 1 if checking on mobile. Default is 2.
    :type chnl: int

    :param devid: Serial number/IMEI. Default is fake, not that it matters.
    :type devid: str
    """
    devid = tcl_default_id(devid)
    geturl = "http://{0}/check.php".format(tcl_master())
    params = {"id": devid, "curef": curef, "fv": fvver, "mode": mode, "type": "Firmware", "cltp": cltp, "cktp": cktp, "rtd": rtd, "chnl": chnl}
    return geturl, params


@networkutils.pem_wrapper
@networkutils.try_try_again
def tcl_check(curef, session=None, mode=4, fvver="AAA000", export=False):
    """
    Check TCL server for updates.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()

    :param mode: 4 if downloading autoloaders, 2 if downloading OTA deltas.
    :type mode: int

    :param fvver: Initial software version, must be specific if downloading OTA deltas.
    :type fvver: str

    :param export: Whether to export XML response to file. Default is False.
    :type export: bool
    """
    sess = networkutils.generic_session(session)
    geturl, params = check_prep(curef, mode, fvver)
    req = sess.get(geturl, params=params)
    if req.status_code == 200:
        req.encoding = "utf-8"
        response = req.text
        if export:
            salt = tcl_salt()
            xmlutilstcl.dump_tcl_xml(response, salt)
    else:
        response = None
    return response


def tcl_salt():
    """
    Generate salt value for TCL server tools.
    """
    millis = round(time.time() * 1000)
    tail = "{0:06d}".format(random.randint(0, 999999))
    return "{0}{1}".format(str(millis), tail)


def unpack_vdkey():
    """
    Draw the curtain back.
    """
    vdkey = b"eJwdjwEOwDAIAr8kKFr//7HhmqXp8AIIDrYAgg8byiUXrwRJRXja+d6iNxu0AhUooDCN9rd6rDLxmGIakUVWo3IGCTRWqCAt6X4jGEIUAxgN0eYWnp+LkpHQAg/PsO90ELsy0Npm/n2HbtPndFgGEV31R9OmT4O4nrddjc3Qt6nWscx7e+WRHq5UnOudtjw5skuV09pFhvmqnOEIs4ljPeel1wfLYUF4\n"
    vdk = zlib.decompress(binascii.a2b_base64(vdkey))
    return vdk.decode("utf-8")


def vkhash(curef, tvver, fwid, salt, mode=4, fvver="AAA000", cltp=2010, devid=None):
    """
    Generate hash from TCL update server variables.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param tvver: Target software version.
    :type tvver: str

    :param fwid: Firmware ID for desired download file.
    :type fwid: str

    :param salt: Salt hash.
    :type salt: str

    :param mode: 4 if downloading autoloaders, 2 if downloading OTA deltas.
    :type mode: int

    :param fvver: Initial software version, must be specific if downloading OTA deltas.
    :type fvver: str

    :param cltp: 2010 to always show latest version, 10 to show actual updates. Default is 2010.
    :type cltp: int

    :param devid: Serial number/IMEI. Default is fake, not that it matters.
    :type devid: str
    """
    vdk = unpack_vdkey()
    devid = tcl_default_id(devid)
    query = "id={0}&salt={1}&curef={2}&fv={3}&tv={4}&type={5}&fw_id={6}&mode={7}&cltp={8}{9}".format(devid, salt, curef, fvver, tvver, "Firmware", fwid, mode, cltp, vdk)
    engine = hashlib.sha1()
    engine.update(bytes(query, "utf-8"))
    return engine.hexdigest()


def download_request_prep(curef, tvver, fwid, salt, vkh, mode=4, fvver="AAA000", cltp=2010, devid=None):
    """
    Prepare variables for download server check.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param tvver: Target software version.
    :type tvver: str

    :param fwid: Firmware ID for desired download file.
    :type fwid: str

    :param salt: Salt hash.
    :type salt: str

    :param vkh: VDKey-based hash.
    :type vkh: str

    :param mode: 4 if downloading autoloaders, 2 if downloading OTA deltas.
    :type mode: int

    :param fvver: Initial software version, must be specific if downloading OTA deltas.
    :type fvver: str

    :param cltp: 2010 to always show latest version, 10 to show actual updates. Default is 2010.
    :type cltp: int

    :param devid: Serial number/IMEI. Default is fake, not that it matters.
    :type devid: str
    """
    devid = tcl_default_id(devid)
    posturl = "http://{0}/download_request.php".format(tcl_master())
    params = {"id": devid, "curef": curef, "fv": fvver, "mode": mode, "type": "Firmware", "tv": tvver, "fw_id": fwid, "salt": salt, "vk": vkh, "cltp": cltp}
    if mode == 4:
        params["foot"] = 1
    return posturl, params


@networkutils.pem_wrapper
@networkutils.try_try_again
def tcl_download_request(curef, tvver, fwid, salt, vkh, session=None, mode=4, fvver="AAA000", export=False):
    """
    Check TCL server for download URLs.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param tvver: Target software version.
    :type tvver: str

    :param fwid: Firmware ID for desired download file.
    :type fwid: str

    :param salt: Salt hash.
    :type salt: str

    :param vkh: VDKey-based hash.
    :type vkh: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()

    :param mode: 4 if downloading autoloaders, 2 if downloading OTA deltas.
    :type mode: int

    :param fvver: Initial software version, must be specific if downloading OTA deltas.
    :type fvver: str

    :param export: Whether to export XML response to file. Default is False.
    :type export: bool
    """
    sess = networkutils.generic_session(session)
    posturl, params = download_request_prep(curef, tvver, fwid, salt, vkh, mode, fvver)
    req = sess.post(posturl, data=params)
    if req.status_code == 200:
        req.encoding = "utf-8"
        response = req.text
        if export:
            xmlutilstcl.dump_tcl_xml(response, salt)
    else:
        response = None
    return response


def encrypt_header_prep(address, encslave):
    """
    Prepare variables for encrypted header check.

    :param address: File URL minus host.
    :type address: str

    :param encslave: Server hosting header script.
    :type encslave: str
    """
    encs = {b"YWNjb3VudA==" : b"emhlbmdodWEuZ2Fv", b"cGFzc3dvcmQ=": b"cWFydUQ0b2s="}
    params = {base64.b64decode(key): base64.b64decode(val) for key, val in encs.items()}
    params[b"address"] = bytes(address, "utf-8")
    posturl = "http://{0}/encrypt_header.php".format(encslave)
    return posturl, params


@networkutils.pem_wrapper
def encrypt_header(address, encslave, session=None):
    """
    Check encrypted header.

    :param address: File URL minus host.
    :type address: str

    :param encslave: Server hosting header script.
    :type encslave: str

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    sess = networkutils.generic_session(session)
    posturl, params = encrypt_header_prep(address, encslave)
    req = sess.post(posturl, data=params)
    if req.status_code == 206:  # partial
        contentlength = int(req.headers["Content-Length"])
        sentinel = "HEADER FOUND" if contentlength == 4194320 else "NO HEADER FOUND"
    else:
        sentinel = None
    return sentinel


@networkutils.pem_wrapper
def remote_prd_info():
    """
    Get list of remote OTA versions.
    """
    dburl = "https://tclota.birth-online.de/json_lastupdates.php"
    req = requests.get(dburl)
    reqj = req.json()
    otadict = {val["curef"]: val["last_ota"] for val in reqj.values() if val["last_ota"] is not None}
    return otadict
