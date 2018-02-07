#!/usr/bin/env python3
"""Test the archiveutils module."""

import os
import tempfile
import zipfile
from shutil import copyfile, rmtree

import bbarchivist.archiveutils as ba
from bbarchivist.utilities import get_seven_zip, new_enough, prep_seven_zip

try:
    import unittest.mock as mock
except ImportError:
    import mock

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2018 Thurask"


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_archiveutils"):
        os.mkdir("temp_archiveutils")
    os.chdir("temp_archiveutils")
    with open("testfile.signed", "w") as targetfile:
        targetfile.write("Jackdaws love my big sphinx of quartz")
    with open("Z10_BIGLOADER.exe", "w") as targetfile:
        targetfile.write("0" * 95000000)
    if os.path.exists("a_temp_folder"):
        rmtree("a_temp_folder")
    os.mkdir("a_temp_folder")
    if os.path.exists("loader_folder"):
        rmtree("loader_folder")
    os.mkdir("loader_folder")
    with open(os.path.join("loader_folder", "snek.txt"), "w") as afile:
        afile.write("The quick brown fox jumps over the lazy dog")


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_archiveutils", ignore_errors=True)


class TestClassArchiveutilsStrength:
    """
    Test strength calculation.
    """
    def test_calculate_strength_32(self):
        """
        Test compression strength for 32-bit systems.
        """
        with mock.patch('bbarchivist.utilities.is_amd64', mock.MagicMock(return_value=False)):
            assert ba.calculate_strength() == 5

    def test_calculate_strength_64(self):
        """
        Test compression strength for 64-bit systems.
        """
        with mock.patch('bbarchivist.utilities.is_amd64', mock.MagicMock(return_value=True)):
            assert ba.calculate_strength() == 9


