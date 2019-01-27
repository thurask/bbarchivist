#!/usr/bin/env python3
"""Test the utilities module."""

import argparse
import os
import sys
from shutil import rmtree

import bbarchivist.argutils as ba
import bbarchivist.bbconstants as bc
import pytest

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
    if not os.path.exists("temp_argutils"):
        os.mkdir("temp_argutils")
    os.chdir("temp_argutils")


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_argutils", ignore_errors=True)


class TestClassArgutilsArgs:
    """
    Test argument utilities.
    """

    def test_file_exists_good(self):
        """
        Test if self exists. How very Cartesian.
        """
        assert ba.file_exists(__file__)

    def test_file_exists_bad(self):
        """
        Test if non-existent file exists. Of course.
        """
        with pytest.raises(argparse.ArgumentError) as argexc:
            ba.file_exists("qrrbrbirlbel")
            assert "not found" in str(argexc.value)

    def test_positive_integer_good(self):
        """
        Test integer for positive-ness, best case.
        """
        assert ba.positive_integer(1048576) == 1048576

    def test_positive_integer_bad(self):
        """
        Test integer for positive-ness, worst case.
        """
        with pytest.raises(argparse.ArgumentError) as argexc:
            ba.positive_integer(-34)
            assert "is too low" in str(argexc.value)

    def test_valid_method_good(self):
        """
        Test compression method validity, best case.
        """
        assert ba.valid_method("tbz") == "tbz"

    def test_valid_method_bad(self):
        """
        Test compression method validity, worst case.
        """
        with pytest.raises(argparse.ArgumentError) as argexc:
            ba.valid_method("jackdaw")
            assert "invalid method" in argexc

    def test_valid_method_legacy(self):
        """
        Test compression method validity, Python 3.2.
        """
        with mock.patch("bbarchivist.utilities.new_enough", mock.MagicMock(return_value=False)):
            with pytest.raises(argparse.ArgumentError) as argexc:
                ba.valid_method("txz")
                assert "invalid method" in argexc

    def test_valid_carrier_good(self):
        """
        Test checking of carrier validity, best case.
        """
        assert ba.valid_carrier("302") == "302"

    def test_valid_carrier_bad(self):
        """
        Test checking of carrier validity, worst case.
        """
        with pytest.raises(argparse.ArgumentError) as argexc:
            ba.valid_carrier("1048576")
            assert "invalid code" in str(argexc.value)

    def test_valid_carrier_reallybad(self):
        """
        Test checking of carrier validity, Ragnarök case.
        """
        with pytest.raises(argparse.ArgumentError) as argexc:
            ba.valid_carrier("BANANA")
            assert "integer" in str(argexc.value)

    def test_escreens_pin_good(self):
        """
        Test checking of escreens PIN.
        """
        assert ba.escreens_pin("ACDCACDC") == "acdcacdc"

    def test_escreens_pin_long(self):
        """
        Test checking of escreens PIN, too long.
        """
        with pytest.raises(argparse.ArgumentError) as argexc:
            ba.escreens_pin("ACDCACDCACDCACDC")
            assert "Invalid PIN" in str(argexc.value)

    def test_escreens_pin_nonhex(self):
        """
        Test checking of escreens PIN, not hexadecimal.
        """
        with pytest.raises(argparse.ArgumentError) as argexc:
            ba.escreens_pin("MONGOLIA")
            assert "Invalid PIN" in str(argexc.value)

    def test_escreens_duration_good(self):
        """
        Test checking of escreens duration, best case.
        """
        for dur in (1, 3, 6, 15, 30):
            assert ba.escreens_duration(dur) == dur

    def test_escreens_duration_bad(self):
        """
        Test checking of escreens duration, worst case.
        """
        with pytest.raises(argparse.ArgumentError) as argexc:
            for dur in (2, 4, 7, 16, 31):
                ba.escreens_duration(dur)
                assert "duration" in str(argexc.value)

    def test_signed_files_good(self):
        """
        Test checking a signed file list, best case.
        """
        assert ba.signed_file_args(["snek", "snek", None]) == (["snek", "snek", None])

    def test_signed_files_bad(self):
        """
        Test checking a signed file list, worst case.
        """
        with pytest.raises(argparse.ArgumentError) as argexc:
            ba.signed_file_args([None])
            assert "requires" in str(argexc.value)

    def test_droidhash_good(self):
        """
        Test checking Android autoloader lookup hash type, best case.
        """
        assert ba.droidlookup_hashtype("SHA512") == "sha512"

    def test_droidhash_bad(self):
        """
        Test checking Android autoloader lookup hash type, worst case.
        """
        with pytest.raises(argparse.ArgumentError) as argexc:
            ba.droidlookup_hashtype("MD5")
            assert "Invalid" in str(argexc.value)

    def test_droiddev_good(self):
        """
        Test checking Android autoloader lookup hash type, best case.
        """
        assert ba.droidlookup_devicetype("dTeK50") == "DTEK50"

    def test_droiddev_bad(self):
        """
        Test checking Android autoloader lookup hash type, worst case.
        """
        with pytest.raises(argparse.ArgumentError) as argexc:
            ba.droidlookup_devicetype("Neon")
            assert "Invalid" in str(argexc.value)

    def test_droiddev_none(self):
        """
        Test checking Android autoloader lookup hash type, None case.
        """
        assert ba.droidlookup_devicetype(None) is None


