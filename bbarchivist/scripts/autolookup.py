#!/usr/bin/env python3
"""Get software release for one/many OS versions."""

import sys  # load arguments
from bbarchivist import bbconstants  # versions/constants
from bbarchivist import networkutils  # lookup
from bbarchivist import utilities  # incrementer
from bbarchivist import smtputils  # email
from bbarchivist import scriptutils  # default parser
from bbarchivist.scripts import linkgen  # automatic generation

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`autolookup.autolookup_main` with those arguments."""
    if len(sys.argv) > 1:
        parser = scriptutils.default_parser("bb-autolookup",
                                            "Get software releases")
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
            help="Only print if available",
            action="store_true",
            default=False)
        parser.add_argument(
            "-i", "--increment",
            dest="increment",
            help="Loop increment, default = 3",
            default=3,
            type=utilities.positive_integer,
            metavar="INT")
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
        parser.add_argument(
            "-c", "--ceiling",
            dest="ceiling",
            help="When to stop script, default = 9996",
            default=9996,
            type=int,
            choices=range(1, 9997),
            metavar="INT")
        args = parser.parse_args(sys.argv[1:])
        parser.set_defaults()
        if getattr(sys, 'frozen', False):
            args.sql = False
            args.email = False
        autolookup_main(
            args.os,
            args.recurse,
            args.log,
            args.autogen,
            args.increment,
            args.sql,
            args.quiet,
            args.ceiling,
            args.email)
    else:
        osversion = input("OS VERSION: ")
        recurse = utilities.s2b(input("LOOP?: "))
        if recurse:
            print("Press Ctrl+C to stop loop")
        print(" ")
        autolookup_main(
            osversion,
            recurse,
            True,
            False,
            3,
            False,
            False,
            9996,
            False)
        scriptutils.enter_to_exit(True)


@utilities.wrap_keyboard_except
def autolookup_main(osversion, loop=False, log=False,
                    autogen=False, inc=3, sql=False,
                    quiet=False, ceiling=9996, mailer=False):
    """
    Lookup a software release from an OS. Can iterate.

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str:param mcc: Country code.

    :param loop: Whether or not to automatically lookup. Default is false.
    :type loop: bool

    :param log: Whether to log. Default is false.
    :type log: bool

    :param autogen: Whether to create text links. Default is false.
    :type autogen: bool

    :param inc: Lookup inc. Default is 3.
    :type inc: int

    :param sql: Whether to add valid lookups to a database. Default is false.
    :type sql: bool

    :param quiet: Whether to only output if release exists. Default is false.
    :type quiet: bool

    :param ceiling: When to stop loop. Default is 9996 (i.e. 10.x.y.9996).
    :type ceiling: int

    :param mailer: Whether to email new valid links. Default is false.
    :type mailer: bool
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
    if log:
        record = utilities.prep_logfile()
    else:
        record = None
    while True:
        print("NOW SCANNING:", osversion, end="\r")
        results = networkutils.sr_lookup_bootstrap(osversion)
        if results is None:
            raise KeyboardInterrupt
        a1rel, a1av = networkutils.clean_availability(results, 'a1')
        a2rel, a2av = networkutils.clean_availability(results, 'a2')
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
            linkgen.linkgen_main(osversion, rad, prel)
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
