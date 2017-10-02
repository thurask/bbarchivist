#!/usr/bin/env python3
"""Test the scriptutils module."""

import argparse
import os
import time
import sys
from shutil import rmtree, copyfile
import zipfile
try:
    import unittest.mock as mock
except ImportError:
    import mock
import pytest
from requests import Session
import bbarchivist.scriptutils as bs
from bbarchivist.bbconstants import LONGVERSION, COMMITDATE, VERSION

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2017 Thurask"


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_scriptutils"):
        os.mkdir("temp_scriptutils")
    os.chdir("temp_scriptutils")
    with open("Z10_loader1.exe", "w") as targetfile:
        targetfile.write("Jackdaws love my big sphinx of quartz")
    copyfile("Z10_loader1.exe", "Z10_loader2.exe")
    copyfile("Z10_loader1.exe", "Z10_loader3.exe")
    copyfile("Z10_loader1.exe", "Z10_loader2.7z")
    copyfile("Z10_loader1.exe", "Z10_loader2.zip")
    copyfile("Z10_loader1.exe", "Z10_loader3.zip")


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_scriptutils", ignore_errors=True)


class Dummy(object):
    """
    Dummy, with text and headers attributes.
    """

    def __init__(self):
        """
        Populate text and headers.
        """
        self.text = "snek"
        self.headers = {"content-length": 12345}


class TestClassScriptutils:
    """
    Test script-related tools.
    """

    def test_compjoiner(self):
        """
        Test getting absolute paths.
        """
        ofi = bs.comp_joiner(os.getcwd(), "snek", ["Z10_loader1.exe"])
        assert ofi[0] == os.path.join(os.getcwd(), "snek", "Z10_loader1.exe")

    def test_radio_version(self):
        """
        Test radio version non-incrementing.
        """
        assert bs.return_radio_version("10.3.2.2639", "10.3.2.5460") == "10.3.2.5460"

    def test_radio_version_inc(self):
        """
        Test radio version incrementing.
        """
        assert bs.return_radio_version("10.3.2.2639") == "10.3.2.2640"

    def test_clean_barlist(self):
        """
        Test excluding useless garbage from a list of apps.
        """
        craplist = ["retaildemo", "nuance", "pajeetmyson"]
        apps = ["os.bar", "radio.bar", "retaildemo.bar", "nuance_common.bar"]
        assert bs.clean_barlist(apps, craplist) == apps[:2]

    def test_blitz_links(self):
        """
        Test creating blitz links.
        """
        with mock.patch('bbarchivist.utilities.create_base_url', mock.MagicMock(return_value="abacab")):
            links = bs.generate_blitz_links([], "10.2.2.2222", "10.3.3.3333", "10.4.4.4444")
            assert len(links) == 10

    def test_cchecker_export_none(self, capsys):
        """
        Test exporting links, with no links to export.
        """
        bs.export_cchecker(None, None, None, None, None, None)
        assert "NO SOFTWARE RELEASE" in capsys.readouterr()[0]

    def test_cchecker_export_upgrade(self):
        """
        Test exporting links, with upgrade files.
        """
        with mock.patch('bbarchivist.textgenerator.get_fnone', mock.MagicMock(return_value=True)):
            bs.export_cchecker(
                ["http://sn.ek"],
                None,
                None,
                "10.1.1.1111",
                "10.2.2.2222",
                "10.3.3.3333",
                True,
                None)
            with open("10.3.3.3333plusapps.txt", "r") as afile:
                assert len(afile.read()) == 2899

    def test_cchecker_export_debrick(self):
        """
        Test exporting links, having to find upgrade files.
        """
        snek = Dummy()
        with mock.patch('requests.Session.head', mock.MagicMock(return_value=snek)):
            bs.export_cchecker(
                ["http://sn.ek"],
                "123456",
                "8500090A",
                "10.1.1.1111",
                "10.2.2.2222",
                "10.3.3.3334",
                False,
                None)
            with open("10.3.3.3334plusapps.txt", "r") as afile:
                assert len(afile.read()) == 2933

    def test_slim_preamble(self, capsys):
        """
        Test single line app header.
        """
        bs.slim_preamble("snek")
        assert "SNEK" in capsys.readouterr()[0]

    def test_standard_preamble(self, capsys):
        """
        Test multi-line app header.
        """
        bs.standard_preamble("snek", "10.3.2.2639", "10.3.2.2474", "10.3.2.2877", "10.3.2.2836")
        assert "2836" in capsys.readouterr()[0]

    def test_shortversion(self, monkeypatch):
        """
        Test version getting, short type.
        """
        monkeypatch.setattr("sys.frozen", True, raising=False)
        with open("version.txt", "w") as afile:
            afile.write("10.0.10586.1000")
        assert bs.shortversion() == "10.0.10586.1000"
        monkeypatch.setattr("sys.frozen", False, raising=False)

    def test_shortversion_unfrozen(self, monkeypatch):
        """
        Test version getting, short type, not frozen.
        """
        monkeypatch.setattr("sys.frozen", False, raising=False)
        assert bs.shortversion() == VERSION

    def test_longversion(self, monkeypatch):
        """
        Test version getting, long type.
        """
        monkeypatch.setattr("sys.frozen", True, raising=False)
        with open("longversion.txt", "w") as afile:
            afile.write("10.0.10586.1000\n1970-01-01")
        assert bs.longversion() == ["10.0.10586.1000", "1970-01-01"]
        monkeypatch.setattr("sys.frozen", False, raising=False)

    def test_longversion_unfrozen(self, monkeypatch):
        """
        Test version getting, long type, not frozen.
        """
        monkeypatch.setattr("sys.frozen", False, raising=False)
        assert bs.longversion() == (LONGVERSION, COMMITDATE)

    def test_linkgen(self):
        """
        Test link generation.
        """
        if os.path.exists("TEMPFILE.txt"):
            os.remove("TEMPFILE.txt")
        bs.linkgen("10.9.8.7654", "10.2.3.4567", "10.1.0.9283", "10.9.2.8374", True, False)
        time.sleep(2)  # wait for file creation
        with open("TEMPFILE.txt", "r") as afile:
            data = afile.read()
        assert len(data) == 2485
        if os.path.exists("TEMPFILE.txt"):
            os.remove("TEMPFILE.txt")

    def test_linkgen_sdk(self):
        """
        Test link generation, with SDK OSes.
        """
        if os.path.exists("TEMPFILE.txt"):
            os.remove("TEMPFILE.txt")
        bs.linkgen("10.9.8.7654", "10.2.3.4567", "10.1.0.9283", "10.9.2.8374", True, True)
        time.sleep(2)  # wait for file creation
        with open("TEMPFILE.txt", "r") as afile:
            data = afile.read()
        assert len(data) == 2421
        if os.path.exists("TEMPFILE.txt"):
            os.remove("TEMPFILE.txt")

    def test_questionnaire_device_good(self):
        """
        Test getting device from input, best case.
        """
        with mock.patch('builtins.input', mock.MagicMock(return_value="SNEK!")):
            assert bs.questionnaire_device() == "SNEK!"

    def test_questionnaire_device_bad(self, capsys):
        """
        Test getting device from input, worst case.
        """
        with mock.patch('builtins.input', mock.MagicMock(return_value="")):
            with pytest.raises(SystemExit):
                bs.questionnaire_device()
                assert "NO DEVICE SPECIFIED!" in capsys.readouterr()[0]

    def test_kernchecker_prep(self):
        """
        Test preparing output for kernel checker script.
        """
        kernlist = ['msm8992/AAL747', 'msm8992/AAL746', 'msm8996/AAJ051']
        assert bs.kernchecker_prep(kernlist) == {"msm8992": ["\tAAL747", "\tAAL746"], "msm8996": ["\tAAJ051"]}


