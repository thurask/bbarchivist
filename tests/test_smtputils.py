#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, W0201, W0142
"""Test the smtputils module."""

import bbarchivist.smtputils as bs
import os
try:
    import unittest.mock as mock
except ImportError:
    import mock
from shutil import rmtree
from email.mime.text import MIMEText
from configparser import ConfigParser


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_smtputils"):
        os.mkdir("temp_smtputils")
    os.chdir("temp_smtputils")


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_smtputils", ignore_errors=True)


class TestClassSMTPUtils:
    """
    Test SMTP-related tools.
    """
    def setup_class(self):
        """
        Create dictionaries for self.
        """
        self.dummy = {"server": None,
                      "port": 0,
                      "username": None,
                      "password": None,
                      "is_ssl": None}
        self.results = {"server": "abc.xyz",
                          "port": 69,
                          "username": "luser",
                          "password": "hunter2",
                          "is_ssl": True}
        self.results_y = {"server": 1,
                          "port": 1,
                          "username": 1,
                          "password": "pas",
                          "is_ssl": "true"}
        self.results_n = {"server": 1,
                          "port": 1,
                          "username": 1,
                          "password": "pas",
                          "is_ssl": "false"}

    def test_smtp_config_generator(self):
        """
        Test config filtering.
        """
        assert bs.smtp_config_generator(self.results) == self.results

    def test_smtp_confgen_fback(self):
        """
        Test config fallback, all true.
        """
        with mock.patch("getpass.getpass", mock.MagicMock(return_value="pas")):
            with mock.patch("builtins.input", mock.MagicMock(return_value=1)):
                assert bs.smtp_config_generator(self.dummy) == self.results_y
                with mock.patch("bbarchivist.utilities.str2bool", mock.MagicMock(return_value=False)):
                    herpderp = bs.smtp_config_generator(self.dummy)
                    herpderp["is_ssl"] = "false"
                    assert herpderp == self.results_n

    def test_parse_kwargs(self):
        """
        Test kwarg unpacking.
        """
        results = {"server": "abc.xyz",
                   "port": 69,
                   "username": "luser",
                   "password": "hunter2",
                   "is_ssl": True}
        assert bs.parse_kwargs(results) == (results['server'],
                                            results['username'],
                                            results['port'],
                                            results['password'])

    def test_generate_message(self):
        """
        Test MIMEText message creation.
        """
        body = "I am the prince of Nigeria"
        username = "prince@gov.ng"
        subject = "Urgent request"
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = username
        msg['To'] = username
        assert bs.generate_message(body, username, subject).as_string() == msg.as_string()

    def test_generate_subject(self):
        """
        Test subject generation.
        """
        sbj = "SW APPLE - OS BANANA available!"
        assert bs.generate_subject("APPLE", "BANANA") == sbj


class TestClassSMTPUtilsConfig:
    """
    Test reading/writing configs with ConfigParser.
    """
    def setup_class(self):
        """
        Create dictionaries for self.
        """
        self.smtpdict = {}
        self.smtpdict['username'] = "butt@butt.butt"
        self.smtpdict['password'] = "hunter2"
        self.smtpdict['server'] = "goatse.cx"
        self.smtpdict['port'] = 9001
        self.smtpdict['is_ssl'] = "false"
        self.bogusdict = {}
        self.bogusdict['username'] = None
        self.bogusdict['password'] = None
        self.bogusdict['server'] = None
        self.bogusdict['port'] = 0
        self.bogusdict['is_ssl'] = None

    def test_smtp_loader_empty(self):
        """
        Test reading SMTP settings when empty.
        """
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.getcwd())):
            assert bs.smtp_config_loader() == self.bogusdict

    def test_smtp_loader_completed(self):
        """
        Test reading SMTP settings when completed.
        """
        config = ConfigParser()
        open("bbarchivist.ini", 'w').close()
        config.read("bbarchivist.ini")
        config['email'] = {}
        config['email']['username'] = "butt@butt.butt"
        config['email']['password'] = "hunter2"
        config['email']['server'] = "goatse.cx"
        config['email']['port'] = "9001"
        config['email']['is_ssl'] = "false"
        with open("bbarchivist.ini", "w") as configfile:
            config.write(configfile)
        assert bs.smtp_config_loader(os.getcwd()) == self.smtpdict

    def test_smtp_writer(self):
        """
        Test writing compression settings.
        """
        try:
            os.remove("bbarchivist.ini")
        except (OSError, FileNotFoundError):
            pass
        dict2 = self.smtpdict
        dict2['port'] = 6969
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.getcwd())):
            bs.smtp_config_writer(homepath=None, **dict2)
            assert bs.smtp_config_loader() == dict2
