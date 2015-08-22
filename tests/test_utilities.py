import bbarchivist.utilities as bu
import os
import pytest
try:
    import unittest.mock as mock
except ImportError:
    import mock
from shutil import rmtree, copyfile
from argparse import ArgumentError
from platform import system


def setup_module(module):
    if not os.path.exists("temp"):
        os.mkdir("temp")
    os.chdir("temp")
    with open("cap-3.11.0.22.dat", "w") as targetfile:
        targetfile.write("Jackdaws love my big sphinx of quartz")
    copyfile("cap-3.11.0.22.dat", "7za.exe")
    copyfile("cap-3.11.0.22.dat", "7za64.exe")


def teardown_module(module):
    if os.path.exists("cap-3.11.0.22.dat"):
        os.remove("cap-3.11.0.22.dat")
    if os.path.exists("7za.exe"):
        os.remove("7za.exe")
    if os.path.exists("7za64.exe"):
        os.remove("7za64.exe")
    os.chdir("..")
    rmtree("temp")


class TestClassUtilities:
    def test_grab_cap(self):
        assert os.path.basename(bu.grab_cap()) == "cap-3.11.0.22.dat"

    def test_filesize_parser(self):
        assert bu.filesize_parser(987654321) == "941.90MB"

    def test_file_exists(self):
        assert bu.file_exists(__file__)

    def test_positive_integer_good(self):
        assert bu.positive_integer(1048576) == 1048576

    def test_positive_integer_bad(self):
        with pytest.raises(ArgumentError) as argexc:
            bu.positive_integer(-34)
            assert "is too low" in str(argexc.value)

    def test_valid_method_good(self):
        assert bu.valid_method("tbz") == "tbz"

    def test_valid_method_bad(self):
        with pytest.raises(ArgumentError) as argexc:
            bu.valid_method("jackdaw")
            assert "invalid method" in argexc

    def test_valid_carrier_good(self):
        assert bu.valid_carrier("302") == "302"

    def test_valid_carrier_bad(self):
        with pytest.raises(ArgumentError) as argexc:
            bu.valid_carrier("1048576")
            assert "invalid code" in str(argexc.value)

    def test_valid_carrier_reallybad(self):
        with pytest.raises(ArgumentError) as argexc:
            bu.valid_carrier("BANANA")
            assert "integer" in str(argexc.value)

    def test_escreens_pin(self):
        assert bu.escreens_pin("ACDCACDC") == "acdcacdc"

    def test_escreens_duration_good(self):
        for dur in (1, 3, 6, 15, 30):
            assert bu.escreens_duration(dur) == dur

    def test_escreens_duration_bad(self):
        with pytest.raises(ArgumentError) as argexc:
            for dur in (2, 4, 7, 16, 31):
                bu.escreens_duration(dur)
                assert "duration" in str(argexc.value)

    def test_str2bool_good(self):
        assert bu.str2bool("YES") == True

    def test_str2bool_bad(self):
        assert bu.str2bool("BANANA") == False

    def test_is_amd64_good(self):
        with mock.patch('platform.machine', mock.MagicMock(return_value="AMD64")):
            assert bu.is_amd64()

    def test_is_amd64_bad(self):
        with mock.patch('platform.machine', mock.MagicMock(return_value="AMD69")):
            assert not bu.is_amd64()

    def test_is_windows_good(self):
        with mock.patch('platform.system', mock.MagicMock(return_value="Windows")):
            assert bu.is_windows()

    def test_is_windows_bad(self):
        with mock.patch('platform.system', mock.MagicMock(return_value="Wandows")):
            assert not bu.is_windows()

    def test_get_seven_zip(self):
        with mock.patch('platform.system', mock.MagicMock(return_value="Wandows")):
            assert bu.get_seven_zip() == "7za"

    def test_win_seven_zip_local_32(self):
        if system != "Windows":
            pass
        else:
            with mock.patch('winreg.OpenKey', mock.MagicMock(return_value=OSError)):
                with mock.patch('platform.machine', mock.MagicMock(return_value="AMD69")):
                    assert bu.win_seven_zip() == "7za.exe"

    def test_win_seven_zip_local_6432(self):
        if system != "Windows":
            pass
        else:
            with mock.patch('winreg.OpenKey', mock.MagicMock(return_value=OSError)):
                with mock.patch('platform.machine', mock.MagicMock(return_value="AMD64")):
                    if not os.path.exists("7za.exe"):
                        copyfile("cap-3.11.0.22.dat", "7za.exe")
                    if os.path.exists("7za64.exe"):
                        os.remove("7za64.exe")
                    assert bu.win_seven_zip() == "error"
                    if os.path.exists("7za64.exe"):
                        os.remove("7za.exe")

    def test_win_seven_zip_local_6464(self):
        if system != "Windows":
            pass
        else:
            with mock.patch('winreg.OpenKey', mock.MagicMock(return_value=OSError)):
                with mock.patch('platform.machine', mock.MagicMock(return_value="AMD64")):
                    if not os.path.exists("7za64.exe"):
                        copyfile("cap-3.11.0.22.dat", "7za64.exe")
                    assert bu.win_seven_zip() == "7za64.exe"
                    if os.path.exists("7za64.exe"):
                        os.remove("7za64.exe")

    def test_win_seven_zip_remote(self):
        if system != "Windows":
            pass
        else:
            with mock.patch('winreg.QueryValueEx', mock.MagicMock(return_value="C:\\Program Files\\7-Zip\\")):
                assert bu.win_seven_zip() == "C:\\Program Files\\7-Zip\\7z.exe"

    def test_get_core_count(self):
        with mock.patch('bbarchivist.utilities.enum_cpus', mock.MagicMock(return_value="123")):
            assert bu.get_core_count() == "123"

    def test_prep_seven_zip_good(self):
        with mock.patch('platform.system', mock.MagicMock(return_value="Wandows")):
            with mock.patch("bbarchivist.utilities.where_which", mock.MagicMock(return_value="/usr/bin/7za")):
                assert bu.prep_seven_zip() == True

    def test_prep_seven_zip_bad(self):
        with mock.patch('platform.system', mock.MagicMock(return_value="Wandows")):
            with mock.patch("bbarchivist.utilities.where_which", mock.MagicMock(return_value=None)):
                assert bu.prep_seven_zip() == False

    def test_version_incrementer_good(self):
        assert bu.version_incrementer("10.3.2.2000", 1000) == "10.3.2.3000"

    def test_version_incrementer_bad(self):
        assert bu.version_incrementer("10.3.2.9999", 3) == "10.3.2.3"

    def test_barname_stripper(self):
        assert bu.barname_stripper("base-nto+armle-v7+signed.bar") == "base"
