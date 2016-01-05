#!/usr/bin/env python3
"""Test the scriptutils module."""

import os
from shutil import rmtree, copyfile
import zipfile
try:
    import unittest.mock as mock
except ImportError:
    import mock
import pytest
import bbarchivist.scriptutils as bs

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


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

    def test_purge_dross(self):
        """
        Test excluding useless garbage from a list of apps.
        """
        apps = ["os.bar", "radio.bar", "retaildemo.bar", "nuance_common.bar"]
        assert bs.purge_dross(apps) == apps[:2]

    def test_blitz_links(self):
        """
        Test creating blitz links.
        """
        with mock.patch('bbarchivist.networkutils.create_base_url',
                        mock.MagicMock(return_value="abacab")):
            links = bs.generate_blitz_links([], "10.2.2.2222",
                                            "10.3.3.3333", "10.4.4.4444")
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
        with mock.patch('bbarchivist.networkutils.get_length', mock.MagicMock(return_value=12345)):
            bs.export_cchecker(["http://sn.ek"], None, None, "10.1.1.1111",
                               "10.2.2.2222", "10.3.3.3333", True, None)
            with open("10.3.3.3333plusapps.txt", "r") as afile:
                assert len(afile.read()) == 2926

    def test_cchecker_export_debrick(self):
        """
        Test exporting links, having to find upgrade files.
        """
        snek = Dummy()
        with mock.patch('requests.head', mock.MagicMock(return_value=snek)):
            bs.export_cchecker(["http://sn.ek"], "123456", "8500090A", "10.1.1.1111",
                                "10.2.2.2222", "10.3.3.3334", False, None)
            with open("10.3.3.3334plusapps.txt", "r") as afile:
                assert len(afile.read()) == 2933


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
        with mock.patch('bbarchivist.networkutils.sr_lookup',
                        mock.MagicMock(return_value="10.3.2.2474")):
            assert bs.return_sw_checked(None, "10.3.2.2639") == ("10.3.2.2474", True)

    def test_return_swc_explicit(self):
        """
        Test software release checking, failure and definition.
        """
        with mock.patch('bbarchivist.networkutils.sr_lookup',
                        mock.MagicMock(return_value="SR not in system")):
            with mock.patch('builtins.input', mock.MagicMock(return_value="10.3.2.9999")):
                with mock.patch('bbarchivist.utilities.s2b', mock.MagicMock(return_value=True)):
                    assert bs.return_sw_checked(None, "10.3.2.2639") == ("10.3.2.9999", False)

    def test_return_swc_exit(self):
        """
        Test exiting upon software release check failure.
        """
        with mock.patch('bbarchivist.networkutils.sr_lookup',
                        mock.MagicMock(return_value="SR not in system")):
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
        with mock.patch('bbarchivist.networkutils.sr_lookup',
                        mock.MagicMock(return_value="SR not in system")):
            with mock.patch('builtins.input', mock.MagicMock(return_value="10.3.2.2474")):
                with mock.patch('bbarchivist.utilities.s2b', mock.MagicMock(return_value=True)):
                    assert bs.return_radio_sw_checked("checkme", "10.3.2.2640") == ("10.3.2.2474", False)

    def test_return_rswc_exit(self):
        """
        Test exiting upon radio software release check failure.
        """
        with mock.patch('bbarchivist.networkutils.sr_lookup',
                        mock.MagicMock(return_value="SR not in system")):
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
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=True)):
            bs.check_sw("http://qrrbrbirlbel.yu/", "10.3.2.2474", False)
            assert "EXISTS" in capsys.readouterr()[0]

    def test_check_sw_exit(self):
        """
        Test exiting upon software release availability failure.
        """
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="n")):
                with pytest.raises(SystemExit):
                    bs.check_sw("http://qrrbrbirlbel.yu/", "10.3.2.2474", False)

    def test_check_sw_go(self):
        """
        Test continuing upon software release availability failure.
        """
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=False)):
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
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=True)):
            bs.check_radio_sw("http://qrrbrbirlbel.yu/", "10.3.2.2474", False)
            assert "EXISTS" in capsys.readouterr()[0]

    def test_check_rsw_exit(self):
        """
        Test exiting upon radio software release availability failure.
        """
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="n")):
                with pytest.raises(SystemExit):
                    bs.check_radio_sw("http://qrrbrbirlbel.yu/", "10.3.2.2474", False)

    def test_check_rsw_go(self):
        """
        Test continuing upon radio software release availability failure.
        """
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="y")):
                assert bs.check_radio_sw("http://qrrbrbirlbel.yu/", "10.3.2.2474", False) is None


