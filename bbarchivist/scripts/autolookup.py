#!/usr/bin/env python3
"""Get software release for one/many OS versions."""

import sys  # load arguments

import requests  # session
from bbarchivist import argutils  # arguments
from bbarchivist import decorators  # Ctrl+C wrapper
from bbarchivist import networkutils  # lookup
from bbarchivist import scriptutils  # default parser
from bbarchivist import smtputils  # email
from bbarchivist import utilities  # incrementer

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2018 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`autolookup.autolookup_main` with those arguments.
    """
    if len(sys.argv) > 1:
        parser = scriptutils.default_parser("bb-autolookup", "Get software releases")
        parser.add_argument("os", help="OS version, 10.x.y.zzzz")
        parser.add_argument(
            "-l", "--loop",
            dest="recurse",
            help="Loop lookup, CTRL-C to quit",
            action="store_true",
            default=False)
        parser.add_argument(
            "-o", "--output",
            dest="log",
            help="Output to file",
            action="store_true",
            default=False)
        parser.add_argument(
            "-a", "--autogen",
            dest="autogen",
            help="Generate links for availables",
            action="store_true",
            default=False)
        parser.add_argument(
            "-q", "--quiet",
            dest="quiet",
            help="Only print if available (implies -p)",
            action="store_true",
            default=False)
        parser.add_argument(
            "-i", "--increment",
            dest="increment",
            help="Loop increment, default = 3",
            default=3,
            type=argutils.positive_integer,
            metavar="INT")
        parser = frozen_args(parser)
        parser.add_argument(
            "-c", "--ceiling",
            dest="ceiling",
            help="When to stop script, default = 9996",
            default=9996,
            type=int,
            choices=range(1, 9997),
            metavar="INT")
        parser.add_argument(
            "-p", "--prod-only",
            dest="production",
            help="Only check production server",
            action="store_true",
            default=False)
        parser.add_argument(
            "-n2", "--no-2",
            dest="no2",
            help="Skip checking Alpha/Beta 2 servers",
            action="store_true",
            default=False)
        args = parser.parse_args(sys.argv[1:])
        parser.set_defaults()
        execute_args(args)
    else:
        questionnaire()


def frozen_args(parser):
    """
    Add args to parser if not frozen.

    :param parser: Parser to modify.
    :type parser: argparse.ArgumentParser
    """
    if not getattr(sys, 'frozen', False):
        parser.add_argument(
            "-s", "--sql",
            dest="sql",
            help="Add valid links to database",
            action="store_true",
            default=False)
        parser.add_argument(
            "-e", "--email",
            dest="email",
            help="Email valid links to self",
            action="store_true",
            default=False)
    return parser


def execute_args(args):
    """
    Get args and decide what to do with them.

    :param args: Arguments.
    :type args: argparse.Namespace
    """
    if getattr(sys, 'frozen', False):
        args.sql = False
        args.email = False
    if args.quiet:
        args.production = True  # impossible otherwise
    autolookup_main(args.os, args.recurse, args.log, args.autogen, args.increment, args.sql, args.quiet, args.ceiling, args.email, args.production, args.no2)


def questionnaire():
    """
    Questions to ask if no arguments given.
    """
    osversion = input("OS VERSION: ")
    recurse = utilities.i2b("LOOP (Y/N)?: ")
    if recurse:
        print("Press Ctrl+C to stop loop")
    print(" ")
    autolookup_main(osversion, recurse, True, False, 3, False, False, 9996, False, False)
    decorators.enter_to_exit(True)


@decorators.wrap_keyboard_except
def autolookup_main(osversion, loop=False, log=False, autogen=False, inc=3, sql=False, quiet=False, ceiling=9996, mailer=False, prod=False, no2=False):
    """
    Lookup a software release from an OS. Can iterate.

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str

    :param loop: Whether or not to automatically lookup. Default is false.
    :type loop: bool

    :param log: Whether to log. Default is false.
    :type log: bool

    :param autogen: Whether to create text links. Default is false.
    :type autogen: bool

    :param inc: Lookup increment. Default is 3.
    :type inc: int

    :param sql: Whether to add valid lookups to a database. Default is false.
    :type sql: bool

    :param quiet: Whether to only output if release exists. Default is false.
    :type quiet: bool

    :param ceiling: When to stop loop. Default is 9996 (i.e. 10.x.y.9996).
    :type ceiling: int

    :param mailer: Whether to email new valid links. Default is false.
    :type mailer: bool

    :param prod: Whether to check only the production server. Default is false.
    :type prod: bool

    :param no2: Whether to skip Alpha2/Beta2 servers. Default is false.
    :type no2: bool
    """
    if mailer:
        sql = True
        smtpc = smtputils.smtp_config_loader()
        smtpc = smtputils.smtp_config_generator(smtpc)
        smtpc['homepath'] = None
        pword = smtpc['password']
        smtputils.smtp_config_writer(**smtpc)
    else:
        pword = None
    scriptutils.slim_preamble("AUTOLOOKUP")
    record = utilities.prep_logfile() if log else None
    sess = requests.Session()
    while True:
        if loop and int(osversion.split(".")[3]) > ceiling:
            raise KeyboardInterrupt
        print("NOW SCANNING: {0}".format(osversion), end="\r")
        if not prod:
            results = networkutils.sr_lookup_bootstrap(osversion, sess, no2)
        else:
            res = networkutils.sr_lookup(osversion, networkutils.SERVERS["p"], sess)
            results = {"p": res, "a1": None, "a2": None, "b1": None, "b2": None}
        if results is None:
            raise KeyboardInterrupt
        a1rel, a1av = networkutils.clean_availability(results, 'a1')
        if not no2:
            a2rel, a2av = networkutils.clean_availability(results, 'a2')
        else:
            a2rel = "SR not in system"
            a2av = "  "
        b1rel, b1av = networkutils.clean_availability(results, 'b1')
        b2rel, b2av = networkutils.clean_availability(results, 'b2')
        prel, pav, avail = scriptutils.prod_avail(results, mailer, osversion, pword)
        avpack = (a1av, a2av, b1av, b2av, pav)
        swrelease = scriptutils.clean_swrel(set([a1rel, a2rel, b1rel, b2rel, prel]))
        if swrelease != "":
            out = scriptutils.autolookup_output(osversion, swrelease, avail, avpack, sql)
            scriptutils.autolookup_printer(out, avail, log, quiet, record)
        if autogen and avail == "Available":
            rad = utilities.increment(osversion, 1)
            scriptutils.linkgen(osversion, rad, prel)
        if not loop:
            raise KeyboardInterrupt  # hack, but whatever
        else:
            if int(osversion.split(".")[3]) > ceiling:
                raise KeyboardInterrupt
            else:
                osversion = utilities.increment(osversion, inc)
                swrelease = ""
                continue


if __name__ == "__main__":
    grab_args()
