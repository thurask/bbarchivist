#!/usr/bin/env python3
"""Test the loadergentcl module."""

import os
import zipfile
from shutil import copyfile, rmtree

import bbarchivist.bbconstants as bc
import bbarchivist.loadergentcl as bl


__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2018 Thurask"


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_loadergentcl"):
        os.mkdir("temp_loadergentcl")
    os.chdir("temp_loadergentcl")


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_loadergentcl", ignore_errors=True)


class TestClassLoadergentcl:
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
            for root, _, files in os.walk("snek"):
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
            for root, _, files in os.walk("snek2"):
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
        bl.generate_tclloader_script("batcheck", bc.FLASHBAT.location, bc.FLASHSH.location, False)
        assert os.path.getsize(os.path.join("batcheck", "flashall.bat")) == 2846
        assert os.path.getsize(os.path.join("batcheck", "flashall.sh")) == 2856

    def test_tclloader_deps(self):
        """
        Test handling platform dependencies.
        """
        oems, radios = bl.generate_tclloader_deps("bbry_qc8953krypton")
        oems2, radios2 = bl.generate_tclloader_deps("bbry_sdm660")
        del oems, oems2
        assert "dsglobal" in radios
        assert "dsjapan" in radios2

    def test_tclloader_ends(self):
        """
        Test handling loose ends.
        """
        if not os.path.exists("krypton"):
            os.mkdir("krypton")
        copyfile("smack.dat", os.path.join("krypton", "NON-HLOS-ssglobal.bin"))
        copyfile("smack.dat", os.path.join("krypton", "NON-HLOS-americas.bin"))
        bl.generate_tclloader_looseends("krypton", "bbry_qc8953krypton")
        bl.generate_tclloader_looseends("krypton", "bbry_sdm660")
        assert sorted(os.listdir("krypton")) == ["NON-HLOS-americas.bin", "NON-HLOS-dsamericas.bin", "NON-HLOS-global.bin"]