class TestClassArgutilsParserPrep:
    """
    pass
    """
    def test_slim_preamble(self, capsys):
        """
        Test single line app header.
        """
        ba.slim_preamble("snek")
        assert "SNEK" in capsys.readouterr()[0]

    def test_standard_preamble(self, capsys):
        """
        Test multi-line app header.
        """
        ba.standard_preamble("snek", "10.3.2.2639", "10.3.2.2474", "10.3.2.2877", "10.3.2.2836")
        assert "2836" in capsys.readouterr()[0]

    def test_shortversion(self, monkeypatch):
        """
        Test version getting, short type.
        """
        monkeypatch.setattr("sys.frozen", True, raising=False)
        with open("version.txt", "w") as afile:
            afile.write("10.0.10586.1000")
        assert ba.shortversion() == "10.0.10586.1000"
        monkeypatch.setattr("sys.frozen", False, raising=False)

    def test_shortversion_unfrozen(self, monkeypatch):
        """
        Test version getting, short type, not frozen.
        """
        monkeypatch.setattr("sys.frozen", False, raising=False)
        assert ba.shortversion() == bc.VERSION

    def test_longversion(self, monkeypatch):
        """
        Test version getting, long type.
        """
        monkeypatch.setattr("sys.frozen", True, raising=False)
        with open("longversion.txt", "w") as afile:
            afile.write("10.0.10586.1000\n1970-01-01")
        assert ba.longversion() == ["10.0.10586.1000", "1970-01-01"]
        monkeypatch.setattr("sys.frozen", False, raising=False)

    def test_longversion_unfrozen(self, monkeypatch):
        """
        Test version getting, long type, not frozen.
        """
        monkeypatch.setattr("sys.frozen", False, raising=False)
        assert ba.longversion() == (bc.LONGVERSION, bc.COMMITDATE)


class TestClassArgutilsParser:
    """
    Test argparse parser generation.
    """
    @classmethod
    def setup_class(cls):
        """
        Create parser for testing.
        """
        cls.parser = ba.default_parser("name", "Formats C:", flags=("folder", "osr"), vers=["deadbeef", "1970-01-01"])

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
        newpar = ba.external_version(self.parser, "|SNEKSNEK")
        verarg = [x for x in newpar._actions if isinstance(x, argparse._VersionAction)][0]
        assert verarg.version == "name deadbeef committed 1970-01-01|SNEKSNEK"

    def test_arg_verify_none(self):
        """
        Test if argument is None.
        """
        with pytest.raises(argparse.ArgumentError):
            ba.arg_verify_none(None, "SNEK!")


class TestClassArgutilsShim:
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
            ba.generic_windows_shim("cap", "CAP!", "cap.exe", "3.10")
            assert "Sorry, Windows only." in capsys.readouterr()[0]

    def test_windows_shim_windows(self, capsys):
        """
        Test CFP/CAP shim on Windows.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Windows")):
            with mock.patch('subprocess.call', mock.MagicMock(side_effect=print("Snek!"))):
                ba.generic_windows_shim("cap", "CAP!", "cap.exe", "3.10")
                assert "Snek!" in capsys.readouterr()[0]
