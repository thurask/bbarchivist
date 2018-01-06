#!/usr/bin/env python3
"""Test the gpgutils module."""

from shutil import rmtree
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
from bbarchivist import gpgutils as bg

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2018 Thurask"


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_gpgutils"):
        os.mkdir("temp_gpgutils")
    os.chdir("temp_gpgutils")
    with open("tempfile.txt", "w") as targetfile:
        targetfile.write("Jackdaws love my big sphinx of quartz")


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_gpgutils", ignore_errors=True)


class GPGFileMock(object):
    """Mock a gnupg.GPG instance."""

    def sign_file(self, file, detach, keyid, passphrase, output):
        """
        "Sign a file".
        """
        print("MOCKED!")


@pytest.mark.needsgpg
@pytest.mark.skipif(NOGNUPG, reason="GnuPG broken or not installed")
class TestClassGPGutils:
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
            bg.gpgfile("tempfile.txt", gpginst, "asdasdad", "hunter2")
            assert "MOCKED!" in capsys.readouterr()[0]
        elif NOGNUPG:
            pass
        else:
            gpgkey, gpgpass = bg.gpg_config_loader()
            if gpgkey is None or gpgpass is None:
                pass
            else:
                gpginst = gnupg.GPG()
                # Note: if you get a "Unknown status message 'NEWSIG'" error, then look here:
                # https://bitbucket.org/vinay.sajip/python-gnupg/issues/35/status-newsig-missing-in-verify
                bg.gpgfile("tempfile.txt", gpginst, gpgkey, gpgpass)
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
            gpgkey, gpgpass = bg.gpg_config_loader()
            if gpgkey is None or gpgpass is None:
                pass
            else:
                gpginst = gnupg.GPG()
                bg.gpgrunner(os.getcwd(), gpgkey, gpgpass, False)
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

    def test_gpgrunner_ci(self):
        """
        Test batch GnuPG signing, just with Travis/Appveyor.
        """
        with mock.patch("concurrent.futures.ThreadPoolExecutor.submit", mock.MagicMock(side_effect=None)):
            bg.gpgrunner(os.getcwd(), "12345678", "hunter2", False)
            assert True

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
                bg.gpgrunner(os.getcwd(), "12345678", "hunter2", False)
                assert "COULD NOT FIND GnuPG" in capsys.readouterr()[0]

    def test_gpgrunner_failure(self, capsys):
        """
        Test GPGRunner going wrong during the process.
        """
        with mock.patch("concurrent.futures.ThreadPoolExecutor.submit", mock.MagicMock(side_effect=Exception)):
            with pytest.raises(SystemExit):
                bg.gpgrunner(os.getcwd(), "12345678", "hunter2", False)
                assert "SOMETHING WENT WRONG" in capsys.readouterr()[0]


class TestClassGPGutilsConfig:
    """
    Test reading/writing configs with ConfigParser.
    """
    def test_gpg_loader_empty(self):
        """
        Test reading GPG settings on empty.
        """
        try:
            os.remove("bbarchivist.ini")
        except (OSError, IOError):
            pass
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.getcwd())):
            assert bg.gpg_config_loader() == (None, None)

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
        assert bg.gpg_config_loader(os.getcwd()) == ("0xDEADBEEF", "hunter2")

    def test_gpg_writer(self):
        """
        Test writing GPG settings.
        """
        try:
            os.remove("bbarchivist.ini")
        except (OSError, IOError):
            pass
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.getcwd())):
            bg.gpg_config_writer("0xDEADF00D", "swordfish")
            assert bg.gpg_config_loader() == ("0xDEADF00D", "swordfish")
