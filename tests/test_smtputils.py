#!/usr/bin/env python3
"""Test the smtputils module."""

import os
from shutil import rmtree
from email.mime.text import MIMEText
from configparser import ConfigParser
try:
    import unittest.mock as mock
except ImportError:
    import mock
import bbarchivist.smtputils as bs

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2018 Thurask"


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

    def test_smtp_config_generator(self):
        """
        Test config filtering.
        """
        results = {
            "server": "abc.xyz",
            "port": 69,
            "username": "luser",
            "password": "hunter2",
            "is_ssl": True
        }
        assert bs.smtp_config_generator(results) == results

    def test_smtp_confgen_fback(self):
        """
        Test config fallback.
        """
        dummy = {
            "server": None,
            "port": 0,
            "username": None,
            "password": None,
            "is_ssl": None
        }
        results_y = {
            "server": "yes",
            "port": "yes",
            "username": "yes",
            "password": "pas",
            "is_ssl": "true"
        }
        with mock.patch("getpass.getpass", mock.MagicMock(return_value="pas")):
            with mock.patch("builtins.input", mock.MagicMock(return_value="yes")):
                assert bs.smtp_config_generator(dummy) == results_y

    def test_smtp_confgen_ssl(self):
        """
        Test SSL fallback, specifically.
        """
        dummy = {
            "server": None,
            "port": 0,
            "username": None,
            "password": None,
            "is_ssl": None
        }
        results_n = {
            "server": "no",
            "port": "no",
            "username": "no",
            "password": "pas",
            "is_ssl": "false"
        }
        with mock.patch("getpass.getpass", mock.MagicMock(return_value="pas")):
            with mock.patch("builtins.input", mock.MagicMock(return_value="no")):
                assert bs.smtp_config_generator(dummy) == results_n

    def test_parse_kwargs(self):
        """
        Test kwarg unpacking.
        """
        results = {
            "server": "abc.xyz",
            "port": 69,
            "username": "luser",
            "password": "hunter2",
            "is_ssl": True
        }
        assert bs.parse_kwargs(results) == (
            results['server'],
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

    def test_send_email(self):
        """
        Test sending an email.
        """
        kwargs = {
            "server": "abc.xyz",
            "port": 69,
            "username": "luser",
            "password": None,
            "is_ssl": False,
            "software": "10.9.8.7654",
            "os": "10.2.3.4567",
            "body": "Hey! Listen!"
        }
        with mock.patch('getpass.getpass', mock.MagicMock(return_value="hunter2")):
            with mock.patch('smtplib.SMTP') as run_amock:
                bs.send_email(kwargs)
            run_amock.assert_called_with(kwargs['server'], kwargs['port'])
            kwargs2 = kwargs
            kwargs2['is_ssl'] = True
            with mock.patch('smtplib.SMTP_SSL') as run_amock:
                bs.send_email(kwargs2)
            run_amock.assert_called_with(kwargs['server'], kwargs['port'])

    def test_prep_email(self):
        """
        Test preparing and sending an email.
        """
        kwargs = {
            "server": "abc.xyz",
            "port": 69,
            "username": "luser",
            "password": None,
            "is_ssl": False,
            "software": "10.9.8.7654",
            "os": "10.2.3.4567",
            "body": "Hey! Listen!"
        }
        kwargsmin = {
            "server": "abc.xyz",
            "port": 69,
            "username": "luser",
            "password": None,
            "is_ssl": False
        }
        with mock.patch('bbarchivist.iniconfig.config_homepath', mock.MagicMock(return_value=os.getcwd())):
            with mock.patch('bbarchivist.smtputils.smtp_config_loader', mock.MagicMock(return_value=kwargsmin)):
                with mock.patch('bbarchivist.utilities.return_and_delete', mock.MagicMock(return_value="Hey! Listen!")):
                    with mock.patch('smtplib.SMTP') as run_amock:
                        bs.prep_email("10.2.3.4567", "10.9.8.7654", "hunter2")
                        run_amock.assert_called_with(kwargs['server'], kwargs['port'])


class TestClassSMTPUtilsConfig:
    """
    Test reading/writing configs with ConfigParser.
    """
    @classmethod
    def setup_class(cls):
        """
        Create dictionaries for self.
        """
        cls.smtpdict = {}
        cls.smtpdict['username'] = "butt@butt.butt"
        cls.smtpdict['password'] = "hunter2"
        cls.smtpdict['server'] = "goatse.cx"
        cls.smtpdict['port'] = 9001
        cls.smtpdict['is_ssl'] = "false"
        cls.bogusdict = {}
        cls.bogusdict['username'] = None
        cls.bogusdict['password'] = None
        cls.bogusdict['server'] = None
        cls.bogusdict['port'] = 0
        cls.bogusdict['is_ssl'] = None

    def test_smtp_loader_empty(self):
        """
        Test reading SMTP settings when empty.
        """
        try:
            os.remove("bbarchivist.ini")
        except (OSError, IOError):
            pass
        with mock.patch('bbarchivist.iniconfig.config_homepath', mock.MagicMock(return_value=os.getcwd())):
            with mock.patch('configparser.ConfigParser.read', mock.MagicMock(return_value=self.bogusdict)):
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
        except (OSError, IOError):
            pass
        dict2 = self.smtpdict
        dict2['port'] = 6969
        with mock.patch('bbarchivist.iniconfig.config_homepath', mock.MagicMock(return_value=os.getcwd())):
            bs.smtp_config_writer(homepath=None, **dict2)
            assert bs.smtp_config_loader() == dict2