class TestClassScriptutilsTCL:
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
        with mock.patch("bbarchivist.networkutils.tcl_check", mock.MagicMock(return_value=6)):
            with mock.patch("bbarchivist.networkutils.parse_tcl_check", mock.MagicMock(return_value=(6, 6, 6, 6, 6))):
                with mock.patch("bbarchivist.networkutils.vkhash", mock.MagicMock(return_value=6)):
                    with mock.patch("bbarchivist.networkutils.tcl_download_request", mock.MagicMock(return_value=6)):
                        with mock.patch("bbarchivist.networkutils.parse_tcl_download_request", mock.MagicMock(return_value=("https://snek.snek/update.zip", None))):
                            with mock.patch("bbarchivist.networkutils.getcode", mock.MagicMock(return_value=200)):
                                bs.tcl_prd_scan("PRD-63116-001")
                                assert "snek.snek" in capsys.readouterr()[0]

    def test_tcl_prd_scan_fail(self):
        """
        Test scanning a PRD and failing.
        """
        with mock.patch("bbarchivist.networkutils.tcl_check", mock.MagicMock(return_value=None)):
            with pytest.raises(SystemExit):
                bs.tcl_prd_scan("PRD-63116-001")

    def test_tcl_prd_scan_dlpass(self, capsys):
        """
        Test scanning a PRD, downloading a file, and passing.
        """
        with mock.patch("bbarchivist.networkutils.tcl_check", mock.MagicMock(return_value=6)):
            with mock.patch("bbarchivist.networkutils.parse_tcl_check", mock.MagicMock(return_value=(6, 6, "snek.zip", 6, 6))):
                with mock.patch("bbarchivist.networkutils.vkhash", mock.MagicMock(return_value=6)):
                    with mock.patch("bbarchivist.networkutils.tcl_download_request", mock.MagicMock(return_value=6)):
                        with mock.patch("bbarchivist.networkutils.parse_tcl_download_request", mock.MagicMock(return_value=("https://snek.snek/update.zip", None))):
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
        with mock.patch("bbarchivist.networkutils.tcl_check", mock.MagicMock(return_value=6)):
            with mock.patch("bbarchivist.networkutils.parse_tcl_check", mock.MagicMock(return_value=(6, 6, "snek.zip", 6, 6))):
                with mock.patch("bbarchivist.networkutils.vkhash", mock.MagicMock(return_value=6)):
                    with mock.patch("bbarchivist.networkutils.tcl_download_request", mock.MagicMock(return_value=6)):
                        with mock.patch("bbarchivist.networkutils.parse_tcl_download_request", mock.MagicMock(return_value=("https://snek.snek/update.zip", None))):
                            with mock.patch("bbarchivist.networkutils.getcode", mock.MagicMock(return_value=200)):
                                with mock.patch("bbarchivist.networkutils.download", mock.MagicMock(side_effect=None)):
                                    with mock.patch("os.rename", mock.MagicMock(side_effect=None)):
                                        with mock.patch("bbarchivist.hashutils.hashlib_hash", mock.MagicMock(return_value=7)):
                                            bs.tcl_prd_scan("PRD-63116-001", download=True)
                                            assert "HASH FAILED" in capsys.readouterr()[0]

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
        with mock.patch("bbarchivist.networkutils.encrypt_header", mock.MagicMock(return_value="\nHEADER FOUND")):
            bs.tcl_prd_print("https://snek.snek/update.zip", "update.zip", 200, "127.0.0.1", Session())
            assert "HEADER FOUND" in capsys.readouterr()[0]

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


