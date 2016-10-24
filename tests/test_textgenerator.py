#!/usr/bin/env python3
"""Test the textgenerator module."""

from shutil import rmtree
import os
import httmock
import bbarchivist.textgenerator as bt


def setup_module(module):
    """
    Create necessary files.
    """
    if os.path.exists("temp_sqlutils"):
        rmtree("temp_sqlutils", ignore_errors=True)
    if not os.path.exists("temp_textgenerator"):
        os.mkdir("temp_textgenerator")
    os.chdir("temp_textgenerator")


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_textgenerator", ignore_errors=True)


def cl_good_mock(url, request):
    """
    HTTMock mock for content_length.
    """
    headers = {'content-length': '525600'}
    return httmock.response(status_code=200,
                            headers=headers)


class TestClassTextGenerator:
    """
    Test text generation and storage.
    """
    @classmethod
    def setup_class(cls):
        """
        Create necessary links.
        """
        deb, cor, rad = bt.url_gen("10.1.1000", "10.2.2000", "10.3.3000")
        cls.deb = deb
        cls.cor = cor
        cls.rad = rad
        cls.finals = {"http://smack.dat/Autoload-DevAlphaX-10.2.3.4567.exe":"12345",
                      "http://smack.dat/Autoload-SnekTL100-1-10.2.3.4567.exe":"987654321"}

    def test_generator_debrick_length(self):
        """
        Test length of debrick dict.
        """
        assert len(self.deb.values()) == 5

    def test_generator_core_length(self):
        """
        Test length of core dict.
        """
        assert len(self.cor.values()) == 5

    def test_generator_radio_length(self):
        """
        Test length of radio dict.
        """
        assert len(self.rad.values()) == 7

    def test_write_links(self):
        """
        Test writing URLs to file.
        """
        bt.write_links(
            "10.3.3000",
            "10.1.1000",
            "10.2.2000",
            self.deb,
            self.cor,
            self.rad,
            True,
            False,
            None,
            False,
            None)
        with open("10.3.3000.txt", 'rb') as file:
            data = file.read()
            data = data.replace(b"\r", b"")
            assert len(data) == 2850

    def test_write_links_unavailable(self):
        """
        Test writing URLs, to file, if file existence not guaranteed.
        """
        bt.write_links(
            "10.3.3000",
            "10.1.1000",
            "10.2.2000",
            self.deb,
            self.cor,
            self.rad,
            False,
            False,
            None,
            False,
            None)
        with open("10.3.3000.txt", 'rb') as file:
            data = file.read()
            data = data.replace(b"\r", b"")
            assert len(data) == 2880

    def test_write_links_withapps(self):
        """
        Test writing URLs to file, including "apps".
        """
        apps = ["http://APP#1.bar", "http://APP#2.bar", "http://APP#3.bar"]
        with httmock.HTTMock(cl_good_mock):
            bt.write_links(
                "10.3.3000",
                "10.1.1000",
                "10.2.2000",
                self.deb,
                self.cor,
                self.rad,
                True,
                True,
                apps,
                True,
                "10.4.4.4000")
        with open("TEMPFILE.txt", 'rb') as file:
            data = file.read()
            data = data.replace(b"\r", b"")
            assert len(data) == 3062

    def test_export_devloader(self):
        """
        Test writing Dev Alpha URLs to file.
        """
        bt.export_devloader("10.2.3.4567", self.finals)
        with open("DevAlpha-10.2.3.4567.txt", 'rb') as file:
            data = file.read()
            data = data.replace(b"\r", b"")
            assert len(data) == 127
