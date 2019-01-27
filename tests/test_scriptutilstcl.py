#!/usr/bin/env python3
"""Test the scriptutilstcl module."""

import os
from shutil import rmtree

import bbarchivist.scriptutilstcl as bs
import pytest
from requests import Session

try:
    import unittest.mock as mock
except ImportError:
    import mock

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2018-2019 Thurask"


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_scriptutilstcl"):
        os.mkdir("temp_scriptutilstcl")
    os.chdir("temp_scriptutilstcl")


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_scriptutilstcl", ignore_errors=True)


class TestClassScriptutilstcl:
    """
    Test Android autoloader-related utilities.
    """

    def test_tclloader_prep(self):
        """
        Test preparing names for Android autoloader generation.
        """
        loadername = "bbry_qc8953_sfi-user-production_signed-AAN358.zip"
        assert bs.tclloader_prep(loadername) == (loadername.replace(".zip", ""), "AAN358")
        assert bs.tclloader_prep(loadername.replace(".zip", ""), True) == (loadername.replace(".zip", ""), "AAN358")

    def test_tclloader_filename(self):
        """
        Test preparing filename for Android autoloader generation.
        """
        loaderdir = "bbry_qc8953_sfi-user-production_signed-AAN358"
        loadername = "bbry_qc8953_autoloader_user-all-AAN358"
        with mock.patch("os.listdir", mock.MagicMock(return_value=["bbry_qc8953"])):
            assert bs.tclloader_filename(loaderdir, "AAN358") == (loadername, "bbry_qc8953")

    def test_tcl_prd_scan(self, capsys):
        """
        Test scanning a PRD.
        """
        with mock.patch("bbarchivist.networkutilstcl.tcl_check", mock.MagicMock(return_value=6)):
            with mock.patch("bbarchivist.xmlutilstcl.parse_tcl_check", mock.MagicMock(return_value=(6, 6, 6, 6, 6))):
                with mock.patch("bbarchivist.networkutilstcl.vkhash", mock.MagicMock(return_value=6)):
                    with mock.patch("bbarchivist.networkutilstcl.tcl_download_request", mock.MagicMock(return_value=6)):
                        with mock.patch("bbarchivist.xmlutilstcl.parse_tcl_download_request", mock.MagicMock(return_value=("https://snek.snek/update.zip", None))):
                            with mock.patch("bbarchivist.networkutils.getcode", mock.MagicMock(return_value=200)):
                                bs.tcl_prd_scan("PRD-63116-001")
                                assert "snek.snek" in capsys.readouterr()[0]

    def test_tcl_prd_scan_fail(self):
        """
        Test scanning a PRD and failing.
        """
        with mock.patch("bbarchivist.networkutilstcl.tcl_check", mock.MagicMock(return_value=None)):
            with pytest.raises(SystemExit):
                bs.tcl_prd_scan("PRD-63116-001")

    def test_tcl_prd_scan_dlpass(self, capsys):
        """
        Test scanning a PRD, downloading a file, and passing.
        """
        with mock.patch("bbarchivist.networkutilstcl.tcl_check", mock.MagicMock(return_value=6)):
            with mock.patch("bbarchivist.xmlutilstcl.parse_tcl_check", mock.MagicMock(return_value=(6, 6, "snek.zip", 6, 6))):
                with mock.patch("bbarchivist.networkutilstcl.vkhash", mock.MagicMock(return_value=6)):
                    with mock.patch("bbarchivist.networkutilstcl.tcl_download_request", mock.MagicMock(return_value=6)):
                        with mock.patch("bbarchivist.xmlutilstcl.parse_tcl_download_request", mock.MagicMock(return_value=("https://snek.snek/update.zip", None))):
                            with mock.patch("bbarchivist.networkutils.getcode", mock.MagicMock(return_value=200)):
                                with mock.patch("bbarchivist.networkutils.download", mock.MagicMock(side_effect=None)):
                                    with mock.patch("os.rename", mock.MagicMock(side_effect=None)):
                                        with mock.patch("bbarchivist.hashutils.hashlib_hash", mock.MagicMock(return_value=6)):
                                            bs.tcl_prd_scan("PRD-63116-001", download=True)
                                            assert "HASH CHECK OK" in capsys.readouterr()[0]

    def test_tcl_prd_scan_dlfail(self, capsys):
        """
        Test scanning a PRD, downloading a file, and failing.
        """
        with mock.patch("bbarchivist.networkutilstcl.tcl_check", mock.MagicMock(return_value=6)):
            with mock.patch("bbarchivist.xmlutilstcl.parse_tcl_check", mock.MagicMock(return_value=(6, 6, "snek.zip", 6, 6))):
                with mock.patch("bbarchivist.networkutilstcl.vkhash", mock.MagicMock(return_value=6)):
                    with mock.patch("bbarchivist.networkutilstcl.tcl_download_request", mock.MagicMock(return_value=6)):
                        with mock.patch("bbarchivist.xmlutilstcl.parse_tcl_download_request", mock.MagicMock(return_value=("https://snek.snek/update.zip", None))):
                            with mock.patch("bbarchivist.networkutils.getcode", mock.MagicMock(return_value=200)):
                                with mock.patch("bbarchivist.networkutils.download", mock.MagicMock(side_effect=None)):
                                    with mock.patch("os.rename", mock.MagicMock(side_effect=None)):
                                        with mock.patch("bbarchivist.hashutils.hashlib_hash", mock.MagicMock(return_value=7)):
                                            bs.tcl_prd_scan("PRD-63116-001", download=True)
                                            assert "HASH FAILED" in capsys.readouterr()[0]

    def test_tcl_newprd(self, capsys):
        """
        Test scanning for new PRDs.
        """
        with mock.patch("bbarchivist.networkutilstcl.tcl_check", mock.MagicMock(return_value=6)):
            with mock.patch("bbarchivist.xmlutilstcl.parse_tcl_check", mock.MagicMock(return_value=(6, 6, "snek.zip", 6, 6))):
                prdbase = {"KEYone": ["PRD-63116-001", "PRD-63118-003"]}
                prddict = bs.tcl_findprd_prepdict(prdbase)
                prddict = bs.tcl_findprd_checkfilter(prddict, ["63119"])
                bs.tcl_findprd(prddict, floor=0, ceiling=111)
                assert "NOW SCANNING: " in capsys.readouterr()[0]

    def test_tcl_newprd_fail(self, capsys):
        """
        Test scanning for new PRDs, worst case.
        """
        with mock.patch("bbarchivist.networkutilstcl.tcl_check", mock.MagicMock(return_value=None)):
            prdbase = {"KEYone": ["PRD-63116-001", "PRD-63118-003"]}
            prddict = bs.tcl_findprd_prepdict(prdbase)
            prddict = bs.tcl_findprd_checkfilter(prddict, ["63119"])
            bs.tcl_findprd(prddict, floor=0, ceiling=111)
            assert "PRD-63119-001:" not in capsys.readouterr()[0]

    def test_tcl_otaprep_ota(self):
        """
        Test preparing values for OTA scanning, OTA scanning.
        """
        assert bs.tcl_prep_otaver("snek") == (2, "snek")

    def test_tcl_otaprep_full(self):
        """
        Test preparing values for OTA scanning, full scanning.
        """
        assert bs.tcl_prep_otaver(None) == (4, "AAA000")

    def test_tcl_otapreamble(self, capsys):
        """
        Test fancy output for OTA scanning.
        """
        bs.tcl_mainscan_preamble("snek")
        assert "OS SNEK" in capsys.readouterr()[0]

    def test_tcl_encheader(self, capsys):
        """
        Test checking for a file header.
        """
        with mock.patch("bbarchivist.networkutilstcl.encrypt_header", mock.MagicMock(return_value="\nHEADER FOUND")):
            bs.tcl_prd_print("televisionversion", "https://snek.snek/update.zip", "update.zip", 200, "127.0.0.1", Session())
            assert "HEADER FOUND" in capsys.readouterr()[0]

    def test_tcl_key2curef(self):
        """
        Test generating Athena CUREF.
        """
        assert bs.tcl_findprd_prepcuref("63824", 69, key2mode=True) == "APBI-PRD63824069"

    def test_tcl_deltaname(self):
        """
        Test generating delta-safe filenames.
        """
        assert bs.tcl_delta_filename("PRD-63116-123", "AAA000", "AAO472", "update.zip", False) == "JSU_PRD-63116-AAA000toAAO472.zip"

    def test_tcl_scanprint(self, capsys):
        """
        Test printing scan output, full scan.
        """
        bs.tcl_mainscan_printer("PRD-63999-999", "AAA000")
        assert "PRD-63999-999: AAA000" in capsys.readouterr()[0]

    def test_tcl_scanprint_ota(self, capsys):
        """
        Test printing scan output, OTA scan.
        """
        bs.tcl_mainscan_printer("PRD-63999-999", "ZZZ999", "AAA000")
        assert "PRD-63999-999: AAA000 to ZZZ999" in capsys.readouterr()[0]

    def test_tcl_remote_delta_good(self):
        """
        Test grabbing remote OTA, best case.
        """
        with mock.patch("bbarchivist.networkutilstcl.remote_prd_info", mock.MagicMock(return_value={"PRD-63999-999":"AAZ069"})):
            assert bs.tcl_delta_remote("PRD-63999-999") == "AAZ069"

    def test_tcl_remote_delta_bad(self):
        """
        Test grabbing remote OTA, best case.
        """
        with mock.patch("bbarchivist.networkutilstcl.remote_prd_info", mock.MagicMock(return_value={"PRD-63999-998":"AAZ069"})):
            with pytest.raises(SystemExit):
                bs.tcl_delta_remote("PRD-63999-999")
