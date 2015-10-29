#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, W0622, C0103
"""Test the utilities module."""

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
    """
    Create necessary files.
    """
    if not os.path.exists("temp_utilities"):
        os.mkdir("temp_utilities")
    os.chdir("temp_utilities")
    with open("cap-3.11.0.22.dat", "w") as targetfile:
        targetfile.write("Jackdaws love my big sphinx of quartz")
    copyfile("cap-3.11.0.22.dat", "7za.exe")
    copyfile("cap-3.11.0.22.dat", "7za64.exe")
    copyfile("cap-3.11.0.22.dat", "Z10_loader1.exe")
    copyfile("cap-3.11.0.22.dat", "Z10_loader2.exe")
    copyfile("cap-3.11.0.22.dat", "Z10_loader3.exe")


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_utilities", ignore_errors=True)


class TestClassUtilities7z:
    """
    Test utilities related to 7-Zip.
    """
    def test_get_seven_zip(self):
        """
        Test checking of 7z.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Wandows")):
            assert bu.get_seven_zip(True) == "7za"

    def test_win_seven_zip_local_32(self):
        """
        Test local checking of 7z, 32-bit on 32-bit.
        """
        if system != "Windows":
            pass
        else:
            with mock.patch('winreg.QueryValueEx', mock.MagicMock(return_value=OSError)):
                with mock.patch('platform.machine', mock.MagicMock(return_value="AMD69")):
                    assert bu.win_seven_zip(True) == "7za.exe"

    def test_win_seven_zip_local_6432(self):
        """
        Test local checking of 7z, 32-bit on 64-bit.
        """
        if system != "Windows":
            pass
        else:
            with mock.patch('winreg.QueryValueEx', mock.MagicMock(return_value=OSError)):
                with mock.patch('platform.machine', mock.MagicMock(return_value="AMD64")):
                    if not os.path.exists("7za.exe"):
                        copyfile("cap-3.11.0.22.dat", "7za.exe")
                    if os.path.exists("7za64.exe"):
                        os.remove("7za64.exe")
                    assert bu.win_seven_zip(True) == "error"
                    if os.path.exists("7za64.exe"):
                        os.remove("7za.exe")

    def test_win_seven_zip_local_6464(self):
        """
        Test local checking of 7z, 64-bit on 64-bit.
        """
        if system != "Windows":
            pass
        else:
            with mock.patch('winreg.QueryValueEx', mock.MagicMock(return_value=OSError)):
                with mock.patch('platform.machine', mock.MagicMock(return_value="AMD64")):
                    if not os.path.exists("7za64.exe"):
                        copyfile("cap-3.11.0.22.dat", "7za64.exe")
                    assert bu.win_seven_zip(True) == "7za64.exe"
                    if os.path.exists("7za64.exe"):
                        os.remove("7za64.exe")

    def test_win_seven_zip_remote(self):
        """
        Test registry checking of 7z.
        """
        if system != "Windows":
            pass
        else:
            with mock.patch('winreg.QueryValueEx', mock.MagicMock(return_value="C:\\Program Files\\7-Zip\\")):
                assert bu.win_seven_zip(True) == "C:\\Program Files\\7-Zip\\7z.exe"

    def test_prep_seven_zip_good(self):
        """
        Test availability of 7z, best case.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Wandows")):
            with mock.patch("bbarchivist.utilities.where_which", mock.MagicMock(return_value="/usr/bin/7za")):
                assert bu.prep_seven_zip(True) == True

    def test_prep_seven_zip_bad(self):
        """
        Test availability of 7z, worst case.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Wandows")):
            with mock.patch("bbarchivist.utilities.where_which", mock.MagicMock(return_value=None)):
                assert bu.prep_seven_zip(True) == False

    def test_prep_seven_zip_which(self):
        """
        Test availability of 7z, no which.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Wandows")):
            with mock.patch("bbarchivist.utilities.where_which", mock.MagicMock(side_effect=ImportError)):
                assert bu.prep_seven_zip(True) == False


