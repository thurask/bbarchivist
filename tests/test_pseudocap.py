#!/usr/bin/env python3
"""Test the pseudocap module."""

import os
from shutil import rmtree, copyfile
from hashlib import sha512
try:
    import unittest.mock as mock
except ImportError:
    import mock
import pytest
import bbarchivist.pseudocap as bp

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2017 Thurask"


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_pseudocap"):
        os.mkdir("temp_pseudocap")
    os.chdir("temp_pseudocap")
    with open("firstfile.signed", "w") as targetfile:
        targetfile.write("Jackdaws love my big sphinx of quartz")
    with open("cap-3.11.0.27.dat", "w") as targetfile:
        targetfile.write("0" * 9500000)
    fpath = os.path.abspath("firstfile.signed")
    bp.make_autoloader("loader1.exe", [fpath])
    bp.make_autoloader("loader2.exe", [fpath, fpath])
    bp.make_autoloader("loader3.exe", [fpath, fpath, fpath])
    bp.make_autoloader("loader4.exe", [fpath, fpath, fpath, fpath])
    bp.make_autoloader("loader5.exe", [fpath, fpath, fpath, fpath, fpath])
    bp.make_autoloader("loader6.exe", [fpath, fpath, fpath, fpath, fpath, fpath])


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_pseudocap", ignore_errors=True)