class TestClassArchiveutilsCompression:
    """
    Test file compression.
    """

    def test_compress_sz(self):
        """
        Test 7z compression.
        """
        exists = prep_seven_zip()
        if exists:
            szexe = get_seven_zip(False)
            ba.compress(os.getcwd(), method="7z", szexe=szexe)
            result = ba.sz_verify("Z10_BIGLOADER.7z", szexe)
            if os.path.exists("Z10_BIGLOADER.7z"):
                os.remove("Z10_BIGLOADER.7z")
            assert result
        else:
            pass

    def test_compress_sz_fail(self, capsys):
        """
        Test 7z compresssion failure.
        """
        exists = prep_seven_zip()
        if exists:
            szexe = get_seven_zip(False)
            with mock.patch("subprocess.call", mock.MagicMock(return_value=2)):
                ba.sz_compress(os.getcwd(), "7z", szexe=szexe, errors=True)
                assert "FATAL ERROR" in capsys.readouterr()[0]
        else:
            pass

    def test_compress_tcl_sz(self):
        """
        Test 7z compression for Android autoloaders.
        """
        exists = prep_seven_zip()
        if exists:
            szexe = get_seven_zip(False)
            ba.pack_tclloader("loader_folder", "snek")
            result = ba.sz_verify("snek.7z", szexe)
            if os.path.exists("snek.7z"):
                os.remove("snek.7z")
            assert result
        else:
            pass

    def test_compress_zip(self):
        """
        Test zip compression.
        """
        ba.compress(os.getcwd(), "zip")
        assert ba.zip_verify("Z10_BIGLOADER.zip")

    def test_compress_tcl_zip(self):
        """
        Test zip compression for Android autoloaders.
        """
        with mock.patch('bbarchivist.utilities.prep_seven_zip', mock.MagicMock(return_value=False)):
            ba.pack_tclloader("loader_folder", "snek")
        assert ba.zip_verify("snek.zip")
        if os.path.exists("snek.zip"):
            os.remove("snek.zip")

    def test_compress_zip_fail(self):
        """
        Test zip compression failure.
        """
        with mock.patch("zipfile.ZipFile.testzip", mock.MagicMock(return_value="Z10_BIGLOADER.zip")):
            assert not ba.zip_verify("Z10_BIGLOADER.zip")

    def test_compress_tar(self):
        """
        Test tar packing.
        """
        ba.compress(os.getcwd(), "tar")
        assert ba.tar_verify("Z10_BIGLOADER.tar")
        if os.path.exists("Z10_BIGLOADER.tar"):
            os.remove("Z10_BIGLOADER.tar")

    def test_compress_tar_fail(self):
        """
        Test tar packing failure.
        """
        with mock.patch("tarfile.TarFile.getmembers", mock.MagicMock(return_value=False)):
            assert not ba.tar_verify("Z10_BIGLOADER.tar")

    def test_compress_gzip(self):
        """
        Test gzip compression.
        """
        ba.compress(os.getcwd(), "tgz")
        assert ba.tgz_verify("Z10_BIGLOADER.tar.gz")
        if os.path.exists("Z10_BIGLOADER.tar.gz"):
            os.remove("Z10_BIGLOADER.tar.gz")

    def test_compress_gzip_fail(self):
        """
        Test gzip compression failure.
        """
        with mock.patch("tarfile.TarFile.getmembers", mock.MagicMock(return_value=False)):
            assert not ba.tgz_verify("Z10_BIGLOADER.tar.gz")

    def test_compress_bz2(self):
        """
        Test bz2 compression.
        """
        ba.compress(os.getcwd(), "tbz")
        assert ba.tbz_verify("Z10_BIGLOADER.tar.bz2")
        if os.path.exists("Z10_BIGLOADER.tar.bz2"):
            os.remove("Z10_BIGLOADER.tar.bz2")

    def test_compress_bz2_fail(self):
        """
        Test bz2 compression failure.
        """
        with mock.patch("tarfile.TarFile.getmembers", mock.MagicMock(return_value=False)):
            assert not ba.tbz_verify("Z10_BIGLOADER.tar.bz2")

    def test_compress_lzma(self):
        """
        Test xz compression.
        """
        if not new_enough(3):
            pass
        else:
            ba.compress(os.getcwd(), "txz")
            assert ba.txz_verify("Z10_BIGLOADER.tar.xz")
            if os.path.exists("Z10_BIGLOADER.tar.xz"):
                os.remove("Z10_BIGLOADER.tar.xz")

    def test_compress_lzma_fail(self):
        """
        Test xz compression failure.
        """
        if not new_enough(3):
            pass
        else:
            with mock.patch("tarfile.TarFile.getmembers", mock.MagicMock(return_value=False)):
                assert not ba.txz_verify("Z10_BIGLOADER.tar.xz")

    def test_compress_lzma_mocked(self):
        """
        Test xz compression failure, if we insist this is Python 3.2.
        """
        with mock.patch('bbarchivist.utilities.new_enough', mock.MagicMock(return_value=False)):
            ba.txz_compress("Z10_BIGLOADER2", "Z10_BIGLOADER.exe")
            assert True

    def test_verify(self):
        """
        Test bulk verification.
        """
        with tempfile.TemporaryDirectory() as tempdir:
            suitedir = os.path.abspath(tempdir)
            with open(os.path.join(suitedir, "Z10.exe"), "w") as afile:
                afile.write("Haters gonna hate")
            with open(os.path.join(suitedir, "Z30.exe"), "w") as afile:
                afile.write("I'm just gonna shake")
            ba.compress(suitedir, "zip", None, True)
            ba.verify(suitedir, "zip", None, True)

    def test_compressfilter_none(self):
        """
        Test "filtering", i.e. not actually filtering anything.
        """
        fileshere = [os.path.abspath(x) for x in os.listdir(os.getcwd())]
        cfit = ba.compressfilter(os.getcwd(), None)
        assert sorted(cfit) == sorted(fileshere)

    def test_compressfilter_arcsonly(self):
        """
        Test filtering for archives only.
        """
        with open("compfilter.zip", "w") as targetfile:
            targetfile.write("Jackdaws love my big sphinx of quartz")
        fileshere = [os.path.abspath("compfilter.zip")]
        if "Z10_BIGLOADER.zip" in os.listdir(os.getcwd()):
            fileshere.append(os.path.abspath("Z10_BIGLOADER.zip"))
        if "testfile.7z" in os.listdir(os.getcwd()):
            fileshere.append(os.path.abspath("testfile.7z"))
        if "testfile.tar" in os.listdir(os.getcwd()):
            fileshere.append(os.path.abspath("testfile.tar"))
        if "testfile.tar.bz2" in os.listdir(os.getcwd()):
            fileshere.append(os.path.abspath("testfile.tar.bz2"))
        if "testfile.tar.gz" in os.listdir(os.getcwd()):
            fileshere.append(os.path.abspath("testfile.tar.gz"))
        if "testfile.tar.xz" in os.listdir(os.getcwd()):
            fileshere.append(os.path.abspath("testfile.tar.xz"))
        if "testfile.zip" in os.listdir(os.getcwd()):
            fileshere.append(os.path.abspath("testfile.zip"))
        cfit = ba.compressfilter(os.getcwd(), "arcsonly")
        assert sorted(cfit) == sorted(fileshere)
        if os.path.exists("compfilter.zip"):
            os.remove("compfilter.zip")