class TestClassUtilitiesPlatform:
    """
    Test platform utilities.
    """
    def test_is_amd64_good(self):
        """
        Test checking of AMD64 OS, best case.
        """
        with mock.patch('platform.machine', mock.MagicMock(return_value="AMD64")):
            assert bu.is_amd64()

    def test_is_amd64_bad(self):
        """
        Test checking of AMD64 OS, worst case.
        """
        with mock.patch('platform.machine', mock.MagicMock(return_value="AMD69")):
            assert not bu.is_amd64()

    def test_is_windows_good(self):
        """
        Test checking of Windows platform, best case.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Windows")):
            assert bu.is_windows()

    def test_is_windows_bad(self):
        """
        Test checking of Windows platform, worst case.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Wandows")):
            assert not bu.is_windows()

    def test_get_core_count(self):
        """
        Test core count.
        """
        with mock.patch('bbarchivist.utilities.enum_cpus', mock.MagicMock(return_value="123")):
            assert bu.get_core_count() == "123"


class TestClassUtilitiesLoaders:
    """
    Test autoloader integrity checking.
    """
    def test_integrity_single_good(self):
        """
        Test checking return code of one autoloader, best case.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Windows")):
            with mock.patch('subprocess.call', mock.MagicMock(return_value=0)):
                assert bu.verify_loader_integrity("Z10_loader1.exe")

    def test_integrity_single_bad(self):
        """
        Test checking return code of one autoloader, worst case.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Windows")):
            with mock.patch('subprocess.call', mock.MagicMock(return_value=255)):
                assert not bu.verify_loader_integrity("Z10_loader1.exe")

    def test_integrity_single_exception(self):
        """
        Test checking return code of one autoloader, if OSError is raised.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Windows")):
            with mock.patch('subprocess.call', mock.MagicMock(side_effect=OSError)):
                assert not bu.verify_loader_integrity("Z10_loader1.exe")

    def test_integrity_single_nonwin(self):
        """
        Test checking return code of one autoloader, non-Windows.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Wandows")):
            assert bu.verify_loader_integrity(os.devnull) is None

    def test_integrity_bulk_good(self):
        """
        Test checking return code of all autoloaders, best case.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Windows")):
            with mock.patch('subprocess.call', mock.MagicMock(return_value=0)):
                assert not bu.verify_bulk_loaders(os.getcwd())

    def test_integrity_bulk_bad(self):
        """
        Test checking return code of all autoloaders, worst case.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Windows")):
            with mock.patch('subprocess.call', mock.MagicMock(return_value=255)):
                assert bu.verify_bulk_loaders(os.getcwd())

    def test_integrity_bulk_nonwin(self):
        """
        Test checking return code of all autoloaders, non-Windows.
        """
        with mock.patch('platform.system', mock.MagicMock(return_value="Wandows")):
            assert bu.verify_bulk_loaders(os.devnull) is None


class TestClassUtilities:
    """
    Test miscellaneous utilities.
    """
    def test_grab_cap(self):
        """
        Test finding cap location.
        """
        assert os.path.dirname(bu.grab_cap()) == os.getcwd()

    def test_where_which(self):
        """
        Test implementation of where.
        """
        with mock.patch("shutil.which", mock.MagicMock(return_value="here")):
            assert bu.where_which("woodo") == "here"

    def test_str2bool_good(self):
        """
        Test checking of input parsing, best case.
        """
        assert bu.str2bool("YES") == True

    def test_str2bool_bad(self):
        """
        Test checking of input parsing, worst case.
        """
        assert bu.str2bool("BANANA") == False

    def test_version_incrementer_good(self):
        """
        Test version incrementing, best case.
        """
        assert bu.version_incrementer("10.3.2.2000", 1000) == "10.3.2.3000"

    def test_version_incrementer_bad(self):
        """
        Test version incrementing, worst case.
        """
        assert bu.version_incrementer("10.3.2.9999", 3) == "10.3.2.3"

    def test_barname_stripper(self):
        """
        Test bar name cleaning.
        """
        assert bu.barname_stripper("base-nto+armle-v7+signed.bar") == "base"

    def test_return_and_delete(self):
        """
        Test reading a file then deleting it.
        """
        with open("TEST.txt", "w") as afile:
            afile.write("You can call me Al")
        assert bu.return_and_delete("TEST.txt") == "You can call me Al"


class TestClassUtilitiesStdout:
    """
    Test UselessStdout and related things.
    """
    def test_uselessstdout_tty(self):
        """
        Test if UselessStdout is a terminal.
        """
        assert bu.UselessStdout.isatty()

    def test_spinner_interrupt(self):
        """
        Test interrupting the Spinner.
        """
        with mock.patch("bbarchivist.utilities.Spinner.next",
                        mock.MagicMock(side_effect=KeyboardInterrupt)):
            with pytest.raises(KeyboardInterrupt):
                spin = bu.Spinner()
                spin.next()


