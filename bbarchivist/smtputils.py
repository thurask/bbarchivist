#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, R0913, R0912, R0914, R0915, W0142
"""This module is used for dealing with SMTP email sending."""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015 Thurask"

import smtplib  # smtp connection
import configparser  # reading config files
import getpass  # passwords
import os  # paths
from email.mime.text import MIMEText  # email formatting
from bbarchivist import utilities  # file work


def smtp_config_loader(homepath=None):
    """
    Read a ConfigParser file to get email preferences.

    :param homepath: Folder containing bbarchivist.ini. Default is user directory.
    :type homepath: str
    """
    resultdict = {}
    config = configparser.ConfigParser()
    if homepath is None:
        homepath = os.path.expanduser("~")
    conffile = os.path.join(homepath, "bbarchivist.ini")
    if not os.path.exists(conffile):
        open(conffile, 'w').close()
    config.read(conffile)
    if not config.has_section('email'):
        config['email'] = {}
    smtpini = config['email']
    resultdict['server'] = smtpini.get('server', fallback=None)
    resultdict['port'] = int(smtpini.getint('port', fallback=0))
    resultdict['username'] = smtpini.get('username', fallback=None)
    resultdict['password'] = smtpini.get('password', fallback=None)
    resultdict['is_ssl'] = smtpini.get('is_ssl', fallback=None)
    return resultdict


def smtp_config_writer(server=None, port=None, username=None, password=None, is_ssl=True, homepath=None):
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

    :param homepath: Folder containing bbarchivist.ini. Default is user directory.
    :type homepath: str
    """
    config = configparser.ConfigParser()
    if homepath is None:
        homepath = os.path.expanduser("~")
    conffile = os.path.join(homepath, "bbarchivist.ini")
    if not os.path.exists(conffile):
        open(conffile, 'w').close()
    config.read(conffile)
    if not config.has_section('email'):
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


def smtp_config_generator(results):
    """
    Take user input to create the SMTP configparser settings.

    :param results: The results to put in bbarchivist.ini.
    :type results: dict
    """
    if results['server'] is None:
        results['server'] = input("SMTP SERVER ADDRESS: ")
    if results['port'] == 0:
        results['port'] = input("SMTP SERVER PORT: ")
    if results['username'] is None:
        results['username'] = input("EMAIL ADDRESS: ")
    if results['password'] is None:
        results['password'] = getpass.getpass(prompt="PASSWORD: ")
    if results['is_ssl'] is None:
        use_ssl = utilities.str2bool(input("Y: SSL, N: TLS (Y/N): "))
        if use_ssl:
            results['is_ssl'] = "true"
        else:
            results['is_ssl'] = "false"
    return results


def send_email(kwargs):
    """
    Wrap email sending based on SSL/TLS.

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

    :param software: Software release.
    :type software: str

    :param os: OS version.
    :type os: str

    :param body: Email message body.
    :type body: str
    """
    if kwargs['password'] is None:
        kwargs['password'] = getpass.getpass(prompt="PASSWORD: ")
    server, username, port, password = parse_kwargs(kwargs)
    subject = generate_subject(kwargs['software'], kwargs['os'])
    message = generate_message(kwargs['body'], username, subject)
    if utilities.str2bool(kwargs['is_ssl']):
        smt = smtplib.SMTP_SSL(server, port)
    else:
        smt = smtplib.SMTP(server, port)
    smt.ehlo()
    if not utilities.str2bool(kwargs['is_ssl']):
        smt.starttls()
    smt.login(username, password)
    smt.sendmail(username, username, message.as_string())
    smt.quit()


def parse_kwargs(kwargs):
    """
    Extract variables from kwargs.

    :param server: SMTP email server.
    :type server: str

    :param port: Port to use.
    :type port: int

    :param username: Email address.
    :type username: str

    :param password: Email password, optional.
    :type password: str
    """
    server = kwargs['server']
    username = kwargs['username']
    port = kwargs['port']
    password = kwargs['password']
    return server, username, port, password


def generate_message(body, username, subject):
    """
    Generate message body/headers.

    :param body: Body of text.
    :type body: str

    :param username: Address to send to and from.
    :type username: str

    :param subject: Subject of message.
    :type subject: str
    """
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = username
    return msg


def generate_subject(softwarerelease, osversion):
    """
    Generate message subject.

    :param softwarerelease: Software version.
    :type softwarerelease: str

    :param osversion: OS version.
    :type osversion: str
    """
    return "SW {0} - OS {1} available!".format(softwarerelease, osversion)


def prep_email(osversion, softwarerelease, password=None):
    """
    Bootstrap the whole process.

    :param osversion: OS version.
    :type osversion: str

    :param softwarerelease: Software version.
    :type softwarerelease: str

    :param password: Email password. None to prompt later.
    :type password: str
    """
    results = smtp_config_loader()
    results['homepath'] = None
    smtp_config_writer(**results)
    results['software'] = softwarerelease
    results['os'] = osversion
    results['body'] = utilities.return_and_delete("TEMPFILE.txt")
    if password is not None:
        results['password'] = password
    send_email(results)