class TestClassArchiveutilsMethods:
    """
    Test method filtering.
    """

    def test_filter_method_null(self):
        """
        Test method checking, null case.
        """
        assert ba.filter_method("tbz", None) == "tbz"

    def test_filter_method_good(self):
        """
        Test method checking, best case.
        """
        with mock.patch('bbarchivist.utilities.prep_seven_zip', mock.MagicMock(return_value=False)):
            assert ba.filter_method("7z", "7za") == "7z"

    def test_filter_method_bad(self):
        """
        Test method checking, worst case.
        """
        with mock.patch('bbarchivist.utilities.prep_seven_zip', mock.MagicMock(return_value=False)):
            assert ba.filter_method("7z", None) == "zip"

    def test_filter_method_ok(self):
        """
        Test method checking, middle case.
        """
        with mock.patch('bbarchivist.utilities.prep_seven_zip', mock.MagicMock(return_value=True)):
            with mock.patch('bbarchivist.utilities.get_seven_zip', mock.MagicMock(return_value='7za')):
                assert ba.filter_method("7z", None) == "7z"

    def test_filter_method_legacy(self):
        """
        Test method checking, Python 3.2.
        """
        if new_enough(3):
            pass
        else:
            assert ba.filter_method("txz", None) == "zip"

    def test_filter_method_mocked(self):
        """
        Test method checking, if we insist this is Python 3.2.
        """
        with mock.patch('bbarchivist.utilities.new_enough', mock.MagicMock(return_value=False)):
            assert ba.filter_method("txz", None) == "zip"


class TestClassArchiveutilsSmartTarfile:
    """
    Test verification that a file is a valid tar.xxx file.
    """
    def test_is_tarfile(self):
        """
        Test if a file is a tar.xxx file.
        """
        with mock.patch('tarfile.is_tarfile', mock.MagicMock(return_value=True)):
            assert ba.smart_is_tarfile("BADTAR.tar")

    def test_is_tarfile_fail(self):
        """
        Test if a file is not a tar.xxx file.
        """
        with mock.patch('tarfile.is_tarfile', mock.MagicMock(return_value=False)):
            assert not ba.smart_is_tarfile("BADTAR.tar")

    def test_is_tarfile_except(self):
        """
        Test if a file raises an exception when checking.
        """
        with mock.patch('tarfile.is_tarfile', mock.MagicMock(side_effect=OSError)):
            assert not ba.smart_is_tarfile("BADTAR.tar")


