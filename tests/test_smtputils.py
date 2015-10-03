#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301
"""Test the smtputils module."""

import bbarchivist.smtputils as bs
from email.mime.text import MIMEText

class TestClassScriptutils:
    """
    Test SMTP-related tools.
    """
    def test_smtp_config_generator(self):
        """
        Test config filtering.
        """
        results={"server": "abc.xyz",
                 "port": 69,
                 "username": "luser",
                 "password": "hunter2",
                 "is_ssl": True}
        assert bs.smtp_config_generator(results) == results

    def test_parse_kwargs(self):
        """
        Test kwarg unpacking.
        """
        results={"server": "abc.xyz",
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