class TestClassScriptutilsURLCheck:
    """
    Test URL-related utilities.
    """
    def test_os_single(self, capsys):
        """
        Test single OS availability.
        """
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=True)):
            bs.check_os_single("http://qrrbrbirlbel.yu/", "10.3.2.2639", 0)
            assert "NOT AVAILABLE" not in capsys.readouterr()[0]

    def test_os_single_fail(self):
        """
        Test single OS availability failure.
        """
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="n")):
                with pytest.raises(SystemExit):
                    bs.check_os_single("http://qrrbrbirlbel.yu/", "10.3.2.2639", 0)

    def test_os_single_go(self):
        """
        Test single OS availability continuation.
        """
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="y")):
                assert bs.check_os_single("http://qrrbrbirlbel.yu/", "10.3.2.2639", 0) is None

    def test_os_bulk(self, capsys):
        """
        Test bulk OS availability.
        """
        osurls = ["http://qrrbrbirlbel.yu/", "http://zeekyboogydoog.su/"]
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=True)):
            bs.check_os_bulk(osurls)
            assert "NOT FOUND" not in capsys.readouterr()[0]

    def test_os_bulk_fail(self):
        """
        Test bulk OS availability failure.
        """
        osurls = ["http://qrrbrbirlbel.yu/", "http://zeekyboogydoog.su/"]
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="n")):
                with pytest.raises(SystemExit):
                    bs.check_os_bulk(osurls)

    def test_os_bulk_go(self):
        """
        Test bulk OS availability continuation.
        """
        osurls = ["http://qrrbrbirlbel.yu/", "http://zeekyboogydoog.su/"]
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="y")):
                assert bs.check_os_bulk(osurls) is None

    def test_radio_single(self, capsys):
        """
        Test single radio availability.
        """
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=True)):
            assert bs.check_radio_single("http://qrrbrbirlbel.yu/",
                                         "10.3.2.2640") == ("http://qrrbrbirlbel.yu/",
                                                            "10.3.2.2640")
            assert "NOT AVAILABLE" not in capsys.readouterr()[0]

    def test_radio_single_fail(self):
        """
        Test single radio availability failure.
        """
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="n")):
                with pytest.raises(SystemExit):
                    bs.check_radio_single("http://qrrbrbirlbel.yu/", "10.3.2.2639")

    def test_radio_single_replace(self):
        """
        Test single radio availability replacement.
        """
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="y")):
                assert bs.check_radio_single("http://qrrbrbirlbel.yu/", "10.3.2.2639") == ("http://qrrbrbirlbel.yu/", "y")

    def test_radio_bulk(self, capsys):
        """
        Test bulk radio availability.
        """
        radiourls = ["http://qrrbrbirlbel.yu/", "http://zeekyboogydoog.su/"]
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=True)):
            assert bs.check_radio_bulk(radiourls,
                                       "10.3.2.2640") == (radiourls,
                                                          "10.3.2.2640")
            assert "NOT FOUND" not in capsys.readouterr()[0]

    def test_radio_bulk_fail(self):
        """
        Test bulk radio availability failure.
        """
        radiourls = ["http://qrrbrbirlbel.yu/", "http://zeekyboogydoog.su/"]
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="n")):
                with pytest.raises(SystemExit):
                    bs.check_radio_bulk(radiourls, "10.3.2.2639")

    def test_radio_bulk_replace(self):
        """
        Test bulk radio availability replacement.
        """
        radiourls = ["http://qrrbrbirlbel.yu/", "http://zeekyboogydoog.su/"]
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="y")):
                assert bs.check_radio_bulk(radiourls, "10.3.2.2639") == (radiourls, "y")


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
        with mock.patch('bbarchivist.utilities.prep_seven_zip',
                        mock.MagicMock(return_value=True)):
            with mock.patch('bbarchivist.utilities.get_seven_zip',
                            mock.MagicMock(return_value="jackdaw")):
                assert bs.get_sz_executable("7z") == ("7z", "jackdaw")

    def test_szexe_exit(self):
        """
        Test exiting upon not finding 7z exe.
        """
        with mock.patch('bbarchivist.utilities.prep_seven_zip',
                        mock.MagicMock(return_value=False)):
            with mock.patch('builtins.input', mock.MagicMock(return_value="n")):
                with pytest.raises(SystemExit):
                    bs.get_sz_executable("7z")

    def test_szexe_fallback(self):
        """
        Test falling back to zip upon not finding 7z exe.
        """
        with mock.patch('bbarchivist.utilities.prep_seven_zip',
                        mock.MagicMock(return_value=False)):
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
        cls.parser = bs.default_parser("name", "Formats C:")

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
        assert self.parser.epilog == "http://github.com/thurask/bbarchivist"


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
        with zipfile.ZipFile("mfest.bar", mode="w",
                             compression=zipfile.ZIP_DEFLATED) as zfile:
            zfile.writestr("MANIFEST.MF", cls.mstring)
            zfile.writestr("target.signed", cls.fstring)
        with zipfile.ZipFile("bkmfest.bar", mode="w",
                             compression=zipfile.ZIP_DEFLATED) as zfile:
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
            with mock.patch('bbarchivist.utilities.verify_loader_integrity',
                            mock.MagicMock(return_value=True)):
                bs.test_single_loader("Z10_loader1.exe")
                assert "OK" in capsys.readouterr()[0]

    def test_loader_single_bad(self):
        """
        Test checking one loader, worst case.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Windows")):
            with mock.patch('bbarchivist.utilities.verify_loader_integrity',
                            mock.MagicMock(return_value=False)):
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
            with mock.patch('bbarchivist.utilities.verify_loader_integrity',
                            mock.MagicMock(return_value=True)):
                bs.test_loader_files(os.getcwd())
                assert "OK" in capsys.readouterr()[0]

    def test_loader_bulk_bad(self):
        """
        Test checking many loaders, worst case.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Windows")):
            with mock.patch('bbarchivist.utilities.verify_loader_integrity',
                            mock.MagicMock(return_value=False)):
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