class TestClassScriptutilsSoftware:
    """
    Test software release-related utilities.
    """

    def test_return_swc_auto(self):
        """
        Test software release non-checking,
        """
        assert bs.return_sw_checked("10.3.2.2474", "10.3.2.2639") == ("10.3.2.2474", True)

    def test_return_swc_manual(self):
        """
        Test software release checking.
        """
        with mock.patch('bbarchivist.networkutils.sr_lookup', mock.MagicMock(return_value="10.3.2.2474")):
            assert bs.return_sw_checked(None, "10.3.2.2639") == ("10.3.2.2474", True)

    def test_return_swc_explicit(self):
        """
        Test software release checking, failure and definition.
        """
        with mock.patch('bbarchivist.networkutils.sr_lookup', mock.MagicMock(return_value="SR not in system")):
            with mock.patch('builtins.input', mock.MagicMock(return_value="10.3.2.9999")):
                with mock.patch('bbarchivist.utilities.s2b', mock.MagicMock(return_value=True)):
                    assert bs.return_sw_checked(None, "10.3.2.2639") == ("10.3.2.9999", False)

    def test_return_swc_exit(self):
        """
        Test exiting upon software release check failure.
        """
        with mock.patch('bbarchivist.networkutils.sr_lookup', mock.MagicMock(return_value="SR not in system")):
            with mock.patch('builtins.input', mock.MagicMock(return_value="n")):
                with pytest.raises(SystemExit):
                    bs.return_sw_checked(None, "10.3.2.2639")

    def test_return_rswc_auto(self):
        """
        Test radio software release non-checking.
        """
        assert bs.return_radio_sw_checked("10.3.2.2474", "10.3.2.2640") == ("10.3.2.2474", True)

    def test_return_rswc_manual(self):
        """
        Test radio software release checking.
        """
        with mock.patch('bbarchivist.networkutils.sr_lookup',
                        mock.MagicMock(return_value="10.3.2.2474")):
            assert bs.return_radio_sw_checked("checkme", "10.3.2.2640") == ("10.3.2.2474", True)

    def test_return_rswc_explicit(self):
        """
        Test radio software release checking, failure and definition.
        """
        with mock.patch('bbarchivist.networkutils.sr_lookup', mock.MagicMock(return_value="SR not in system")):
            with mock.patch('builtins.input', mock.MagicMock(return_value="10.3.2.2474")):
                with mock.patch('bbarchivist.utilities.s2b', mock.MagicMock(return_value=True)):
                    assert bs.return_radio_sw_checked(
                        "checkme", "10.3.2.2640") == (
                            "10.3.2.2474", False)

    def test_return_rswc_exit(self):
        """
        Test exiting upon radio software release check failure.
        """
        with mock.patch('bbarchivist.networkutils.sr_lookup', mock.MagicMock(return_value="SR not in system")):
            with mock.patch('builtins.input', mock.MagicMock(return_value="n")):
                with pytest.raises(SystemExit):
                    bs.return_radio_sw_checked("checkme", "10.3.2.2639")

    def test_check_sw_auto(self, capsys):
        """
        Test automatic software availability checking.
        """
        bs.check_sw("http://qrrbrbirlbel.yu/", "10.3.2.2474", True)
        assert "EXISTS" in capsys.readouterr()[0]

    def test_check_sw_manual(self, capsys):
        """
        Test manual software availability checking.
        """
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=True)):
            bs.check_sw("http://qrrbrbirlbel.yu/", "10.3.2.2474", False)
            assert "EXISTS" in capsys.readouterr()[0]

    def test_check_sw_exit(self):
        """
        Test exiting upon software release availability failure.
        """
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="n")):
                with pytest.raises(SystemExit):
                    bs.check_sw("http://qrrbrbirlbel.yu/", "10.3.2.2474", False)

    def test_check_sw_go(self):
        """
        Test continuing upon software release availability failure.
        """
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="y")):
                assert bs.check_sw("http://qrrbrbirlbel.yu/", "10.3.2.2474", False) is None

    def test_check_rsw_auto(self, capsys):
        """
        Test automatic radio software availability checking.
        """
        bs.check_radio_sw("http://qrrbrbirlbel.yu/", "10.3.2.2474", True)
        assert "EXISTS" in capsys.readouterr()[0]

    def test_check_rsw_manual(self, capsys):
        """
        Test manual radio software availability checking.
        """
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=True)):
            bs.check_radio_sw("http://qrrbrbirlbel.yu/", "10.3.2.2474", False)
            assert "EXISTS" in capsys.readouterr()[0]

    def test_check_rsw_exit(self):
        """
        Test exiting upon radio software release availability failure.
        """
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="n")):
                with pytest.raises(SystemExit):
                    bs.check_radio_sw("http://qrrbrbirlbel.yu/", "10.3.2.2474", False)

    def test_check_rsw_go(self):
        """
        Test continuing upon radio software release availability failure.
        """
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="y")):
                assert bs.check_radio_sw("http://qrrbrbirlbel.yu/", "10.3.2.2474", False) is None

    def test_check_altsw_none(self):
        """
        Test checking alternate software release, no need to.
        """
        assert bs.check_altsw(False) is None

    def test_check_altsw_manual(self):
        """
        Test checking alternate software release, with user input.
        """
        with mock.patch('builtins.input', mock.MagicMock(return_value="snek")):
            assert bs.check_altsw(True) == "snek"

    def test_check_altsw_checkme(self):
        """
        Test checking alternate software release, check it later.
        """
        with mock.patch('builtins.input', mock.MagicMock(return_value="")):
            assert bs.check_altsw(True) == "checkme"

    def test_prod_avail_invalid(self):
        """
        Test production lookup, no software release.
        """
        assert bs.prod_avail({"p": "SR not in system"}) == ("SR not in system", "  ", "Unavailable")

    def test_prod_avail_unavail(self):
        """
        Test production lookup, no software release.
        """
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=False)):
            assert bs.prod_avail({"p": "10.3.3.1465"}) == ("10.3.3.1465", "PD", "Unavailable")

    def test_prod_avail_avail(self):
        """
        Test production lookup, no software release.
        """
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=True)):
            with mock.patch('bbarchivist.sqlutils.prepare_sw_db', mock.MagicMock(side_effect=None)):
                with mock.patch('bbarchivist.sqlutils.check_exists', mock.MagicMock(return_value=False)):
                    with mock.patch('bbarchivist.scriptutils.linkgen', mock.MagicMock(side_effect=None)):
                        with mock.patch('bbarchivist.smtputils.prep_email', mock.MagicMock(side_effect=None)):
                            assert bs.prod_avail({"p": "10.3.3.1465"}, mailer=True, osversion="10.3.3.2163") == ("10.3.3.1465", "PD", "Available")


