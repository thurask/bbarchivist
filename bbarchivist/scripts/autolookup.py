#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, R0913, R0912, R0914, R0915
"""Get software release for one/many OS versions."""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015 Thurask"

import argparse  # parse arguments
import sys  # load arguments
from bbarchivist import bbconstants  # versions/constants
from bbarchivist import networkutils  # lookup
from bbarchivist import utilities  # incrementer
from bbarchivist import sqlutils  # sql db work
from bbarchivist.scripts import linkgen  # link generator @UnresolvedImport
from bbarchivist import smtputils  # email
import time  # get datestamp for lookup
import os  # path work


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`autolookup.autolookup_main` with those arguments."""
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(
            prog="bb-autolookup",
            description="Get software release for one/many OS versions.",
            epilog="http://github.com/thurask/bbarchivist")
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s " + bbconstants.VERSION)
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
        recurse = utilities.str2bool(input("LOOP?: "))
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
        smeg = input("Press Enter to exit")
        if smeg or not smeg:
            raise SystemExit


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

    :param quiet: Whether to only output if the release exists. Default is false.
    :type quiet: bool

    :param ceiling: When to stop loop. Default is 9996 (i.e. 10.x.y.9996).
    :type ceiling: int

    :param mailer: Whether to send new valid links through email. Default is false.
    :type mailer: bool
    """
    if mailer:
        sql = True
    print("~~~AUTOLOOKUP VERSION", bbconstants.VERSION + "~~~")
    print("")
    if log:
        logfile = time.strftime("%Y_%m_%d_%H%M%S") + ".txt"
        record = os.path.join(os.path.expanduser("~"),
                              logfile)
    try:
        while True:
            swrelease = ""
            print("NOW SCANNING:", osversion, end="\r")
            results = networkutils.sr_lookup_bootstrap(osversion)
            if results is None:
                raise KeyboardInterrupt
            a1rel = results['a1']
            if a1rel != "SR not in system" and a1rel is not None:
                a1av = "A1"
            else:
                a1av = "  "
            a2rel = results['a2']
            if a2rel != "SR not in system" and a2rel is not None:
                a2av = "A2"
            else:
                a2av = "  "
            b1rel = results['b1']
            if b1rel != "SR not in system" and b1rel is not None:
                b1av = "B1"
            else:
                b1av = "  "
            b2rel = results['b2']
            if b2rel != "SR not in system" and b2rel is not None:
                b2av = "B2"
            else:
                b2av = "  "
            prel = results['p']
            if prel != "SR not in system" and prel is not None:
                pav = "PD"
                baseurl = networkutils.create_base_url(prel)
                # Check availability of software release
                avail = networkutils.availability(baseurl)
                if avail:
                    available = "Available"
                    if autogen:
                        rad = utilities.version_incrementer(osversion, 1)
                        linkgen.linkgen_main(osversion, rad, prel)
                    if sql:
                        sqlutils.prepare_sw_db()
                        if not sqlutils.check_entry_existence(osversion, prel):
                            if mailer:
                                rad = utilities.version_incrementer(osversion, 1)
                                linkgen.linkgen_main(osversion, rad, prel, temp=True)
                                smtputils.prep_email(osversion, prel)
                            sqlutils.insert_sw_release(osversion, prel)
                else:
                    available = "Unavailable"
            else:
                pav = "  "
                available = "Unavailable"
            swrelset = set([a1rel, b1rel, b2rel, prel])
            for i in swrelset:
                if i != "SR not in system" and i is not None:
                    swrelease = i
                    break
            else:
                swrelease = ""
            if swrelease != "":
                out = "OS {} - SR {} - [{}|{}|{}|{}|{}] - {}".format(osversion,
                                                                     swrelease,
                                                                     pav,
                                                                     a1av,
                                                                     a2av,
                                                                     b1av,
                                                                     b2av,
                                                                     available)
                if not quiet:
                    if log:
                        with open(record, "a") as rec:
                            rec.write(out+"\n")
                    print(out)
                else:
                    if available == "Available":
                        if log:
                            with open(record, "a") as rec:
                                rec.write(out+"\n")
                        print(out)
            if not loop:
                raise KeyboardInterrupt  # hack, but whateva, I do what I want
            else:
                if int(osversion.split(".")[3]) > ceiling:
                    raise KeyboardInterrupt
                else:
                    osversion = utilities.version_incrementer(osversion, inc)
                    swrelease = ""
                    continue
    except KeyboardInterrupt:
        raise SystemExit

if __name__ == "__main__":
    grab_args()