class TestClassUtilitiesUrls:
    """
    Test generation of URLs.
    """
    def test_bulk(self):
        """
        Test generating all URLs.
        """
        osu, radu, coru = bu.generate_urls("http://www.qrrbrbirlbel.yu/", "10.3.2.4567", "10.9.8.7654", True)
        del radu, coru
        assert "http://www.qrrbrbirlbel.yu//qc8960.factory_sfi_hybrid_qc8974.desktop-10.3.2.4567-nto+armle-v7+signed.bar" in osu

    def test_bulk_nocore(self):
        """
        Test generating only debrick and radio URLs.
        """
        osu, radu, coru = bu.generate_urls("http://www.qrrbrbirlbel.yu/", "10.2.3.4567", "10.9.8.7654", False)
        del osu, radu
        assert not coru

    def test_stl1(self):
        """
        Test STL100-1 URLs.
        """
        ourl, rurl = bu.generate_lazy_urls("http://www.qrrbrbirlbel.yu/", "10.2.3.4567", "10.9.8.7654", 0)
        assert "winchester" in ourl
        assert "m5730" in rurl

    def test_stlx(self):
        """
        Test STL100-X URLs.
        """
        ourl, rurl = bu.generate_lazy_urls("http://www.qrrbrbirlbel.yu/", "10.2.3.4567", "10.9.8.7654", 1)
        assert "qc8960.factory_sfi" in ourl
        assert "qc8960-" in rurl

    def test_stl4(self):
        """
        Test STL100-4 URLs.
        """
        ourl, rurl = bu.generate_lazy_urls("http://www.qrrbrbirlbel.yu/", "10.2.3.4567", "10.9.8.7654", 2)
        assert "verizon" in ourl
        assert "qc8960.omadm" in rurl

    def test_q10(self):
        """
        Test Q10 URLs.
        """
        ourl, rurl = bu.generate_lazy_urls("http://www.qrrbrbirlbel.yu/", "10.2.3.4567", "10.9.8.7654", 3)
        assert "qc8960.factory_sfi" in ourl
        assert "qc8960.wtr" in rurl

    def test_z30(self):
        """
        Test Z30 URLs.
        """
        ourl, rurl = bu.generate_lazy_urls("http://www.qrrbrbirlbel.yu/", "10.2.3.4567", "10.9.8.7654", 4)
        assert "qc8960.factory_sfi" in ourl
        assert "qc8960.wtr5" in rurl

    def test_z3(self):
        """
        Test Z3 URLs.
        """
        ourl, rurl = bu.generate_lazy_urls("http://www.qrrbrbirlbel.yu/", "10.2.3.4567", "10.9.8.7654", 5)
        assert "qc8960.factory_sfi" in ourl
        assert "qc8930" in rurl

    def test_z3_alt(self):
        """
        Test Z3 URLs, having been updated due to OS version.
        """
        ourl, rurl = bu.generate_lazy_urls("http://www.qrrbrbirlbel.yu/", "10.9.8.7654", "10.2.3.4567", 5)
        assert "qc8960.factory_sfi_hybrid_qc8x30" in ourl
        assert "qc8930" in rurl

    def test_8974(self):
        """
        Test 8974 URLs.
        """
        ourl, rurl = bu.generate_lazy_urls("http://www.qrrbrbirlbel.yu/", "10.2.3.4567", "10.9.8.7654", 6)
        assert "qc8974" in ourl
        assert "8974.wtr2" in rurl

    def test_8974_alt(self):
        """
        Test 8974 URLs, having been updated due to OS version.
        """
        ourl, rurl = bu.generate_lazy_urls("http://www.qrrbrbirlbel.yu/", "10.9.8.7654", "10.2.3.4567", 6)
        assert "qc8960.factory_sfi_hybrid_qc8974" in ourl
        assert "qc8974.wtr2" in rurl


