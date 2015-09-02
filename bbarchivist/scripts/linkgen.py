#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, R0913, R0912, R0914, R0915
"""Generate links from OS/radio/software."""

import argparse  # parse arguments
import sys  # load arguments
from bbarchivist import scriptutils  # script stuff
from bbarchivist import networkutils  # lookup, if sw not specified
from bbarchivist import utilities  # increment version, if radio not specified
from bbarchivist import bbconstants  # versions/constants
from bbarchivist import textgenerator  # actually writing


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`linkgen.linkgen_main` with those arguments.
    """
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(
            prog="bb-linkgen",
            description="Generate links from OS/radio/software.",
            epilog="http://github.com/thurask/bbarchivist")
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s " + bbconstants.VERSION)
        parser.add_argument(
            "os",
            help="OS version, 10.x.y.zzzz")
        parser.add_argument(
            "radio",
            help="Radio version, 10.x.y.zzzz",
            nargs="?",
            default=None)
        parser.add_argument(
            "swrelease",
            help="Software version, 10.x.y.zzzz",
            nargs="?",
            default=None)
        parser.add_argument(
            "-r",
            "--radiosw",
            dest="altsw",
            metavar="SW",
            help="Radio software version, if not same as OS",
            nargs="?",
            default=None)
        parser.set_defaults()
        args = parser.parse_args(sys.argv[1:])
        linkgen_main(
            args.os,
            args.radio,
            args.swrelease,
            args.altsw)
    else:
        osversion = input("OS VERSION: ")
        radioversion = input("RADIO VERSION: ")
        softwareversion = input("SOFTWARE RELEASE: ")
        print(" ")
        if not radioversion:
            radioversion = None
        if not softwareversion:
            softwareversion = None
        usealt = utilities.str2bool(input("USE ALTERNATE RADIO? Y/N: "))
        if usealt:
            altsw = input("RADIO SOFTWARE RELEASE: ")
        else:
            altsw = None
        linkgen_main(
            osversion,
            radioversion,
            softwareversion,
            altsw)
        smeg = input("Press Enter to exit")
        if smeg or not smeg:
            raise SystemExit


def linkgen_main(osversion, radioversion=None,
                 softwareversion=None, altsw=None):
    """
    Generate debrick/core/radio links for given OS, radio, software release.

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz. Can be guessed.
    :type radioversion: str

    :param softwareversion: Software version, 10.x.y.zzzz. Can be guessed.
    :type softwareversion: str

    :param altsw: Radio software release, if not the same as OS.
    :type altsw: str
    """
    radioversion = scriptutils.return_radio_version(osversion, radioversion)
    softwareversion, swchecked = scriptutils.return_sw_checked(softwareversion, osversion)
    del swchecked
    baseurl = networkutils.create_base_url(softwareversion)

    # List of debrick urls
    oses, cores, radios = textgenerator.url_generator(osversion, radioversion, softwareversion)

    if altsw:
        del radios
        dbks, cors, radios = textgenerator.url_generator(osversion, radioversion, altsw)
        del dbks
        del cors

    avlty = networkutils.availability(baseurl)
    textgenerator.write_links(softwareversion, osversion, radioversion,
                              oses, cores, radios,
                              avlty, False, None)

if __name__ == "__main__":
    grab_args()