class TestClassArchiveutilsVerifier:
    """
    Test verification of archives.
    """
    @classmethod
    def setup_class(cls):
        """
        Create compressed loaders to verify.
        """
        if not os.path.exists("verifiers"):
            os.makedirs("verifiers", exist_ok=True)
        verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
        aloader = os.path.join(verdir, "Q10.exe")
        with open(aloader, "w") as afile:
            afile.write("Haters gonna hate")

    def test_verify_sz(self):
        """
        Test 7z verification.
        """
        with mock.patch('subprocess.call', mock.MagicMock(return_value=0)):
            verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
            filepath = os.path.join(verdir, "Q10.7z")
            exists = prep_seven_zip()
            if not exists:
                pass
            else:
                szexe = get_seven_zip(False)
                if not os.path.exists("Q10.7z"):
                    ba.compress(verdir, "7z", szexe, True)
                assert ba.sz_verify(filepath, szexe)

    def test_verify_sz_fail(self):
        """
        Test 7z verification failure.
        """
        with mock.patch('subprocess.call', mock.MagicMock(return_value=255)):
            verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
            filepath = os.path.join(verdir, "Q10.7z")
            exists = prep_seven_zip()
            if not exists:
                pass
            else:
                szexe = get_seven_zip(False)
                assert not ba.sz_verify(filepath, szexe)

    def test_verify_zip(self):
        """
        Test zip verification.
        """
        verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
        if not os.path.exists("Q10.zip"):
            ba.compress(verdir, "zip", None, True)
        filepath = os.path.join(verdir, "Q10.zip")
        smeg = ba.zip_verify(filepath)
        assert smeg

    def test_verify_zip_fail(self):
        """
        Test zip verification failure.
        """
        with mock.patch('zipfile.is_zipfile', mock.MagicMock(return_value=False)):
            verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
            filepath = os.path.join(verdir, "Q10.zip")
            assert not ba.zip_verify(filepath)

    def test_verify_zip_fail2(self):
        """
        Test zip verification failure, different reason.
        """
        verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
        filepath = os.path.join(verdir, "Q10.zip")
        with mock.patch('zipfile.ZipFile.testzip', mock.MagicMock(return_value=filepath)):
            assert not ba.zip_verify(filepath)

    def test_verify_tgz(self):
        """
        Test tar.gz verification.
        """
        verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
        if not os.path.exists("Q10.tar.gz"):
            ba.compress(verdir, "tgz", None, True)
        filepath = os.path.join(verdir, "Q10.tar.gz")
        assert ba.tgz_verify(filepath)

    def test_verify_tgz_fail(self):
        """
        Test tar.gz verification failure.
        """
        with mock.patch('bbarchivist.archiveutils.smart_is_tarfile', mock.MagicMock(return_value=False)):
            verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
            filepath = os.path.join(verdir, "Q10.tar.gz")
            assert not ba.tgz_verify(filepath)

    def test_verify_tbz(self):
        """
        Test tar.bz2 verification.
        """
        verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
        if not os.path.exists("Q10.tar.bz2"):
            ba.compress(verdir, "tbz", None, True)
        filepath = os.path.join(verdir, "Q10.tar.bz2")
        assert ba.tbz_verify(filepath)

    def test_verify_tbz_fail(self):
        """
        Test tar.bz2 verification failure.
        """
        with mock.patch('bbarchivist.archiveutils.smart_is_tarfile', mock.MagicMock(return_value=False)):
            verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
            filepath = os.path.join(verdir, "Q10.tar.bz2")
            assert not ba.tbz_verify(filepath)

    def test_verify_txz(self):
        """
        Test tar.xz verification.
        """
        if not new_enough(3):
            pass
        else:
            verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
            if not os.path.exists("Q10.tar.xz"):
                ba.compress(verdir, "txz", None, True)
            filepath = os.path.join(verdir, "Q10.tar.xz")
            assert ba.txz_verify(filepath)

    def test_verify_txz_fail(self):
        """
        Test tar.xz verification failure.
        """
        if not new_enough(3):
            pass
        else:
            with mock.patch('bbarchivist.archiveutils.smart_is_tarfile', mock.MagicMock(return_value=False)):
                verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
                filepath = os.path.join(verdir, "Q10.tar.xz")
                assert not ba.txz_verify(filepath)

    def test_verify_txz_mocked(self):
        """
        Test tar.xz verification failure, if we insist this is Python 3.2.
        """
        with mock.patch('bbarchivist.utilities.new_enough', mock.MagicMock(return_value=False)):
            verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
            filepath = os.path.join(verdir, "Q10.tar.xz")
            assert ba.txz_verify(filepath) is None

    def test_verify_printer_ok(self, capsys):
        """
        Test reporting if file is OK.
        """
        ba.decide_verifier_printer("SNEK.snek", True)
        assert "SNEK.snek OK" in capsys.readouterr()[0]

    def test_verify_assignment(self):
        """
        Test assigning verifier functions.
        """
        with mock.patch('bbarchivist.archiveutils.zip_verify', mock.MagicMock(return_value=True)):
            assert ba.tarzip_verifier("snek.zip")

    def test_verify_decide_sz(self):
        """
        Test checking 7-Zip verification.
        """
        with mock.patch('bbarchivist.archiveutils.sz_verify', mock.MagicMock(return_value=True)):
            assert ba.decide_verifier("snek.7z", "7z.exe")