class TestClassScriptutilsIO:
    """
    Test print/folder-related utilities.
    """

    def test_autolookup_printer(self, capsys):
        """
        Test writing autolookup output to stdout.
        """
        bs.autolookup_printer("SNEK", "Available", False, False)
        assert "SNEK" in capsys.readouterr()[0]

    def test_autolookup_printer_log(self):
        """
        Test writing autolookup output to file.
        """
        bs.autolookup_printer("SNEK", "Available", True, True, "snek.txt")
        time.sleep(2)  # wait for file creation
        with open("snek.txt", "r") as afile:
            data = afile.read()
        assert data == "SNEK\n"

    def test_autolookup_logger(self):
        """
        Test writing autolookup output to file, unthreaded.
        """
        if os.path.exists("austinsnexas.txt"):
            os.remove("austinsnexas.txt")
        bs.autolookup_logger("austinsnexas.txt", "SNEK")
        with open("austinsnexas.txt", "r") as afile:
            data = afile.read()
        assert data == "SNEK\n"

    def test_autolookup_out(self):
        """
        Test autolookup output.
        """
        avpack = ("A1", "  ", "  ", "B2", "PD")
        block = bs.autolookup_output("10.3.2.2639", "10.3.2.2474", "Available", avpack)
        assert "OS 10.3.2.2639 -" in block

    def test_autolookup_output_sql(self):
        """
        Test autolookup output SQL handling.
        """
        with mock.patch('bbarchivist.sqlutils.prepare_sw_db', mock.MagicMock(side_effect=None)):
            with mock.patch('bbarchivist.sqlutils.check_exists', mock.MagicMock(return_value=False)):
                with mock.patch('bbarchivist.sqlutils.insert', mock.MagicMock(side_effect=None)):
                    bs.autolookup_output_sql("10.3.2.2639", "10.3.2.2474", "Available", True)

    def test_generate_workfolder_local(self):
        """
        Test getting workfolder if we default to local.
        """
        assert bs.generate_workfolder(None) == os.getcwd()

    def test_generate_workfolder_create(self):
        """
        Test getting workfolder if we have to make it.
        """
        if "snektacular" in os.listdir():
            os.remove("snektacular")
        bs.generate_workfolder("snektacular")
        assert "snektacular" in os.listdir()


