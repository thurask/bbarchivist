#!/usr/bin/env python3
"""Test the hashutils module."""

from shutil import rmtree, copyfile
from hashlib import algorithms_available as algos
from configparser import ConfigParser
import os
try:
    import unittest.mock as mock
except ImportError:
    import mock
import pytest
try:
    import gnupg
except ImportError:
    NOGNUPG = True
else:
    NOGNUPG = False
from bbarchivist import hashutils as bh

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_hashutils"):
        os.mkdir("temp_hashutils")
    os.chdir("temp_hashutils")
    with open("tempfile.txt", "w") as targetfile:
        targetfile.write("Jackdaws love my big sphinx of quartz")
    os.mkdir("skipme")


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_hashutils", ignore_errors=True)


class TestClasshashutils:
    """
    Test hash/GnuPG utilities.
    """

    def test_crc32(self):
        """
        Test CRC32 checksum.
        """
        assert bh.hc32("tempfile.txt") == "ed5d3f26"

    def test_adler32(self):
        """
        Test Adler32 checksum.
        """
        assert bh.ha32("tempfile.txt") == "02470dcd"

    def test_sha0(self):
        """
        Test SHA-0 hash.
        """
        if "sha" not in algos:
            pass
        else:
            assert bh.hs0("tempfile.txt") == "d26b25f6170daf49e31e68bf57f6164815c368d8"

    def test_sha0_unavail(self, capsys):
        """
        Test SHA-0 hash, if not available.
        """
        with mock.patch("hashlib.new", mock.MagicMock(side_effect=ValueError)):
            bh.hs0("tempfile.txt")
            assert "SHA HASH FAILED" in capsys.readouterr()[0]

    def test_sha1(self):
        """
        Test SHA-1 hash.
        """
        assert bh.hs1("tempfile.txt") == "71dc7ce8f27c11b792be3f169ecf985865e276d0"

    def test_sha224(self):
        """
        Test SHA-224 hash.
        """
        assert bh.hs224(
            "tempfile.txt") == "7bcd7b77f63633bf0f7db181106f08eb630a58c521b109be1cc4a404"

    def test_sha256(self):
        """
        Test SHA-256 hash.
        """
        assert bh.hs256(
            "tempfile.txt") == "f118871c45171d5fe4e9049980959e033eeeabcfa12046c243fda310580e8a0b"

    def test_sha384(self):
        """
        Test SHA-384 hash.
        """
        assert bh.hs384(
            "tempfile.txt") == "76620873c0d27873c137b082425c6e87e3d601c4b19241a1f2222f7f700a2fe8d3c648b26f62325a411cb020bff527be"

    def test_sha512(self):
        """
        Test SHA-512 hash.
        """
        assert bh.hs512(
            "tempfile.txt") == "b66a5e8aa9b9705748c2ee585b0e1a3a41288d2dafc3be2db12fa89d2f2a3e14f9dec11de4ba865bb51eaa6c2cfeb294139455e34da7d827a19504b0906c01c1"

    def test_md4(self):
        """
        Test MD4 hash.
        """
        if "md4" not in algos:
            pass
        else:
            assert bh.hm4("tempfile.txt") == "df26ada1a895f94e1f1257fad984e809"

    def test_md4_unavail(self, capsys):
        """
        Test MD4 hash, if not available.
        """
        with mock.patch("hashlib.new", mock.MagicMock(side_effect=ValueError)):
            bh.hm4("tempfile.txt")
            assert "MD4 HASH FAILED" in capsys.readouterr()[0]

    def test_md5(self):
        """
        Test MD5 hash.
        """
        assert bh.hm5("tempfile.txt") == "822e1187fde7c8d55aff8cc688701650"

    def test_ripemd160(self):
        """
        Test RIPEMD160 hash.
        """
        if "ripemd160" not in algos:
            pass
        else:
            assert bh.hr160("tempfile.txt") == "f3e191024c33768e2589e2efca53d55f4e4945ee"

    def test_ripemd160_unavail(self, capsys):
        """
        Test RIPEMD160 hash, if not available.
        """
        with mock.patch("hashlib.new", mock.MagicMock(side_effect=ValueError)):
            bh.hr160("tempfile.txt")
            assert "RIPEMD160 HASH FAILED" in capsys.readouterr()[0]

    def test_whirlpool(self):
        """
        Test Whirlpool hash.
        """
        if "whirlpool" not in algos:
            pass
        else:
            assert bh.hwp(
                "tempfile.txt") == "9835d12f3cb3ea3934635e4a7cc918e489379ed69d894ebc2c09bbf99fe72567bfd26c919ad666e170752abfc4b8c37b376f5102f9e5de59af2b65efc2e01293"

    def test_whirlpool_unavail(self, capsys):
        """
        Test Whirlpool hash, if not available.
        """
        with mock.patch("hashlib.new", mock.MagicMock(side_effect=ValueError)):
            bh.hwp("tempfile.txt")
            assert "WHIRLPOOL HASH FAILED" in capsys.readouterr()[0]

    def test_escreens(self):
        """
        Test EScreens code generation.
        """
        pin = "acdcacdc"
        app = "10.3.2.500"
        uptime = "69696969"
        assert bh.calculate_escreens(pin, app, uptime, duration=2) == "E4A25067"

    def test_verifier(self):
        """
        Test batch hashing.
        """
        confload = {}
        confload['adler32'] = True
        confload['crc32'] = True
        confload['md4'] = True if "md4" in algos else False
        confload['md5'] = True
        confload['sha0'] = True if "sha" in algos else False
        confload['sha1'] = True
        confload['sha224'] = True
        confload['sha256'] = True
        confload['sha384'] = True
        confload['sha512'] = True
        confload['ripemd160'] = True if "ripemd160" in algos else False
        confload['whirlpool'] = True if "whirlpool" in algos else False
        confload['blocksize'] = "16777216"
        print(confload)
        with mock.patch('bbarchivist.hashutils.verifier_config_loader', mock.MagicMock(return_value=confload)):
            bh.verifier(os.getcwd())
        stocklines = [
            b"ADLER32",
            b"02470DCD tempfile.txt",
            b"CRC32",
            b"ED5D3F26 tempfile.txt"]
        if confload["md4"]:
            stocklines.extend([
            b"MD4",
            b"DF26ADA1A895F94E1F1257FAD984E809 tempfile.txt"])
        stocklines.extend([
            b"MD5",
            b"822E1187FDE7C8D55AFF8CC688701650 tempfile.txt"])
        if confload["sha0"]:
            stocklines.extend([
            b"SHA0",
            b"D26B25F6170DAF49E31E68BF57F6164815C368D8 tempfile.txt"])
        stocklines.extend([
            b"SHA1",
            b"71DC7CE8F27C11B792BE3F169ECF985865E276D0 tempfile.txt",
            b"SHA224",
            b"7BCD7B77F63633BF0F7DB181106F08EB630A58C521B109BE1CC4A404 tempfile.txt",
            b"SHA256",
            b"F118871C45171D5FE4E9049980959E033EEEABCFA12046C243FDA310580E8A0B tempfile.txt",
            b"SHA384",
            b"76620873C0D27873C137B082425C6E87E3D601C4B19241A1F2222F7F700A2FE8D3C648B26F62325A411CB020BFF527BE tempfile.txt",
            b"SHA512",
            b"B66A5E8AA9B9705748C2EE585B0E1A3A41288D2DAFC3BE2DB12FA89D2F2A3E14F9DEC11DE4BA865BB51EAA6C2CFEB294139455E34DA7D827A19504B0906C01C1 tempfile.txt"])
        if confload["ripemd160"]:
            stocklines.extend([
            b"RIPEMD160",
            b"F3E191024C33768E2589E2EFCA53D55F4E4945EE tempfile.txt"])
        if confload["whirlpool"]:
            stocklines.extend([
                b"WHIRLPOOL",
                b"9835D12F3CB3EA3934635E4A7CC918E489379ED69D894EBC2C09BBF99FE72567BFD26C919AD666E170752ABFC4B8C37B376F5102F9E5DE59AF2B65EFC2E01293 tempfile.txt"])
        stocklines2 = []
        for item in stocklines:
            item2 = item.strip()
            item2 = item2.replace(b'\r\n', b'')
            item2 = item2.replace(b'\n', b'')
            item2 = item2.replace(b'\r', b'')
            stocklines2.append(item2)
        filename = "tempfile.txt.cksum"
        with open(filename, "rb") as checksumfile:
            content = checksumfile.read().splitlines()
        content2 = []
        for item in content:
            item2 = item.strip()
            item2 = item2.replace(b'\r\n', b'')
            item2 = item2.replace(b'\n', b'')
            item2 = item2.replace(b'\r', b'')
            content2.append(item2)
        for idx, value in enumerate(content2):
            assert stocklines2[idx] == value

    def test_verifier_multiple(self):
        """
        Test batch hashing, but with multiple files.
        """
        for i in range(17):
            copyfile("tempfile.txt", "tempfile{0}.txt".format(i))
        self.test_verifier()

    def test_verifier_fail(self, capsys):
        """
        Test batch hashing failure.
        """
        with mock.patch("concurrent.futures.ThreadPoolExecutor.submit", mock.MagicMock(side_effect=Exception)):
            with pytest.raises(SystemExit):
                bh.verifier(os.getcwd())
                assert "SOMETHING WENT WRONG" in capsys.readouterr()[0]


