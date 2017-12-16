#!/usr/bin/env python3
"""Test the loadergen module."""

import os
import zipfile
from shutil import rmtree, copyfile
from hashlib import sha512
try:
    import unittest.mock as mock
except ImportError:
    import mock
import pytest
import bbarchivist.loadergen as bl
from bbarchivist.bbconstants import FLASHBAT, FLASHSH

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2017 Thurask"


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_loadergen"):
        os.mkdir("temp_loadergen")
    os.chdir("temp_loadergen")
    with open("cap-3.11.0.27.dat", "w") as targetfile:
        targetfile.write("0" * 9500000)


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_loadergen", ignore_errors=True)


class TestClassLoadergen:
    """
    Test autoloader generation.
    """

    def test_read_os_none(self):
        """
        Test finding OS filenames when there are no OS files.
        """
        assert set(bl.read_os_files(os.getcwd())) == {None}

    def test_read_radio_none(self):
        """
        Test finding radio filenames when there are no radio files.
        """
        assert set(bl.read_radio_files(os.getcwd())) == {None}

    def test_generate_lazy_loader(self):
        """
        Test creating one autoloader (lazyloader).
        """
        with open("desktop_sfi.signed", "w") as targetfile:
            targetfile.write("Jackdaws love my big sphinx of quartz" * 5000)
        with open("radio.signed", "w") as targetfile:
            targetfile.write("Why must I chase the cat?" * 5000)
        bl.generate_lazy_loader("TESTING", 0)
        shahash = sha512()
        with open("Z10_TESTING_STL100-1.exe", "rb") as targetfile:
            data = targetfile.read()
            shahash.update(data)
        thehash = shahash.hexdigest()
        os.remove("desktop_sfi.signed")
        os.remove("radio.signed")
        assert thehash == 'd4872a853e19fb8512067f50555827c74ec33da6fd5d71ae3ddd1b0ce98a18e01727eb1f345f476d6d59bcb438be8780e3f1dc7b212dc63b4b7c09914093a730'

    def test_generate_lazy_no_os(self, capsys):
        """
        Test creating one autoloader but no OS is given.
        """
        bl.generate_lazy_loader("TESTING", 0)
        assert "No OS found" in capsys.readouterr()[0]

    def test_generate_lazy_no_rad(self, capsys):
        """
        Test creating one autoloader but no radio is given.
        """
        with open("desktop_sfi.signed", "w") as targetfile:
            targetfile.write("Jackdaws love my big sphinx of quartz" * 5000)
        bl.generate_lazy_loader("TESTING", 0)
        assert "No radio found" in capsys.readouterr()[0]
        os.remove("desktop_sfi.signed")

    def test_generate_loaders(self):
        """
        Test creating multiple autoloaders (archivist).
        """
        with open("qc8960.factory_sfi.desktop.BB.signed", "w") as targetfile:
            targetfile.write("Jackdaws love my big sphinx of quartz" * 5000)
        copyfile("qc8960.factory_sfi.desktop.BB.signed", "qc8x30.factory_sfi.desktop.BB.signed")
        copyfile("qc8960.factory_sfi.desktop.BB.signed", "qc8974.factory_sfi.desktop.BB.signed")
        copyfile("qc8960.factory_sfi.desktop.BB.signed", "winchester.factory_sfi.desktop.BB.signed")
        with open("radio.m5730.signed", "w") as targetfile:
            targetfile.write("Why must I chase the cat?" * 5000)
        copyfile("radio.m5730.signed", "radio.qc8960.BB.signed")
        copyfile("radio.m5730.signed", "radio.qc8960.omadm.signed")
        copyfile("radio.m5730.signed", "radio.qc8960.wtr.signed")
        copyfile("radio.m5730.signed", "radio.qc8960.wtr5.signed")
        copyfile("radio.m5730.signed", "radio.qc8930.wtr5.signed")
        copyfile("radio.m5730.signed", "radio.qc8974.wtr2.signed")
        bl.generate_loaders("10.1.2.3000", "10.3.2.1000", True)
        for file in os.listdir():
            if file.endswith(".exe"):
                with open(file, 'rb') as filehandle:
                    shahash = sha512()
                    while True:
                        data = filehandle.read(16777216)
                        if not data:
                            break
                        shahash.update(data)
                    assert shahash.hexdigest() in (
                        "3143a5bdfffbab199fe071d720b374d8678e5a2baafaeaf375f747c578a314cdf10059ccfac51fbe992d6d473106c2ba18bb8a80026269b046c3e299c33adaf3",
                        "d4872a853e19fb8512067f50555827c74ec33da6fd5d71ae3ddd1b0ce98a18e01727eb1f345f476d6d59bcb438be8780e3f1dc7b212dc63b4b7c09914093a730")
        for item in os.listdir():
            if item.endswith("desktop.signed"):
                os.remove(item)

    def test_generate_cores(self):
        """
        Test creating multiple core autoloaders.
        """
        with open("qc8960.factory_sfi.BB.signed", "w") as targetfile:
            targetfile.write("Jackdaws love my big sphinx of quartz" * 5000)
        copyfile("qc8960.factory_sfi.BB.signed", "qc8x30.factory_sfi.BB.signed")
        copyfile("qc8960.factory_sfi.BB.signed", "qc8974.factory_sfi.BB.signed")
        copyfile("qc8960.factory_sfi.BB.signed", "winchester.factory_sfi.BB.signed")
        bl.generate_loaders("10.1.2.3000", "10.3.2.1000", True, core=True)
        for file in os.listdir():
            if file.endswith(".exe"):
                with open(file, 'rb') as filehandle:
                    shahash = sha512()
                    while True:
                        data = filehandle.read(16777216)
                        if not data:
                            break
                        shahash.update(data)
                    assert shahash.hexdigest() in (
                        "3143a5bdfffbab199fe071d720b374d8678e5a2baafaeaf375f747c578a314cdf10059ccfac51fbe992d6d473106c2ba18bb8a80026269b046c3e299c33adaf3",
                        "d4872a853e19fb8512067f50555827c74ec33da6fd5d71ae3ddd1b0ce98a18e01727eb1f345f476d6d59bcb438be8780e3f1dc7b212dc63b4b7c09914093a730")

    def test_filename_malformed(self):
        """
        Test filename creation if the device is imaginary.
        """
        assert bl.generate_filename(-1, "10.3.2.2789") is None

    def test_filename_nosuffix(self):
        """
        Test filename creation without suffix.
        """
        assert bl.generate_filename(0, "10.3.2.2789", None) == "Z10_10.3.2.2789_STL100-1.exe"

    def test_suffix_hybrid(self):
        """
        Test suffix formation, if hybrid radio is specified.
        """
        assert bl.format_suffix(True, "SUFFIX", True) == "_RSUFFIX_CORE"

    def test_pretty_formatter(self):
        """
        Test OS/radio version formatting.
        """
        assert bl.pretty_formatter("10.3.2.680", "10.3.2.681") == ("10.3.02.0680", "10.3.02.0681")

    def test_wrap_pseudocap_none(self):
        """
        Test wrapping pseudocap when no files are given.
        """
        with pytest.raises(SystemError):
            bl.wrap_pseudocap("filename.exe", os.getcwd(), None, None)

    def test_wrap_pseudocap_error(self, capsys):
        """
        Test wrapping pseudocap when an error is raised.
        """
        with mock.patch('bbarchivist.pseudocap.make_autoloader', mock.MagicMock(side_effect=IndexError)):
            bl.wrap_pseudocap("filename.exe", os.getcwd(), "qc8960.factory_sfi.signed", None)
            assert "Could not create" in capsys.readouterr()[0]


