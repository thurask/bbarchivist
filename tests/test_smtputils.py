#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301
"""Test the smtputils module."""

import bbarchivist.smtputils as bs
import os
from email.mime.text import MIMEText
from configparser import ConfigParser

class TestClassSMTPUtils:
    """
    Test SMTP-related tools.
    """
    def test_smtp_config_generator(self):
        """
        Test config filtering.
        """
        results = {"server": "abc.xyz",
                   "port": 69,
                   "username": "luser",
                   "password": "hunter2",
                   "is_ssl": True}
        assert bs.smtp_config_generator(results) == results

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
        open("bbarchivist.ini", 'w').close()
        assert bs.smtp_config_loader(os.getcwd()) == self.bogusdict

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
        open("bbarchivist.ini", 'w').close()
        dict2 = self.smtpdict
        dict2['port'] = 6969
        bs.smtp_config_writer(homepath=os.getcwd(), **dict2)
        assert bs.smtp_config_loader(os.getcwd()) == dict2
