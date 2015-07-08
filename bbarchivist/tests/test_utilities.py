import bbarchivist.utilities as bu
import os
import pytest
try:
    import unittest.mock as mock
except ImportError:
    import mock
from shutil import rmtree, copyfile
from argparse import ArgumentError
from sys import version_info
from platform import system


def setup_module(module):
    if not os.path.exists("temp"):
        os.mkdir("temp")
    os.chdir("temp")
    with open("cap-3.11.0.22.dat", "w") as targetfile:
        targetfile.write("Jackdaws love my big sphinx of quartz")


def teardown_module(module):
    os.remove("cap-3.11.0.22.dat")
    os.chdir("..")
    rmtree("temp")


class TestClassUtilities:
    def test_grab_cap(self):
        assert os.path.basename(bu.grab_cap()) == "cap-3.11.0.22.dat"

    def test_filesize_parser(self):
        assert bu.filesize_parser(987654321) == "941.9MB"

    def test_file_exists(self):
        assert bu.file_exists(__file__)

    def test_positive_integer(self):
        assert bu.positive_integer(1048576) == 1048576
        with pytest.raises(ArgumentError) as argexc:
            bu.positive_integer(-34)
            assert "is too low" in str(argexc.value)

    def test_valid_carrier(self):
        assert bu.valid_carrier("302") == "302"
        with pytest.raises(ArgumentError) as argexc:
            bu.valid_carrier("1048576")
            assert "invalid code" in str(argexc.value)
            bu.valid_carrier("BANANA")
            assert "integer" in str(argexc.value)

    def test_escreens_pin(self):
        assert bu.escreens_pin("ACDCACDC") == "acdcacdc"

    def test_escreens_duration(self):
        for dur in (1, 3, 6, 15, 30):
            assert bu.escreens_duration(dur) == dur

    def test_str2bool(self):
        assert bu.str2bool("YES") == True
        assert bu.str2bool("BANANA") == False

    def test_is_amd64(self):
        with mock.patch('platform.machine', mock.MagicMock(return_value="AMD64")): #@IgnorePep8
            assert bu.is_amd64()
        with mock.patch('platform.machine', mock.MagicMock(return_value="AMD69")): #@IgnorePep8
            assert not bu.is_amd64()

    def test_is_windows(self):
        with mock.patch('platform.system', mock.MagicMock(return_value="Windows")): #@IgnorePep8
            assert bu.is_windows()

        with mock.patch('platform.system', mock.MagicMock(return_value="Wandows")): #@IgnorePep8
            assert not bu.is_windows()

    def test_get_seven_zip(self):
        with mock.patch('platform.system', mock.MagicMock(return_value="Wandows")): #@IgnorePep8
            assert bu.get_seven_zip() == "7za"

    def test_win_seven_zip(self):
        if system != "Windows":
            pass
        else:
            copyfile("cap-3.11.0.22.dat", "7za.exe")
            copyfile("cap-3.11.0.22.dat", "7za64.exe")
            with mock.patch('winreg.OpenKey', mock.MagicMock(return_value=OSError)): #@IgnorePep8
                with mock.patch('platform.machine', mock.MagicMock(return_value="AMD69")): #@IgnorePep8
                    assert bu.win_seven_zip() == "7za.exe"
                with mock.patch('platform.machine', mock.MagicMock(return_value="AMD64")): #@IgnorePep8
                    assert bu.win_seven_zip() == "7za64.exe"
                    os.remove("7za64.exe")
                    assert bu.win_seven_zip() == "error"
                    os.remove("7za.exe")
            with mock.patch('winreg.QueryValueEx', mock.MagicMock(return_value="C:\\Program Files\\7-Zip\\")): #@IgnorePep8
                assert bu.win_seven_zip() == "C:\\Program Files\\7-Zip\\7z.exe"

    def test_get_core_count(self):
        if version_info[1] >= 4:
            prog = 'os.cpu_count'
        else:
            prog = 'multiprocessing.cpu_count'
        with mock.patch(prog, mock.MagicMock(return_value="123")):
            assert bu.get_core_count() == "123"

    def test_prep_seven_zip(self):
        with mock.patch('platform.system', mock.MagicMock(return_value="Wandows")): #@IgnorePep8
            with mock.patch("shutil.which", mock.MagicMock(return_value="/usr/bin/7za")): #@IgnorePep8
                assert bu.prep_seven_zip() == True
            with mock.patch("shutil.which", mock.MagicMock(return_value=None)): #@IgnorePep8
                assert bu.prep_seven_zip() == False

    def test_version_incrementer(self):
        assert bu.version_incrementer("10.3.2.2000", 1000) == "10.3.2.3000"
        assert bu.version_incrementer("10.3.2.9999", 3) == "10.3.2.3"

    def test_barname_stripper(self):
        assert bu.barname_stripper("base-nto+armle-v7+signed.bar") == "base"