class TestClassLoadergenTcl:
    """
    Test Android autoloader generation.
    """

    @classmethod
    def setup_class(cls):
        """
        Create loader template file structure.
        """
        if not os.path.exists("autoloader-signed"):
            os.makedirs("autoloader-signed", exist_ok=True)
        verdir = os.path.abspath(os.path.join(os.getcwd(), "autoloader-signed"))
        os.makedirs(os.path.join(verdir, "host", "darwin-x86", "bin"), exist_ok=True)
        os.makedirs(os.path.join(verdir, "host", "linux-x86", "bin"), exist_ok=True)
        os.makedirs(os.path.join(verdir, "host", "windows-x86", "bin"), exist_ok=True)
        imgdir = os.path.join(verdir, "target", "product", "bbry_qc8953")
        os.makedirs(os.path.join(imgdir, "qcbc"), exist_ok=True)
        os.makedirs(os.path.join(imgdir, "sig"), exist_ok=True)
        with open("smack.dat", "w") as targetfile:
            targetfile.write("The quick brown fox jumps over the lazy dog")
        copyfile("smack.dat", os.path.join(verdir, "flashall.bat"))
        copyfile("smack.dat", os.path.join(verdir, "flashall.sh"))
        copyfile("smack.dat", os.path.join(verdir, "host", "linux-x86", "bin", "fastboot"))
        copyfile("smack.dat", os.path.join(verdir, "host", "darwin-x86", "bin", "fastboot"))
        copyfile("smack.dat", os.path.join(verdir, "host", "windows-x86", "bin", "AdbWinApi.dll"))
        copyfile("smack.dat", os.path.join(verdir, "host", "windows-x86", "bin", "AdbWinUsbApi.dll"))
        copyfile("smack.dat", os.path.join(verdir, "host", "windows-x86", "bin", "fastboot.exe"))
        imgs = ["oem_att", "oem_china", "oem_common", "oem_sprint", "oem_vzw", "recovery", "system", "userdata", "cache", "boot"]
        for img in imgs:
            copyfile("smack.dat", os.path.join(imgdir, "{0}.img".format(img)))
        radios = ["china", "emea", "global", "india", "japan", "usa"]
        for rad in radios:
            copyfile("smack.dat", os.path.join(imgdir, "NON-HLOS-{0}.bin".format(rad)))
        others = ["adspso.bin", "emmc_appsboot.mbn", "sbl1_signed.mbn"]
        for file in others:
            copyfile("smack.dat", os.path.join(imgdir, "{0}".format(file)))
        mbns = ["devcfg.mbn", "devcfg_cn.mbn", "rpm.mbn", "tz.mbn"]
        for mbn in mbns:
            copyfile("smack.dat", os.path.join(imgdir, "qcbc", mbn))
        sigs = ["boot.img.production.sig", "boot.img.production-sprint.sig", "recovery.img.production.sig", "recovery.img.production-sprint.sig"]
        for sig in sigs:
            copyfile("smack.dat", os.path.join(imgdir, "sig", sig))

    def test_tclloader_local(self):
        """
        Test generating loader from template, using local host files.
        """
        bl.generate_tclloader("autoloader-signed", "snek", "bbry_qc8953", localtools=True)
        os.remove(os.path.join("snek", "flashall.bat"))
        os.remove(os.path.join("snek", "flashall.sh"))
        copyfile("smack.dat", os.path.join("snek", "flashall.bat"))
        copyfile("smack.dat", os.path.join("snek", "flashall.sh"))
        with zipfile.ZipFile("snek.zip", 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zfile:
            for root, dirs, files in os.walk("snek"):
                for file in files:
                    abs_filename = os.path.join(root, file)
                    abs_arcname = abs_filename.replace("autoloader-signed{0}".format(os.sep), "")
                    zfile.write(abs_filename, abs_arcname)
        assert os.path.getsize("snek.zip") == 5754

    def test_tclloader_network(self):
        """
        Test generating loader from template, using downloaded host files.
        """
        platdir = os.path.abspath(os.path.join(os.getcwd(), "plattools"))
        os.makedirs(os.path.join(platdir, "darwin", "platform-tools"), exist_ok=True)
        os.makedirs(os.path.join(platdir, "linux", "platform-tools"), exist_ok=True)
        os.makedirs(os.path.join(platdir, "windows", "platform-tools"), exist_ok=True)
        copyfile("smack.dat", os.path.join(platdir, "darwin", "platform-tools", "fastboot"))
        copyfile("smack.dat", os.path.join(platdir, "linux", "platform-tools", "fastboot"))
        copyfile("smack.dat", os.path.join(platdir, "windows", "platform-tools", "AdbWinApi.dll"))
        copyfile("smack.dat", os.path.join(platdir, "windows", "platform-tools", "AdbWinUsbApi.dll"))
        copyfile("smack.dat", os.path.join(platdir, "windows", "platform-tools", "fastboot.exe"))
        bl.generate_tclloader("autoloader-signed", "snek2", "bbry_qc8953", localtools=False)
        os.remove(os.path.join("snek2", "flashall.bat"))
        os.remove(os.path.join("snek2", "flashall.sh"))
        copyfile("smack.dat", os.path.join("snek2", "flashall.bat"))
        copyfile("smack.dat", os.path.join("snek2", "flashall.sh"))
        with zipfile.ZipFile("snek2.zip", 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zfile:
            for root, dirs, files in os.walk("snek2"):
                for file in files:
                    abs_filename = os.path.join(root, file)
                    abs_arcname = abs_filename.replace("autoloader-signed{0}".format(os.sep), "")
                    zfile.write(abs_filename, abs_arcname)
        assert os.path.getsize("snek2.zip") == 5822

    def test_tclloader_nowipe(self):
        """
        Test modifying loader scripts.
        """
        if not os.path.exists("batcheck"):
            os.mkdir("batcheck")
        bl.generate_tclloader_script("batcheck", FLASHBAT.location, FLASHSH.location, False)
        assert os.path.getsize(os.path.join("batcheck", "flashall.bat")) == 2797
        assert os.path.getsize(os.path.join("batcheck", "flashall.sh")) == 2787

    def test_tclloader_deps(self):
        """
        Test handling platform dependencies.
        """
        oems, radios = bl.generate_tclloader_deps("bbry_qc8953krypton")
        assert "dsglobal" in radios

    def test_tclloader_ends(self):
        """
        Test handling loose ends.
        """
        if not os.path.exists("krypton"):
            os.mkdir("krypton")
        copyfile("smack.dat", os.path.join("krypton", "NON-HLOS-ssglobal.bin"))
        copyfile("smack.dat", os.path.join("krypton", "NON-HLOS-americas.bin"))
        bl.generate_tclloader_looseends("krypton", "bbry_qc8953krypton")
        assert sorted(os.listdir("krypton")) == ["NON-HLOS-americas.bin", "NON-HLOS-dsamericas.bin", "NON-HLOS-global.bin"]