class TestClassPseudocap:
    """
    Test pseudocap, the Python equivalent of cap.exe.
    """

    def test_ghetto_convert(self):
        """
        Test decimal -> little-endian hex "conversion".
        """
        assert bp.ghetto_convert(987654321) == b'\x00\x00\x00\x00\xb1h\xde:'

    def test_gconvert_nonint(self):
        """
        Test non-int "conversion".
        """
        assert bp.ghetto_convert("987654321") == b'\x00\x00\x00\x00\xb1h\xde:'

    def test_make_offset_len(self):
        """
        Test offset length.
        """
        data = bp.make_offset(["firstfile.signed"])
        assert len(data) == 208

    def test_make_offset_hash(self):
        """
        Test offset integrity.
        """
        shahash = sha512()
        data = bp.make_offset(["firstfile.signed"])
        shahash.update(data)
        thehash = shahash.hexdigest()
        assert thehash == '8001a4814bff60f755d8e86a250fee517e983e54cdfc64964b2120f8ce0444ea786c441f0707f1a8a3ccda612281f6ee226264059833abcf8c910883564e8d32'

    def test_first_loader(self):
        """
        Test loader integrity.
        """
        shahash = sha512()
        with open("loader1.exe", 'rb') as file:
            while True:
                data = file.read(1048576)
                if not data:
                    break
                shahash.update(data)
        thehash = shahash.hexdigest()
        assert thehash == 'f4f6ac62387a665471898b14b4934c594b5877ac4170a1d204264ca8ed9be8709b6c5fd66c75c975ab76e26fbf512a02918d723e34c579d523c3b2bfbd11d6e4'

    def test_second_loader(self):
        """
        Test loader integrity.
        """
        shahash = sha512()
        with open("loader2.exe", 'rb') as file:
            while True:
                data = file.read(1048576)
                if not data:
                    break
                shahash.update(data)
        thehash = shahash.hexdigest()
        assert thehash == '36693f2e4f33d7f8b13b7569339d7731c2d24314ca514b3366ede2221c1bf7da0c65a2a1b52fd53152c9cc2f5893cbb385a7a69e44da3686132a422c598b44b9'

    def test_third_loader(self):
        """
        Test loader integrity.
        """
        shahash = sha512()
        with open("loader3.exe", 'rb') as file:
            while True:
                data = file.read(1048576)
                if not data:
                    break
                shahash.update(data)
        thehash = shahash.hexdigest()
        assert thehash == '31fd64cf114af147f7cdfc7257a7987b2bae9d63fe1fc30042eedc8feee51876cdedbe7b6e33ac45fd6ac575e3305164e267da4d887681703450f8c043c079aa'

    def test_fourth_loader(self):
        """
        Test loader integrity.
        """
        shahash = sha512()
        with open("loader4.exe", 'rb') as file:
            while True:
                data = file.read(1048576)
                if not data:
                    break
                shahash.update(data)
        thehash = shahash.hexdigest()
        assert thehash == 'e33b55ac78823b8f7e637a9b56608ea4fbba75a2660f959597257db74235e3ad63fdefe525621258d24b1ca6948072f6571142a27cca385d90bf63736696f50e'

    def test_fifth_loader(self):
        """
        Test loader integrity.
        """
        shahash = sha512()
        with open("loader5.exe", 'rb') as file:
            while True:
                data = file.read(1048576)
                if not data:
                    break
                shahash.update(data)
        thehash = shahash.hexdigest()
        assert thehash == 'c797f5a7197d6e657c4ff1dbaef7b16bea86e4cfeb631652c487a3181837710f7fb3c33b6f826b39f1e8470388ceae8a3ad0caf6939aba646236cff61ebf16d1'

    def test_sixth_loader(self):
        """
        Test loader integrity.
        """
        shahash = sha512()
        with open("loader6.exe", 'rb') as file:
            while True:
                data = file.read(1048576)
                if not data:
                    break
                shahash.update(data)
        thehash = shahash.hexdigest()
        assert thehash == '511b817b00b33c7c2d007d6dfcb77a10ab1ca1be7ba0dadd47a940cdaf7a03948a58f17a24dcbc0bd1b66dc9a2163a5efd1c0a0ecd5c63d5d6a311c844b168fb'

    def test_invalid_filecount(self, capsys):
        """
        Test invalid number of files sent to autoloader maker.
        """
        with pytest.raises(SystemExit):
            bp.make_autoloader("loader0.exe", [None])
            assert "Invalid filecount" in capsys.readouterr()[0]

    def test_write4k_ioerror(self, capsys):
        """
        Test error incurred by writing 4096 bytes at a time.
        """
        with mock.patch("bbarchivist.pseudocap.write_4k", mock.MagicMock(side_effect=IOError)):
            bp.make_autoloader("loader0.exe", ["firstfile.signed"])
            assert "Operation failed" in capsys.readouterr()[0]

    def test_type_error(self):
        """
        Test file type failure (i.e. file is None).
        """
        with mock.patch("glob.glob", mock.MagicMock(side_effect=TypeError)):
            with pytest.raises(TypeError):
                bp.make_autoloader("loader0.exe", ["zerothfile"])

    def test_target_ioerror(self):
        """
        Test IOError upon opening target file.
        """
        with mock.patch("os.path.join", mock.MagicMock(side_effect=IOError)):
            with pytest.raises(IOError):
                bp.make_autoloader("loader0.exe", ["firstfile"])

    def test_firstfile_ioerror(self):
        """
        Test IOError while writing first signed file.
        """
        with mock.patch("os.path.normpath", mock.MagicMock(side_effect=IOError)):
            with pytest.raises(IOError):
                bp.make_autoloader("loader0.exe", ["firstfile"])

    def test_secondfile_ioerror(self):
        """
        Test IOError while writing second signed file.
        """
        with mock.patch("os.path.normpath", mock.MagicMock(side_effect=IOError)):
            with pytest.raises(IOError):
                bp.make_autoloader("loader0.exe", ["firstfile", "secondfile"])

    def test_thirdfile_ioerror(self):
        """
        Test IOError while writing third signed file.
        """
        with mock.patch("os.path.normpath", mock.MagicMock(side_effect=IOError)):
            with pytest.raises(IOError):
                bp.make_autoloader("loader0.exe", ["firstfile", "secondfile", "thirdfile"])

    def test_fourthfile_ioerror(self):
        """
        Test IOError while writing fourth signed file.
        """
        with mock.patch("os.path.normpath", mock.MagicMock(side_effect=IOError)):
            with pytest.raises(IOError):
                bp.make_autoloader(
                    "loader0.exe", [
                        "firstfile", "secondfile", "thirdfile", "fourthfile"])

    def test_fifthfile_ioerror(self):
        """
        Test IOError while writing fifth signed file.
        """
        with mock.patch("os.path.normpath", mock.MagicMock(side_effect=IOError)):
            with pytest.raises(IOError):
                bp.make_autoloader(
                    "loader0.exe", [
                        "firstfile", "secondfile", "thirdfile", "fourthfile", "fifthfile"])

    def test_sixthfile_ioerror(self):
        """
        Test IOError while writing sixth signed file.
        """
        with mock.patch("os.path.normpath", mock.MagicMock(side_effect=IOError)):
            with pytest.raises(IOError):
                bp.make_autoloader(
                    "loader0.exe", [
                        "firstfile", "secondfile", "thirdfile", "fourthfile", "fifthfile", "sixthfile"])
