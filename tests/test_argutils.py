#!/usr/bin/env python3
"""Test the utilities module."""

import os
from argparse import ArgumentError
from shutil import copyfile, rmtree

import bbarchivist.argutils as ba
import bbarchivist.bbconstants as bc
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2018 Thurask"


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


class TestClassArgutils:
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
        with pytest.raises(ArgumentError) as argexc:
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
        with pytest.raises(ArgumentError) as argexc:
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
        with pytest.raises(ArgumentError) as argexc:
            ba.valid_method("jackdaw")
            assert "invalid method" in argexc

    def test_valid_method_legacy(self):
        """
        Test compression method validity, Python 3.2.
        """
        with mock.patch("bbarchivist.utilities.new_enough", mock.MagicMock(return_value=False)):
            with pytest.raises(ArgumentError) as argexc:
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
        with pytest.raises(ArgumentError) as argexc:
            ba.valid_carrier("1048576")
            assert "invalid code" in str(argexc.value)

    def test_valid_carrier_reallybad(self):
        """
        Test checking of carrier validity, Ragnarök case.
        """
        with pytest.raises(ArgumentError) as argexc:
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
        with pytest.raises(ArgumentError) as argexc:
            ba.escreens_pin("ACDCACDCACDCACDC")
            assert "Invalid PIN" in str(argexc.value)

    def test_escreens_pin_nonhex(self):
        """
        Test checking of escreens PIN, not hexadecimal.
        """
        with pytest.raises(ArgumentError) as argexc:
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
        with pytest.raises(ArgumentError) as argexc:
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
        with pytest.raises(ArgumentError) as argexc:
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
        with pytest.raises(ArgumentError) as argexc:
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
        with pytest.raises(ArgumentError) as argexc:
            ba.droidlookup_devicetype("Neon")
            assert "Invalid" in str(argexc.value)

    def test_droiddev_none(self):
        """
        Test checking Android autoloader lookup hash type, None case.
        """
        assert ba.droidlookup_devicetype(None) == None
