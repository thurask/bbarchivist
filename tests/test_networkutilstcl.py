#!/usr/bin/env python3
"""Test the networkutilstcl module."""

import os
from shutil import rmtree

import bbarchivist.networkutilstcl as bn
import bbarchivist.xmlutilstcl as bx
import httmock
import requests

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2018 Thurask"


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_networkutilstcl"):
        os.mkdir("temp_networkutilstcl")
    os.chdir("temp_networkutilstcl")


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_networkutilstcl", ignore_errors=True)


@httmock.all_requests
def tcl_check_mock(url, request):
    """
    Mock for TCL update checking.
    """
    badbody = b'<?xml version="1.0" encoding="utf-8"?>\n<GOTU><UPDATE_DESC>0</UPDATE_DESC><ENCODING_ERROR>0</ENCODING_ERROR><CUREF>PRD-63764-001</CUREF><VERSION><TYPE>4</TYPE><FV>AAA000</FV><TV>AAM693</TV><SVN>20170717_173202</SVN><RELEASE_INFO><year>2017</year><month>07</month><day>17</day><hour>17</hour><minute>29</minute><second>20</second><timezone>GMT 8</timezone><publisher>jin.zeng.hz</publisher></RELEASE_INFO></VERSION><FIRMWARE><FW_ID>258098</FW_ID><FILESET_COUNT>1</FILESET_COUNT><FILESET><FILE><FILENAME>bbry_qc8953_sfi-user-production_signed-AAM693.zip</FILENAME><FILE_ID>261497</FILE_ID><SIZE>2712821341</SIZE><CHECKSUM>97a9f933c70fbe7c106037aaba19c6aedd9136d2</CHECKSUM><FILE_VERSION>1</FILE_VERSION><INDEX>0</INDEX></FILE></FILESET></FIRMWARE><DESCRIPTION/></GOTU>\n'
    return {'status_code': 200, 'content': badbody}


@httmock.all_requests
def tcl_request_mock(url, request):
    """
    Mock for TCL download URL request.
    """
    badbody = b'<?xml version="1.0" encoding="utf-8"?>\n<GOTU><FILE_LIST><FILE><FILE_ID>261497</FILE_ID><DOWNLOAD_URL>/ce570ddc079e2744558f191895e524d02a60476f/cfcdde91ea7f810311d1f973726e390f77a9ff1b/258098/261497</DOWNLOAD_URL></FILE></FILE_LIST><SLAVE_LIST><SLAVE>g2slave-ap-north-01.tctmobile.com</SLAVE><SLAVE>g2slave-ap-north-01.tctmobile.com</SLAVE><SLAVE>g2slave-eu-west-01.tctmobile.com</SLAVE><SLAVE>g2slave-eu-west-01.tctmobile.com</SLAVE><SLAVE>g2slave-us-east-01.tctmobile.com</SLAVE><SLAVE>g2slave-us-east-01.tctmobile.com</SLAVE></SLAVE_LIST></GOTU>\n'
    return {'status_code': 200, 'content': badbody}


@httmock.all_requests
def tcl_enc_good_mock(url, request):
    """
    Mock for TCL header checking, best case.
    """
    return httmock.response(status_code=206, headers={'content-length': 4194320})


@httmock.all_requests
def tcl_enc_bad_mock(url, request):
    """
    Mock for TCL header checking, worst case.
    """
    return httmock.response(status_code=400, headers={'content-length': 123456})

@httmock.all_requests
def remote_prd_mock(url, request):
    """
    Mock for remote PRD info.
    """
    thebody = b'{"PRD-63999-999":{"curef":"PRD-63999-999","variant":"Snek","last_ota":"AAZ888","last_full":"AAZ999"}}'
    return {'status_code': 200, 'content': thebody}


@httmock.all_requests
def pa_bad_mock(url, request):
    """
    Mock for Android autoloader lookup, worst case.
    """
    thebody = "https://bbapps.download.blackberry.com/Priv/bbry_qc8992_autoloader_user-common-AAD250.zip"
    return {'status_code': 404, 'content': thebody}


@httmock.all_requests
def timeout_mock(url, request):
    """
    Mock for software release lookup, timeout.
    """
    raise requests.exceptions.Timeout


class TestClassNetworkutilstcl:
    """
    Test functions that are used for checking for Android updates.
    """

    def test_tcl_check(self):
        """
        Test checking for Android updates.
        """
        with httmock.HTTMock(tcl_check_mock):
            ctxt = bn.tcl_check("PRD-63764-001", export=True)
        tvver, fwver, fname, fsize, fhash = bx.parse_tcl_check(ctxt)
        assert tvver == "AAM693"
        assert fwver == "258098"
        assert fname == "bbry_qc8953_sfi-user-production_signed-AAM693.zip"
        assert fsize == "2712821341"
        assert fhash == "97a9f933c70fbe7c106037aaba19c6aedd9136d2"

    def test_tcl_check_fail(self):
        """
        Test checking for Android updates, worst case.
        """
        with httmock.HTTMock(pa_bad_mock):
            ctxt = bn.tcl_check("PRD-63764-001")
        assert ctxt is None

    def test_tcl_check_timeout(self):
        """
        Test checking for Android updates, timeout.
        """
        with httmock.HTTMock(timeout_mock):
            ctxt = bn.tcl_check("PRD-63764-001")
        assert ctxt is None

    def test_tcl_request(self):
        """
        Test checking for Android update URLs.
        """
        with httmock.HTTMock(tcl_request_mock):
            salt = bn.tcl_salt()
            vkh = bn.vkhash("PRD-63764-001", "AAM693", "258098", salt)
            utxt = bn.tcl_download_request("PRD-63764-001", "AAM693", "258098", salt, vkh, export=True)
        dlurl, encslave = bx.parse_tcl_download_request(utxt)
        del encslave
        assert "/ce570ddc079e2744558f191895e524d02a60476f/cfcdde91ea7f810311d1f973726e390f77a9ff1b/258098/261497" in dlurl

    def test_tcl_request_fail(self):
        """
        Test checking for Android update URLs, worst case.
        """
        with httmock.HTTMock(pa_bad_mock):
            salt = bn.tcl_salt()
            vkh = bn.vkhash("PRD-63764-001", "AAM693", "258098", salt)
            utxt = bn.tcl_download_request("PRD-63764-001", "AAM693", "258098", salt, vkh)
        assert utxt is None

    def test_tcl_encheader(self):
        """
        Test checking header, best case.
        """
        with httmock.HTTMock(tcl_enc_good_mock):
            sentinel = bn.encrypt_header("http://snek.com/snek/update.zip", "snek.com")
        assert sentinel == "HEADER FOUND"

    def test_tcl_encheader_fail(self):
        """
        Test checking header, worst case.
        """
        with httmock.HTTMock(tcl_enc_bad_mock):
            sentinel = bn.encrypt_header("http://snek.com/snek/update.zip", "snek.com")
        assert sentinel is None

    def test_remote_prd(self):
        """
        Test getting remote PRD info.
        """
        with httmock.HTTMock(remote_prd_mock):
            sentinel = bn.remote_prd_info()
        assert sentinel == {"PRD-63999-999": "AAZ888"}
