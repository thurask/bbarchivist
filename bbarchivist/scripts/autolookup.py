#!/usr/bin/env python3

import argparse  # parse arguments
import sys  # load arguments
from bbarchivist import bbconstants  # versions/constants
from bbarchivist import networkutils  # lookup
from bbarchivist import utilities  # incrementer
from bbarchivist.scripts import linkgen  # link generator
import time  # get datestamp for lookup
import os  # path work


def main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.scripts.autolookup.do_magic` with those arguments.
    """
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(
            prog="bb-autolookup",
            description="Get software release for one/many OS versions.",
            epilog="http://github.com/thurask/bbarchivist")
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s " +
            bbconstants.VERSION)
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
            "-i", "--increment",
            dest="increment",
            help="Loop increment, default = 3",
            default=3,
            type=utilities.positive_integer,
            metavar="INT")
        args = parser.parse_args(sys.argv[1:])
        parser.set_defaults()
        do_magic(
            args.os,
            args.recurse,
            args.log,
            args.autogen,
            args.increment)
    else:
        osversion = input("OS VERSION: ")
        recurse = utilities.str2bool(input("LOOP?: "))
        print(" ")
        do_magic(
            osversion,
            recurse,
            True,
            False,
            3)
        smeg = input("Press Enter to exit")
        if smeg or not smeg:
            raise SystemExit

if __name__ == "__main__":
    main()


def do_magic(osversion, loop=False, log=False, autogen=False, increment=3):
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

    :param increment: Lookup increment. Default is 3.
    :type increment: int
    """
    print("~~~AUTOLOOKUP VERSION", bbconstants.VERSION + "~~~")
    print("")
    if log:
        logfile = time.strftime("%Y_%m_%d_%H%M%S") + ".txt"
        record = os.path.join(os.path.expanduser("~"),
                              logfile)
    try:
        while True:
            swrelease = ""
            print("NOW SCANNING:", osversion, end="\r"),
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
                        linkgen.do_magic(osversion, utilities.version_incrementer(osversion, 1), prel) #@IgnorePep8
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
                if log:
                    with open(record, "a") as rec:
                        rec.write(out+"\n")
                print(out)
            if not loop:
                raise KeyboardInterrupt  # hack, but whateva, I do what I want
            else:
                if int(osversion.split(".")[3]) > 9996:
                    raise KeyboardInterrupt
                else:
                    osversion = utilities.version_incrementer(osversion, increment) #@IgnorePep8
                    swrelease = ""
                    continue
    except KeyboardInterrupt:
        raise SystemExit