class TestClassScriptutilsURLCheck:
    """
    Test URL-related utilities.
    """

    def test_os_single(self, capsys):
        """
        Test single OS availability.
        """
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=True)):
            bs.check_os_single("http://qrrbrbirlbel.yu/", "10.3.2.2639", 0)
            assert "NOT AVAILABLE" not in capsys.readouterr()[0]

    def test_os_single_fail(self):
        """
        Test single OS availability failure.
        """
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="n")):
                with pytest.raises(SystemExit):
                    bs.check_os_single("http://qrrbrbirlbel.yu/", "10.3.2.2639", 0)

    def test_os_single_go(self):
        """
        Test single OS availability continuation.
        """
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="y")):
                assert bs.check_os_single("http://qrrbrbirlbel.yu/", "10.3.2.2639", 0) is None

    def test_os_bulk(self, capsys):
        """
        Test bulk OS availability.
        """
        osurls = ["http://qrrbrbirlbel.yu/", "http://zeekyboogydoog.su/"]
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=True)):
            bs.check_os_bulk(osurls)
            assert "NOT FOUND" not in capsys.readouterr()[0]

    def test_os_bulk_fail(self):
        """
        Test bulk OS availability failure.
        """
        osurls = ["http://qrrbrbirlbel.yu/", "http://zeekyboogydoog.su/"]
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="n")):
                with pytest.raises(SystemExit):
                    bs.check_os_bulk(osurls)

    def test_os_bulk_go(self):
        """
        Test bulk OS availability continuation.
        """
        osurls = ["http://qrrbrbirlbel.yu/", "http://zeekyboogydoog.su/"]
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="y")):
                assert bs.check_os_bulk(osurls) is None

    def test_radio_single(self, capsys):
        """
        Test single radio availability.
        """
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=True)):
            assert bs.check_radio_single(
                "http://qrrbrbirlbel.yu/",
                "10.3.2.2640") == (
                    "http://qrrbrbirlbel.yu/",
                    "10.3.2.2640")
            assert "NOT AVAILABLE" not in capsys.readouterr()[0]

    def test_radio_single_fail(self):
        """
        Test single radio availability failure.
        """
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="n")):
                with pytest.raises(SystemExit):
                    bs.check_radio_single("http://qrrbrbirlbel.yu/", "10.3.2.2639")

    def test_radio_single_replace(self):
        """
        Test single radio availability replacement.
        """
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="y")):
                assert bs.check_radio_single(
                    "http://qrrbrbirlbel.yu/",
                    "10.3.2.2639") == (
                        "http://qrrbrbirlbel.yu/",
                        "y")

    def test_radio_bulk(self, capsys):
        """
        Test bulk radio availability.
        """
        radiourls = ["http://qrrbrbirlbel.yu/", "http://zeekyboogydoog.su/"]
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=True)):
            assert bs.check_radio_bulk(radiourls, "10.3.2.2640") == (radiourls, "10.3.2.2640")
            assert "NOT FOUND" not in capsys.readouterr()[0]

    def test_radio_bulk_fail(self):
        """
        Test bulk radio availability failure.
        """
        radiourls = ["http://qrrbrbirlbel.yu/", "http://zeekyboogydoog.su/"]
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="n")):
                with pytest.raises(SystemExit):
                    bs.check_radio_bulk(radiourls, "10.3.2.2639")

    def test_radio_bulk_replace(self):
        """
        Test bulk radio availability replacement.
        """
        radiourls = ["http://qrrbrbirlbel.yu/", "http://zeekyboogydoog.su/"]
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="y")):
                assert bs.check_radio_bulk(radiourls, "10.3.2.2639") == (radiourls, "y")

    def test_clean_swrel(self):
        """
        Test picking a software release out of a set of software releases.
        """
        swrels = set(["SR not in system", None, "10.3.2.2836", None])
        assert bs.clean_swrel(swrels) == "10.3.2.2836"

    def test_clean_swrel_none(self):
        """
        Test dealing with no software release in a set of lookup results.
        """
        swrels = set(["SR not in system", None, "SR not in system", None])
        assert not bs.clean_swrel(swrels)

    def test_baseurls(self):
        """
        Test generating base URLs for bar links, no alternate radio URLs.
        """
        baseurl, alturl = bs.get_baseurls("10.3.2.2836")
        assert "7bca9151809337becef897a0bcf3f199dfc74373" in baseurl
        assert alturl is None

    def test_baseurls_alt(self):
        """
        Test generating base URLs for bar links, with alternate radio URLs.
        """
        baseurl, alturl = bs.get_baseurls("10.3.2.2836", "10.3.2.2474")
        assert "7bca9151809337becef897a0bcf3f199dfc74373" in baseurl
        assert "af31a981d0a53f304d0cfe3f68d35dc3c0b5964f" in alturl


class TestClassScriptutilsSevenzip:
    """
    Test 7-Zip related utilities.
    """

    def test_szexe_irrelevant(self):
        """
        Test 7z exe finding, without actually looking.
        """
        assert bs.get_sz_executable("tbz") == ("tbz", "")

    def test_szexe_present(self):
        """
        Test 7z exe finding, when it exists.
        """
        with mock.patch('bbarchivist.utilities.prep_seven_zip', mock.MagicMock(return_value=True)):
            with mock.patch('bbarchivist.utilities.get_seven_zip', mock.MagicMock(return_value="jackdaw")):
                assert bs.get_sz_executable("7z") == ("7z", "jackdaw")

    def test_szexe_exit(self):
        """
        Test exiting upon not finding 7z exe.
        """
        with mock.patch('bbarchivist.utilities.prep_seven_zip', mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="n")):
                with pytest.raises(SystemExit):
                    bs.get_sz_executable("7z")

    def test_szexe_fallback(self):
        """
        Test falling back to zip upon not finding 7z exe.
        """
        with mock.patch('bbarchivist.utilities.prep_seven_zip', mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="y")):
                assert bs.get_sz_executable("7z") == ("zip", "")