class TestClassArchiveutilsConfig:
    """
    Test reading/writing configs with ConfigParser.
    """

    def test_compress_loader(self):
        """
        Test reading compression settings.
        """
        try:
            os.remove("bbarchivist.ini")
        except (OSError, IOError):
            pass
        with mock.patch('bbarchivist.iniconfig.config_homepath', mock.MagicMock(return_value=os.getcwd())):
            assert ba.compress_config_loader(os.getcwd()) == "7z"

    def test_compress_loader_legacy(self):
        """
        Test reading compression settings, Python 3.2.
        """
        if new_enough(3):
            pass
        else:
            try:
                os.remove("bbarchivist.ini")
            except (OSError, IOError):
                pass
            with mock.patch('bbarchivist.iniconfig.config_homepath', mock.MagicMock(return_value=os.getcwd())):
                ba.compress_config_writer("txz")
                print(ba.compress_config_loader())
                assert ba.compress_config_loader(os.getcwd()) == "zip"

    def test_compress_loader_mocked(self):
        """
        Test reading compression settings, forced Python 3.2.
        """
        with mock.patch('bbarchivist.utilities.new_enough', mock.MagicMock(return_value=False)):
            try:
                os.remove("bbarchivist.ini")
            except (OSError, IOError):
                pass
            with mock.patch('bbarchivist.iniconfig.config_homepath', mock.MagicMock(return_value=os.getcwd())):
                ba.compress_config_writer("txz")
                print(ba.compress_config_loader())
                assert ba.compress_config_loader(os.getcwd()) == "zip"

    def test_compress_writer(self):
        """
        Test writing compression settings.
        """
        try:
            os.remove("bbarchivist.ini")
        except (OSError, IOError):
            pass
        with mock.patch('bbarchivist.iniconfig.config_homepath', mock.MagicMock(return_value=os.getcwd())):
            with mock.patch('bbarchivist.archiveutils.compress_config_loader', mock.MagicMock(return_value="tbz")):
                ba.compress_config_writer()
            assert ba.compress_config_loader() == "tbz"

class TestClassArchiveutils:
    """
    Test miscellaneous tools.
    """

    @classmethod
    def setup_class(cls):
        """
        Create loader template file structure.
        """
        if not os.path.exists("tooldir"):
            os.mkdir("tooldir")
        with zipfile.ZipFile(os.path.join("tooldir", "platform-tools-latest-linux.zip"), mode="w", compression=zipfile.ZIP_DEFLATED) as zfile:
            zfile.writestr("snek", b"Jackdaws love my big sphinx of quartz")
        copyfile(os.path.join("tooldir", "platform-tools-latest-linux.zip"), os.path.join("tooldir", "platform-tools-latest-darwin.zip"))
        copyfile(os.path.join("tooldir", "platform-tools-latest-linux.zip"), os.path.join("tooldir", "platform-tools-latest-windows.zip"))

    def test_android_tools(self):
        """
        Test Android SDK platform tools utilities.
        """
        ba.verify_android_tools("tooldir")
        ba.extract_android_tools("tooldir")


    def test_android_tools_fail(self):
        """
        Test when verification fails.
        """
        with mock.patch('bbarchivist.archiveutils.zip_verify', mock.MagicMock(return_value=False)):
            assert not ba.verify_android_tools("tooldir")
