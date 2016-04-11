#!/usr/bin/env python3
"""This module is used for dealing with SMTP email sending."""

import smtplib  # smtp connection
import configparser  # reading config files
import getpass  # passwords
import os  # paths
from email.mime.text import MIMEText  # email formatting
from bbarchivist import utilities  # file work

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def smtp_config_loader(homepath=None):
    """
    Read a ConfigParser file to get email preferences.

    :param homepath: Folder containing ini file. Default is user directory.
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


def smtp_config_writer(**kwargs):
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

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    config = configparser.ConfigParser()
    if kwargs['homepath'] is None:
        kwargs['homepath'] = os.path.expanduser("~")
    conffile = os.path.join(kwargs['homepath'], "bbarchivist.ini")
    if not os.path.exists(conffile):
        open(conffile, 'w').close()
    config.read(conffile)
    if not config.has_section('email'):
        config['email'] = {}
    if kwargs['server'] is not None:
        config['email']['server'] = kwargs['server']
    if kwargs['port'] is not None:
        config['email']['port'] = str(kwargs['port'])
    if kwargs['username'] is not None:
        config['email']['username'] = kwargs['username']
    if kwargs['password'] is not None:
        config['email']['password'] = kwargs['password']
    if kwargs['is_ssl'] is not None:
        config['email']['is_ssl'] = str(kwargs['is_ssl']).lower()
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
        use_ssl = utilities.s2b(input("Y: SSL, N: TLS (Y/N): "))
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
    payload = {
        "server": server,
        "port": port,
        "username": username,
        "password": password,
        "message": message
    }
    if utilities.s2b(kwargs['is_ssl']):
        send_email_ssl(payload)
    else:
        send_email_tls(payload)


def send_email_ssl(kwargs):
    """
    Send email through SSL.

    :param server: SMTP email server.
    :type server: str

    :param port: Port to use.
    :type port: int

    :param username: Email address.
    :type username: str

    :param password: Email password.
    :type password: str

    :param message: Message to send, with body and subject.
    :type message: MIMEText
    """
    smt = smtplib.SMTP_SSL(kwargs['server'], kwargs['port'])
    smt.ehlo()
    smt.login(kwargs['username'], kwargs['password'])
    smt.sendmail(kwargs['username'], kwargs['username'], kwargs['message'].as_string())
    smt.quit()


def send_email_tls(kwargs):
    """
    Send email through TLS.

    :param server: SMTP email server.
    :type server: str

    :param port: Port to use.
    :type port: int

    :param username: Email address.
    :type username: str

    :param password: Email password.
    :type password: str

    :param message: Message to send, with body and subject.
    :type message: MIMEText
    """
    smt = smtplib.SMTP(kwargs['server'], kwargs['port'])
    smt.ehlo()
    smt.starttls()
    smt.login(kwargs['username'], kwargs['password'])
    smt.sendmail(kwargs['username'], kwargs['username'], kwargs['message'].as_string())
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