class TestClassUtilitiesArgparse:
    """
    Test miscellaneous utilities involving arguments.
    """
    def test_filesize_parser_good(self):
        """
        Test parsing of filesize, ideal case.
        """
        assert bu.filesize_parser(987654321) == "941.90MB"

    def test_filesize_parser_none(self):
        """
        Test parsing of filesize, None given.
        """
        assert bu.filesize_parser(None) == "0.00B"

    def test_filesize_parser_huge(self):
        """
        Test parsing of filesize, large number given.
        """
        assert bu.filesize_parser(pow(2, 80)) == "1.00YB"

    def test_file_exists_good(self):
        """
        Test if self exists. How very Cartesian.
        """
        assert bu.file_exists(__file__)

    def test_file_exists_bad(self):
        """
        Test if non-existent file exists. Of course.
        """
        with pytest.raises(ArgumentError) as argexc:
            bu.file_exists("qrrbrbirlbel")
            assert "not found" in str(argexc.value)

    def test_positive_integer_good(self):
        """
        Test integer for positive-ness, best case.
        """
        assert bu.positive_integer(1048576) == 1048576

    def test_positive_integer_bad(self):
        """
        Test integer for positive-ness, worst case.
        """
        with pytest.raises(ArgumentError) as argexc:
            bu.positive_integer(-34)
            assert "is too low" in str(argexc.value)

    def test_valid_method_good(self):
        """
        Test compression method validity, best case.
        """
        assert bu.valid_method("tbz") == "tbz"

    def test_valid_method_bad(self):
        """
        Test compression method validity, worst case.
        """
        with pytest.raises(ArgumentError) as argexc:
            bu.valid_method("jackdaw")
            assert "invalid method" in argexc

    def test_valid_carrier_good(self):
        """
        Test checking of carrier validity, best case.
        """
        assert bu.valid_carrier("302") == "302"

    def test_valid_carrier_bad(self):
        """
        Test checking of carrier validity, worst case.
        """
        with pytest.raises(ArgumentError) as argexc:
            bu.valid_carrier("1048576")
            assert "invalid code" in str(argexc.value)

    def test_valid_carrier_reallybad(self):
        """
        Test checking of carrier validity, Ragnarök case.
        """
        with pytest.raises(ArgumentError) as argexc:
            bu.valid_carrier("BANANA")
            assert "integer" in str(argexc.value)

    def test_escreens_pin_good(self):
        """
        Test checking of escreens PIN.
        """
        assert bu.escreens_pin("ACDCACDC") == "acdcacdc"

    def test_escreens_pin_long(self):
        """
        Test checking of escreens PIN, too long.
        """
        with pytest.raises(ArgumentError) as argexc:
            bu.escreens_pin("ACDCACDCACDCACDC")
            assert "Invalid PIN" in str(argexc.value)

    def test_escreens_pin_nonhex(self):
        """
        Test checking of escreens PIN, not hexadecimal.
        """
        with pytest.raises(ArgumentError) as argexc:
            bu.escreens_pin("MONGOLIA")
            assert "Invalid PIN" in str(argexc.value)

    def test_escreens_duration_good(self):
        """
        Test checking of escreens duration, best case.
        """
        for dur in (1, 3, 6, 15, 30):
            assert bu.escreens_duration(dur) == dur

    def test_escreens_duration_bad(self):
        """
        Test checking of escreens duration, worst case.
        """
        with pytest.raises(ArgumentError) as argexc:
            for dur in (2, 4, 7, 16, 31):
                bu.escreens_duration(dur)
                assert "duration" in str(argexc.value)


class TestClassUtilitiesConfig:
    """
    Test reading/writing configs with ConfigParser.
    """
    def test_cappath_loader(self):
        """
        Test reading CAP path settings.
        """
        try:
            FileNotFoundError
        except NameError:
            FileNotFoundError = IOError
        try:
            os.remove("bbarchivist.ini")
        except (OSError, FileNotFoundError):
            pass
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.getcwd())):
            with mock.patch('bbarchivist.bbconstants.CAPLOCATION', "cap.dat"):
                assert bu.cappath_config_loader() == "cap.dat"

    def test_cappath_writer(self):
        """
        Test writing CAP path settings.
        """
        try:
            FileNotFoundError
        except NameError:
            FileNotFoundError = IOError
        try:
            os.remove("bbarchivist.ini")
        except (OSError, FileNotFoundError):
            pass
        with mock.patch('bbarchivist.utilities.grab_cap',
                        mock.MagicMock(return_value=os.path.abspath(os.path.join(os.getcwd(), "cap.dat")))):
            with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.getcwd())):
                bu.cappath_config_writer()
        with mock.patch('bbarchivist.utilities.grab_cap',
                        mock.MagicMock(return_value=os.path.abspath(os.path.join(os.getcwd(), "cap.dat")))):
            with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.getcwd())):
                assert bu.cappath_config_loader() == os.path.join(os.getcwd(), "cap.dat")