class TestClassScriptutilsGPG:
    """
    Test GPG-related utilities.
    """
    def test_gpgver_unchanged(self):
        """
        Test no modifications to GPG credentials.
        """
        with mock.patch('bbarchivist.filehashtools.gpg_config_loader',
                        mock.MagicMock(return_value=("12345678", "hunter2"))):
            assert bs.verify_gpg_credentials() == ("12345678", "hunter2")

    def test_gpgver_key(self):
        """
        Test lack of GPG key.
        """
        with mock.patch('bbarchivist.filehashtools.gpg_config_loader',
                        mock.MagicMock(return_value=(None, "hunter2"))):
            with mock.patch('builtins.input', mock.MagicMock(return_value="y")):
                with mock.patch('bbarchivist.filehashtools.gpg_config_writer',
                                mock.MagicMock(return_value=None)):
                    assert bs.verify_gpg_credentials() == ("0xy", "hunter2")

    def test_gpgver_pass(self):
        """
        Test lack of GPG pass.
        """
        with mock.patch('bbarchivist.filehashtools.gpg_config_loader',
                        mock.MagicMock(return_value=("12345678", None))):
            with mock.patch('builtins.input', mock.MagicMock(return_value="y")):
                with mock.patch('bbarchivist.filehashtools.gpg_config_writer',
                                mock.MagicMock(return_value=None)):
                    with mock.patch('getpass.getpass', mock.MagicMock(return_value="hunter2")):
                        assert bs.verify_gpg_credentials() == ("12345678", "hunter2")

    def test_gpgver_no_sell(self):
        """
        Test lack of both, and not replacing them.
        """
        with mock.patch('bbarchivist.filehashtools.gpg_config_loader',
                        mock.MagicMock(return_value=(None, None))):
            with mock.patch('builtins.input', mock.MagicMock(return_value="n")):
                assert bs.verify_gpg_credentials() == (None, None)
