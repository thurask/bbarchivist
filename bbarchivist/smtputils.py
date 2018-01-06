#!/usr/bin/env python3
"""This module is used for dealing with SMTP email sending."""

import smtplib  # smtp connection
import getpass  # passwords
from email.mime.text import MIMEText  # email formatting
from bbarchivist import utilities  # file work
from bbarchivist import iniconfig  # config parsing

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2018 Thurask"


def smtp_config_loader(homepath=None):
    """
    Read a ConfigParser file to get email preferences.

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    resultdict = {}
    smtpini = iniconfig.generic_loader("email", homepath)
    resultdict['server'] = smtpini.get('server', fallback=None)
    resultdict['port'] = int(smtpini.getint('port', fallback=0))
    resultdict['username'] = smtpini.get('username', fallback=None)
    resultdict['password'] = smtpini.get('password', fallback=None)
    resultdict['is_ssl'] = smtpini.get('is_ssl', fallback=None)
    return resultdict


def smtp_config_writer_kwargs(kwargs, config, key):
    """
    Set server/port/username/password config.

    :param kwargs: Values. Refer to `:func:smtp_config_writer`.
    :type kwargs: dict

    :param config: Configuration dictionary.
    :type config: dict

    :param key: Key for kwargs and config dict.
    :type key: str
    """
    if kwargs[key] is not None:
        config[key] = kwargs[key]
    return kwargs


def smtp_config_writer_ssl(kwargs, config):
    """
    Set SSL/TLS config.

    :param kwargs: Values. Refer to `:func:smtp_config_writer`.
    :type kwargs: dict

    :param config: Configuration dictionary.
    :type config: dict
    """
    if kwargs['is_ssl'] is not None:
        config['is_ssl'] = str(kwargs['is_ssl']).lower()
    return config


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
    results = {}
    results = smtp_config_writer_kwargs(kwargs, results, "server")
    results = smtp_config_writer_kwargs(kwargs, results, "port")
    results = smtp_config_writer_kwargs(kwargs, results, "username")
    results = smtp_config_writer_kwargs(kwargs, results, "password")
    results = smtp_config_writer_ssl(kwargs, results)
    iniconfig.generic_writer("email", results, kwargs['homepath'])


def smtp_config_generator_str(results, key, inp):
    """
    Set server/username config.

    :param kwargs: Values. Refer to `:func:smtp_config_writer`.
    :type kwargs: dict

    :param key: Key for results dict.
    :type key: str

    :param inp: Input question.
    :type inp: str
    """
    if results[key] is None:
        results[key] = input(inp)
    return results


def smtp_config_generator_port(results):
    """
    Generate port config.

    :param results: Values. Refer to `:func:smtp_config_writer`.
    :type results: dict
    """
    if results['port'] == 0:
        results['port'] = input("SMTP SERVER PORT: ")
    return results


def smtp_config_generator_password(results):
    """
    Generate password config.

    :param results: Values. Refer to `:func:smtp_config_writer`.
    :type results: dict
    """
    if results['password'] is None:
        results['password'] = getpass.getpass(prompt="PASSWORD: ")
    return results


def smtp_config_generator_ssl(results):
    """
    Generate SSL/TLS config.

    :param results: Values. Refer to `:func:smtp_config_writer`.
    :type results: dict
    """
    if results['is_ssl'] is None:
        use_ssl = utilities.i2b("Y: SSL, N: TLS (Y/N): ")
        results['is_ssl'] = "true" if use_ssl else "false"
    return results


def smtp_config_generator(results):
    """
    Take user input to create the SMTP config settings.

    :param results: The results to put in bbarchivist.ini.
    :type results: dict
    """
    results = smtp_config_generator_str(results, "server", "SMTP SERVER ADDRESS: ")
    results = smtp_config_generator_port(results)
    results = smtp_config_generator_str(results, "username", "EMAIL ADDRESS: ")
    results = smtp_config_generator_password(results)
    results = smtp_config_generator_ssl(results)
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
    password = smtp_config_generator_password(kwargs)
    server, username, port, password = parse_kwargs(kwargs)
    subject = generate_subject(kwargs['software'], kwargs['os'])
    message = generate_message(kwargs['body'], username, subject)
    payload = {
        "server": server,
        "port": port,
        "username": username,
        "password": password,
        "message": message,
        "is_ssl": utilities.s2b(kwargs["is_ssl"])
    }
    send_email_post(payload)


def prep_smtp_instance(kwargs):
    """
    Prepare a smtplib.SMTP/SMTP_SSL instance.

    :param is_ssl: True if server uses SSL, False if TLS only.
    :type is_ssl: bool

    :param server: SMTP email server.
    :type server: str

    :param port: Port to use.
    :type port: int
    """
    args = kwargs['server'], kwargs['port']
    smt = smtplib.SMTP_SSL(*args) if kwargs['is_ssl'] else smtplib.SMTP(*args)
    return smt


def send_email_post(kwargs):
    """
    Send email through SSL/TLS.

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
    smt = prep_smtp_instance(kwargs)
    smt.ehlo()
    if not kwargs['is_ssl']:
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
