#!/usr/bin/env python3

"""This module is used for dealing with SMTP email sending."""

__author__ = "Thurask"
__license__ = "Do whatever"
__copyright__ = "2015 Thurask"

import smtplib  # smtp connection
import configparser  # reading config files
import getpass  # passwords
import os  # paths
from email.mime.text import MIMEText  # email formatting
from bbarchivist import utilities  # file work


def smtp_config_loader():
    """
    Read a ConfigParser file to get email preferences.
    """
    resultdict = {}
    config = configparser.ConfigParser()
    homepath = os.path.expanduser("~")
    conffile = os.path.join(homepath, "bbarchivist.ini")
    config.read(conffile)
    if not config.has_section('email'):
        config['email'] = {}
        with open(conffile, "w") as configfile:
            config.write(configfile)
    smtpini = config['email']
    resultdict['server'] = smtpini.get('server', fallback=None)
    resultdict['port'] = int(smtpini.getint('port', fallback=0))
    resultdict['username'] = smtpini.get('username', fallback=None)
    resultdict['password'] = smtpini.get('password', fallback=None)
    resultdict['is_ssl'] = bool(smtpini.getboolean('is_ssl', fallback=True))
    return resultdict


def smtp_config_writer(server=None, port=None, username=None, password=None, is_ssl=True):
    """
    Write a ConfigParser file to store email server details.

    :param server: SMTP email server.
    :type server: str

    :param port: Port to use.
    :type port: int

    :param username: Email address.
    :type username: str

    :param password: Email password, optional.
    :type password: str

    :param is_ssl: True if server uses SSL, False if TLS only.
    :type is_ssl: bool
    """
    config = configparser.ConfigParser()
    homepath = os.path.expanduser("~")
    conffile = os.path.join(homepath, "bbarchivist.ini")
    config['email'] = {}
    if server is not None:
        config['email']['server'] = server
    if port is not None:
        config['email']['port'] = str(port)
    if username is not None:
        config['email']['username'] = username
    if password is not None:
        config['email']['password'] = password
    if is_ssl is not None:
        config['email']['is_ssl'] = str(is_ssl).lower()
    with open(conffile, "w") as configfile:
        config.write(configfile)


def send_email(kwargs):
    """
    """
    if kwargs['password'] is None:
        kwargs['password'] = getpass.getpass(prompt="PASSWORD: ")
    if kwargs['is_ssl']:
        send_email_ssl(kwargs)
    else:
        send_email_tls(kwargs)


def parse_kwargs(kwargs):
    """
    """
    server = kwargs['server']
    username = kwargs['username']
    port = kwargs['port']
    password = kwargs['password']
    return server, username, port, password


def generate_message(body, username, subject):
    """
    """
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = username
    return msg


def generate_subject(softwarerelease, osversion):
    """
    """
    return "SW {0} - OS {1} available!".format(softwarerelease, osversion)


def send_email_ssl(kwargs):
    """
    """
    server, username, port, password = parse_kwargs(kwargs)
    subject = generate_subject(kwargs['software'], kwargs['os'])
    message = generate_message(kwargs['body'], username, subject)
    smt = smtplib.SMTP_SSL(server, port)
    smt.ehlo()
    smt.login(username, password)
    smt.sendmail(username, username, message.as_string())
    smt.quit()


def send_email_tls(kwargs):
    """
    """
    server, username, port, password = parse_kwargs(kwargs)
    subject = generate_subject(kwargs['software'], kwargs['os'])
    message = generate_message(kwargs['body'], username, subject)
    smt = smtplib.SMTP(server, port)
    smt.ehlo()
    smt.starttls()
    smt.login(username, password)
    smt.sendmail(username, username, message.as_string())
    smt.quit()


def prep_email(osversion, softwarerelease):
    """
    """
    results = smtp_config_loader()
    smtp_config_writer(**results)
    results['software'] = softwarerelease
    results['os'] = osversion
    bodytext = utilities.return_and_delete("TEMPFILE.txt")
    results['body'] = bodytext
    send_email(results)