class TestClassScriptutilsArguments:
    """
    Test argparse parser generation.
    """
    @classmethod
    def setup_class(cls):
        """
        Create parser for testing.
        """
        cls.parser = bs.default_parser("name", "Formats C:", flags=("folder", "osr"), vers=["deadbeef", "1970-01-01"])

    def test_parser_name(self):
        """
        Test if parser has the name set.
        """
        assert self.parser.prog == "name"

    def test_parser_desc(self):
        """
        Test if parser has the desc set.
        """
        assert self.parser.description == "Formats C:"

    def test_parser_epilog(self):
        """
        Test if parser has the epilog set.
        """
        assert self.parser.epilog == "https://github.com/thurask/bbarchivist"

    def test_parser_version(self):
        """
        Test if parser has the version set.
        """
        verarg = [x for x in self.parser._actions if isinstance(x, argparse._VersionAction)][0]
        assert verarg.version == "name deadbeef committed 1970-01-01"

    def test_parser_args(self):
        """
        Test arg parsing.
        """
        pargs = self.parser.parse_args(["10.3.2.2876"])
        args = vars(pargs)
        assert args["folder"] is None
        assert args["radio"] is None
        assert args["swrelease"] is None
        assert args["os"] == "10.3.2.2876"

    def test_external_version(self):
        """
        Test version modification.
        """
        newpar = bs.external_version(self.parser, "|SNEKSNEK")
        verarg = [x for x in newpar._actions if isinstance(x, argparse._VersionAction)][0]
        assert verarg.version == "name deadbeef committed 1970-01-01|SNEKSNEK"

    def test_arg_verify_none(self, capsys):
        """
        Test if argument is None.
        """
        with pytest.raises(argparse.ArgumentError):
            bs.arg_verify_none(None, "SNEK!")


class TestClassScriptutilsShim:
    """
    Test CFP/CAP shim.
    """
    def setup_method(self, method):
        """
        Mock sys.argv.
        """
        self.oldsysargv = sys.argv
        sys.argv = ["cap.exe", "help"]

    def teardown_method(self, method):
        """
        Unmock sys.argv.
        """
        sys.argv = self.oldsysargv

    def test_windows_shim_posix(self, capsys):
        """
        Test CFP/CAP shim on non-Windows.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Wandows")):
            bs.generic_windows_shim("cap", "CAP!", "cap.exe", "3.10")
            assert "Sorry, Windows only." in capsys.readouterr()[0]

    def test_windows_shim_windows(self, capsys):
        """
        Test CFP/CAP shim on Windows.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Windows")):
            with mock.patch('subprocess.call', mock.MagicMock(side_effect=print("Snek!"))):
                bs.generic_windows_shim("cap", "CAP!", "cap.exe", "3.10")
                assert "Snek!" in capsys.readouterr()[0]