class GPGFileMock(object):
    """Mock a gnupg.GPG instance."""

    def sign_file(self, file, detach, keyid, passphrase, output):
        """
        "Sign a file".
        """
        print("MOCKED!")


class TestClasshashutilsGPG:
    """
    Test GPG-related tools.
    """

    def test_gpgfile(self, capsys):
        """
        Test GnuPG signing.
        """
        envs = (os.getenv("TRAVIS", "false"), os.getenv("APPVEYOR", "false"))
        if any(env for env in envs if env == "true"):
            gpginst = GPGFileMock()
            bh.gpgfile("tempfile.txt", gpginst, "asdasdad", "hunter2")
            assert "MOCKED!" in capsys.readouterr()[0]
        elif NOGNUPG:
            pass
        else:
            gpgkey, gpgpass = bh.gpg_config_loader()
            if gpgkey is None or gpgpass is None:
                pass
            else:
                gpginst = gnupg.GPG()
                # Note: if you get a "Unknown status message 'NEWSIG'" error, then look here:
                # https://bitbucket.org/vinay.sajip/python-gnupg/issues/35/status-newsig-missing-in-verify
                bh.gpgfile("tempfile.txt", gpginst, gpgkey, gpgpass)
                with open("tempfile.txt.asc", "rb") as sig:
                    try:
                        verified = gpginst.verify_file(sig, 'tempfile.txt')
                    except ValueError as exc:
                        rep = str(exc)
                        if "NEWSIG" not in rep:
                            print(rep)
                        else:
                            pass
                    else:
                        assert verified

    def test_gpgrunner(self):
        """
        Test batch GnuPG signing.
        """
        envs = (os.getenv("TRAVIS", "false"), os.getenv("APPVEYOR", "false"))
        if any(env for env in envs if env == "true"):
            pass
        elif NOGNUPG:
            pass
        else:
            gpgkey, gpgpass = bh.gpg_config_loader()
            if gpgkey is None or gpgpass is None:
                pass
            else:
                gpginst = gnupg.GPG()
                bh.gpgrunner(os.getcwd(), gpgkey, gpgpass, False)
                with open("tempfile.txt.asc", "rb") as sig:
                    try:
                        verified = gpginst.verify_file(sig, 'tempfile.txt')
                    except ValueError as exc:
                        rep = str(exc)
                        if "NEWSIG" not in rep:
                            print(rep)
                        else:
                            pass
                    else:
                        assert verified

    def test_gpgrunner_single(self):
        """
        Test GPGRunner, but with just one file (ThreadPoolExecutor worker count).
        """
        for file in os.listdir():
            if any(char.isdigit() for char in file):
                os.remove(file)
        self.test_gpgrunner()

    def test_gpgrunner_unavail(self, capsys):
        """
        Test GPGRunner raising ValueError, i.e. GnuPG not found.
        """
        with mock.patch("gnupg.GPG", mock.MagicMock(side_effect=ValueError)):
            with pytest.raises(SystemExit):
                bh.gpgrunner(os.getcwd(), "12345678", "hunter2", False)
                assert "COULD NOT FIND GnuPG" in capsys.readouterr()[0]

    def test_gpgrunner_failure(self, capsys):
        """
        Test GPGRunner going wrong during the process.
        """
        envs = (os.getenv("TRAVIS", "false"), os.getenv("APPVEYOR", "false"))
        if any(env for env in envs if env == "true"):
            pass
        elif NOGNUPG:
            pass
        else:
            with mock.patch("concurrent.futures.ThreadPoolExecutor.submit", mock.MagicMock(side_effect=Exception)):
                with pytest.raises(SystemExit):
                    bh.gpgrunner(os.getcwd(), "12345678", "hunter2", False)
                    assert "SOMETHING WENT WRONG" in capsys.readouterr()[0]


class TestClasshashutilsConfig:
    """
    Test reading/writing configs with ConfigParser.
    """
    @classmethod
    def setup_class(cls):
        """
        Create dictionaries for self.
        """
        cls.hashdict = {}
        cls.hashdict['crc32'] = False
        cls.hashdict['adler32'] = False
        cls.hashdict['sha1'] = True
        cls.hashdict['sha224'] = False
        cls.hashdict['sha256'] = True
        cls.hashdict['sha384'] = False
        cls.hashdict['sha512'] = False
        cls.hashdict['md5'] = True
        cls.hashdict['md4'] = False
        cls.hashdict['ripemd160'] = False
        cls.hashdict['whirlpool'] = False
        cls.hashdict['sha0'] = False
        cls.hashdict['blocksize'] = 16777216

    def test_hash_loader(self):
        """
        Test reading hash settings.
        """
        try:
            os.remove("bbarchivist.ini")
        except (OSError, IOError):
            pass
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.getcwd())):
            assert bh.verifier_config_loader() == self.hashdict

    def test_hash_writer(self):
        """
        Test writing hash settings.
        """
        hash2 = self.hashdict
        hash2['sha512'] = True
        try:
            os.remove("bbarchivist.ini")
        except (OSError, IOError):
            pass
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.getcwd())):
            with mock.patch('bbarchivist.hashutils.verifier_config_loader',
                            mock.MagicMock(return_value=hash2)):
                bh.verifier_config_writer()
            assert bh.verifier_config_loader() == hash2

    def test_gpg_loader_empty(self):
        """
        Test reading GPG settings on empty.
        """
        try:
            os.remove("bbarchivist.ini")
        except (OSError, IOError):
            pass
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.getcwd())):
            assert bh.gpg_config_loader() == (None, None)

    def test_gpg_loader_loaded(self):
        """
        Test reading GPG settings when completed.
        """
        config = ConfigParser()
        open("bbarchivist.ini", 'w').close()
        config.read("bbarchivist.ini")
        config['gpgrunner'] = {}
        config['gpgrunner']['key'] = "0xDEADBEEF"
        config['gpgrunner']['pass'] = "hunter2"
        with open("bbarchivist.ini", "w") as configfile:
            config.write(configfile)
        assert bh.gpg_config_loader(os.getcwd()) == ("0xDEADBEEF", "hunter2")

    def test_gpg_writer(self):
        """
        Test writing GPG settings.
        """
        try:
            os.remove("bbarchivist.ini")
        except (OSError, IOError):
            pass
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.getcwd())):
            bh.gpg_config_writer("0xDEADF00D", "swordfish")
            assert bh.gpg_config_loader() == ("0xDEADF00D", "swordfish")