class TestClassScriptutilsIntegrity:
    """
    Test checking file integrity.
    """
    @classmethod
    def setup_class(cls):
        """
        Create files for testing.
        """
        cls.mstring = b"Somestuff\nName: target.signed\nDigest: tmpeiqm5cFdIwu5YWw4aOkEojS2vw74tsS-onS8qPhT53sEd5LqGW7Ueqmws_rKUE5RV402n2CehlQSwkGwBwQ\nmorestuff"
        cls.estring = cls.mstring + b"HAHAHAFOOLEDYOU"
        cls.fstring = b"Jackdaws love my big sphinx of quartz"
        with zipfile.ZipFile("mfest.bar", mode="w", compression=zipfile.ZIP_DEFLATED) as zfile:
            zfile.writestr("MANIFEST.MF", cls.mstring)
            zfile.writestr("target.signed", cls.fstring)
        with zipfile.ZipFile("bkmfest.bar", mode="w", compression=zipfile.ZIP_DEFLATED) as zfile:
            zfile.writestr("MANIFEST.MF", cls.mstring)
            zfile.writestr("target.signed", cls.estring)
        copyfile("bkmfest.bar", "bkmfest.bra")
        with open("target.signed", "wb") as targetfile:
            targetfile.write(cls.fstring)

    def test_bar_files_good(self, capsys):
        """
        Test checking bar file manifest, best case.
        """
        if os.path.exists("bkmfest.bar"):
            os.rename("bkmfest.bar", "bkmfest.bak")
        bs.test_bar_files(os.getcwd(), ["http://mfest.bar"])
        assert "OK" in capsys.readouterr()[0]
        if os.path.exists("bkmfest.bak"):
            os.rename("bkmfest.bak", "bkmfest.bar")

    def test_bar_files_bad(self, capsys):
        """
        Test checking bar file manifest, worst case, no download.
        """
        if os.path.exists("mfest.bar"):
            os.rename("mfest.bar", "mfest.bak")
        with mock.patch("bbarchivist.barutils.bar_tester", mock.MagicMock(return_value="bkmfest.bar")):
            with pytest.raises(SystemExit):
                bs.test_bar_files(os.getcwd(), ["http://bkmfest.bar"])
        assert "BROKEN" in capsys.readouterr()[0]
        if os.path.exists("mfest.bak"):
            os.rename("mfest.bak", "mfest.bar")

    def test_signed_files_good(self):
        """
        Test checking signed files against manifest, best case.
        """
        if os.path.exists("bkmfest.bar"):
            os.rename("bkmfest.bar", "bkmfest.bak")
        bs.test_signed_files(os.getcwd())
        if os.path.exists("bkmfest.bak"):
            os.rename("bkmfest.bak", "bkmfest.bar")

    def test_signed_files_bad(self, capsys):
        """
        Test checking signed files against manifest, worst case.
        """
        if os.path.exists("mfest.bar"):
            os.rename("mfest.bar", "mfest.bak")
        os.rename("bkmfest.bra", "bkmfest.bar")
        with mock.patch("bbarchivist.barutils.verify_sha512", mock.MagicMock(return_value=False)):
            bs.test_signed_files(os.getcwd())
            assert "IS BROKEN" in capsys.readouterr()[0]
        if os.path.exists("mfest.bak"):
            os.rename("mfest.bak", "mfest.bar")

    def test_loader_single_good(self, capsys):
        """
        Test checking one loader, best case.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Windows")):
            with mock.patch('bbarchivist.utilities.verify_loader_integrity', mock.MagicMock(return_value=True)):
                bs.test_single_loader("Z10_loader1.exe")
                assert "OK" in capsys.readouterr()[0]

    def test_loader_single_bad(self):
        """
        Test checking one loader, worst case.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Windows")):
            with mock.patch('bbarchivist.utilities.verify_loader_integrity', mock.MagicMock(return_value=False)):
                try:
                    bs.test_single_loader("Z10_loader1.exe")
                except SystemExit:
                    assert True
                else:
                    assert False

    def test_loader_single_nonwin(self):
        """
        Test checking one loader, non-Windows.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Wandows")):
            assert bs.test_single_loader("Z10_loader1.exe") is None

    def test_loader_bulk_good(self, capsys):
        """
        Test checking many loaders, best case.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Windows")):
            with mock.patch('bbarchivist.utilities.verify_loader_integrity', mock.MagicMock(return_value=True)):
                bs.test_loader_files(os.getcwd())
                assert "OK" in capsys.readouterr()[0]

    def test_loader_bulk_bad(self):
        """
        Test checking many loaders, worst case.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Windows")):
            with mock.patch('bbarchivist.utilities.verify_loader_integrity', mock.MagicMock(return_value=False)):
                try:
                    bs.test_loader_files(os.getcwd())
                except SystemExit:
                    assert True
                else:
                    assert False

    def test_loader_bulk_nonwin(self):
        """
        Test checking many loaders, non-Windows.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Wandows")):
            assert bs.test_loader_files(os.getcwd()) is None

    def test_bulk_avail(self):
        """
        Test bulk loader URL availability.
        """
        with mock.patch('bbarchivist.networkutils.availability', mock.MagicMock(return_value=False)):
            assert bs.bulk_avail(["fake.url", "fakeurl.2"]) == []

    def test_package_blitz_good(self):
        """
        Test packaging blitz, best case.
        """
        os.mkdir("blitzdir")
        with mock.patch('bbarchivist.barutils.create_blitz', mock.MagicMock(side_effect=None)):
            with mock.patch('bbarchivist.archiveutils.zip_verify', mock.MagicMock(return_value=True)):
                bs.package_blitz("blitzdir", "BlitzSW")
                assert "blitzdir" not in os.listdir()

    def test_package_blitz_bad(self, capsys):
        """
        Test packaging Blitz, worst case.
        """
        os.mkdir("blitzdir")
        with mock.patch('bbarchivist.barutils.create_blitz', mock.MagicMock(side_effect=None)):
            with mock.patch('bbarchivist.archiveutils.zip_verify', mock.MagicMock(return_value=False)):
                with pytest.raises(SystemExit):
                    bs.package_blitz("blitzdir", "BlitzSW")
                    assert "BLITZ FILE IS BROKEN" in capsys.readouterr()[0]


class TestClassScriptutilsHash:
    """
    Test hash/GPG-related utilities.
    """

    def test_gpgver_unchanged(self):
        """
        Test no modifications to GPG credentials.
        """
        with mock.patch('bbarchivist.gpgutils.gpg_config_loader', mock.MagicMock(return_value=("12345678", "hunter2"))):
            assert bs.verify_gpg_credentials() == ("12345678", "hunter2")

    def test_gpgver_key(self):
        """
        Test lack of GPG key.
        """
        with mock.patch('bbarchivist.gpgutils.gpg_config_loader', mock.MagicMock(return_value=(None, "hunter2"))):
            with mock.patch('builtins.input', mock.MagicMock(return_value="y")):
                with mock.patch('bbarchivist.gpgutils.gpg_config_writer', mock.MagicMock(return_value=None)):
                    assert bs.verify_gpg_credentials() == ("0xy", "hunter2")

    def test_gpgver_pass(self):
        """
        Test lack of GPG pass.
        """
        with mock.patch('bbarchivist.gpgutils.gpg_config_loader', mock.MagicMock(return_value=("12345678", None))):
            with mock.patch('builtins.input', mock.MagicMock(return_value="y")):
                with mock.patch('bbarchivist.gpgutils.gpg_config_writer', mock.MagicMock(return_value=None)):
                    with mock.patch('getpass.getpass', mock.MagicMock(return_value="hunter2")):
                        assert bs.verify_gpg_credentials() == ("12345678", "hunter2")

    def test_gpgver_no_sell(self):
        """
        Test lack of both, and not replacing them.
        """
        with mock.patch('bbarchivist.gpgutils.gpg_config_loader', mock.MagicMock(return_value=(None, None))):
            with mock.patch('builtins.input', mock.MagicMock(return_value="n")):
                assert bs.verify_gpg_credentials() == (None, None)

    def test_gpgver_bulk(self):
        """
        Test flag-based per-folder GPG verification.
        """
        dirs = (os.getcwd(), os.getcwd(), os.getcwd(), os.getcwd(), os.getcwd(), os.getcwd())
        with mock.patch('bbarchivist.gpgutils.gpg_config_loader', mock.MagicMock(return_value=("12345678", "hunter2"))):
            with mock.patch('bbarchivist.gpgutils.gpgrunner', mock.MagicMock(side_effect=None)):
                bs.bulk_verify(dirs, True, False, True)
                assert True

    def test_hash_bulk(self):
        """
        Test flag-based per-folder hashing.
        """
        dirs = (os.getcwd(), os.getcwd(), os.getcwd(), os.getcwd(), os.getcwd(), os.getcwd())
        with mock.patch('bbarchivist.hashutils.verifier', mock.MagicMock(side_effect=None)):
            bs.bulk_hash(dirs, True, False, True)
            assert True


class TestClassScriptutilsInfo:
    """
    Test info file generation.
    """
    @classmethod
    def setup_class(cls):
        """
        Safeguard .exe files.
        """
        os.rename("Z10_loader1.exe", "Z10_loader1.exe.bak")
        os.rename("Z10_loader2.exe", "Z10_loader2.exe.bak")
        os.rename("Z10_loader3.exe", "Z10_loader3.exe.bak")

    @classmethod
    def teardown_class(cls):
        """
        Replace .exe files.
        """
        os.rename("Z10_loader1.exe.bak", "Z10_loader1.exe")
        os.rename("Z10_loader2.exe.bak", "Z10_loader2.exe")
        os.rename("Z10_loader3.exe.bak", "Z10_loader3.exe")

    def test_enn_ayy_good(self):
        """
        Test placeholder, best case.
        """
        assert bs.enn_ayy("SNEK") == "SNEK"

    def test_enn_ayy_bad(self):
        """
        Test placeholder, worst case.
        """
        assert bs.enn_ayy(None) == "N/A"

    def test_info_droid(self):
        """
        Test info file generation, Android autoloaders.
        """
        bs.make_info(os.getcwd(), "ABC123", None, None, "Priv")
        final = ['OS: ABC123', 'Device: Priv', '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~', 'File: Z10_loader2.zip', '\tSize: 37 (37.00B)', '\tHashes:', '\t\tMD5: 822E1187FDE7C8D55AFF8CC688701650', '\t\tSHA1: 71DC7CE8F27C11B792BE3F169ECF985865E276D0', '\t\tSHA256: F118871C45171D5FE4E9049980959E033EEEABCFA12046C243FDA310580E8A0B', '\t\tSHA512: B66A5E8AA9B9705748C2EE585B0E1A3A41288D2DAFC3BE2DB12FA89D2F2A3E14F9DEC11DE4BA865BB51EAA6C2CFEB294139455E34DA7D827A19504B0906C01C1', '', 'File: Z10_loader3.zip', '\tSize: 37 (37.00B)', '\tHashes:', '\t\tMD5: 822E1187FDE7C8D55AFF8CC688701650', '\t\tSHA1: 71DC7CE8F27C11B792BE3F169ECF985865E276D0', '\t\tSHA256: F118871C45171D5FE4E9049980959E033EEEABCFA12046C243FDA310580E8A0B', '\t\tSHA512: B66A5E8AA9B9705748C2EE585B0E1A3A41288D2DAFC3BE2DB12FA89D2F2A3E14F9DEC11DE4BA865BB51EAA6C2CFEB294139455E34DA7D827A19504B0906C01C1']
        with open("!ABC123_OSINFO!.txt", "r") as afile:
            content = afile.read()
        assert final == content.splitlines()

    def test_info_qnx(self):
        """
        Test info file generation, BB10/PlayBook autoloaders.
        """
        bs.make_info(os.getcwd(), "10.2.3.4567", "10.2.3.4568", "10.2.3.1234", None)
        final = ['OS: 10.2.3.4567', 'Radio: 10.2.3.4568', 'Software: 10.2.3.1234', '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~', 'File: Z10_loader2.7z', '\tSize: 37 (37.00B)', '\tHashes:', '\t\tMD5: 822E1187FDE7C8D55AFF8CC688701650', '\t\tSHA1: 71DC7CE8F27C11B792BE3F169ECF985865E276D0', '\t\tSHA256: F118871C45171D5FE4E9049980959E033EEEABCFA12046C243FDA310580E8A0B', '\t\tSHA512: B66A5E8AA9B9705748C2EE585B0E1A3A41288D2DAFC3BE2DB12FA89D2F2A3E14F9DEC11DE4BA865BB51EAA6C2CFEB294139455E34DA7D827A19504B0906C01C1']
        with open("!10.2.3.4567_OSINFO!.txt", "r") as afile:
            content = afile.read()
        assert final == content.splitlines()

    def test_info_bulk(self):
        """
        Test flag-based per-folder info generation.
        """
        dirs = (os.getcwd(), os.getcwd(), os.getcwd(), os.getcwd(), os.getcwd(), os.getcwd())
        with mock.patch('bbarchivist.scriptutils.make_info', mock.MagicMock(side_effect=None)):
            bs.bulk_info(dirs, "ABC123", True, False, True, None, None, None)
            assert True