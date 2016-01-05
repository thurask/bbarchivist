#!/usr/bin/env python3
"""Generate links from OS/radio/software."""

import sys  # load arguments
from bbarchivist import scriptutils  # script stuff
from bbarchivist import networkutils  # lookup, if sw not specified
from bbarchivist import utilities  # increment version, if radio not specified
from bbarchivist import textgenerator  # actually writing

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`linkgen.linkgen_main` with those arguments.
    """
    if len(sys.argv) > 1:
        parser = scriptutils.default_parser("bb-linkgen",
                                            "Bar link generation")
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
        questionnaire()


def questionnaire():
    """
    Questions to ask if no arguments given.
    """
    osversion = input("OS VERSION (REQUIRED): ")
    radioversion = input("RADIO VERSION (PRESS ENTER TO GUESS): ")
    softwareversion = input("OS SOFTWARE RELEASE (PRESS ENTER TO GUESS): ")
    if not radioversion:
        radioversion = None
        usealt = False
    else:
        usealt = utilities.s2b(input("ALTERNATE RADIO (Y/N)?: "))
    if not softwareversion:
        softwareversion = None
    if usealt:
        altsw = input("RADIO SOFTWARE RELEASE (PRESS ENTER TO GUESS): ")
        if not altsw:
            altsw = "checkme"
    else:
        altsw = None
    linkgen_main(
        osversion,
        radioversion,
        softwareversion,
        altsw)
    scriptutils.enter_to_exit(True)


def linkgen_main(osversion, radioversion=None,
                 softwareversion=None, altsw=None, temp=False):
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

    :param temp: If file we write to is temporary.
    :type temp: bool
    """
    radioversion = scriptutils.return_radio_version(osversion, radioversion)
    softwareversion, swc = scriptutils.return_sw_checked(softwareversion,
                                                         osversion)
    del swc
    if altsw is not None:
        altsw, aswc = scriptutils.return_radio_sw_checked(altsw, radioversion)
        del aswc
    baseurl = networkutils.create_base_url(softwareversion)

    # List of debrick urls
    oses, cores, radios = textgenerator.url_gen(osversion,
                                                radioversion,
                                                softwareversion)
    if altsw is not None:
        del radios
        dbks, cors, radios = textgenerator.url_gen(osversion,
                                                   radioversion,
                                                   altsw)
        del dbks
        del cors

    avlty = networkutils.availability(baseurl)
    textgenerator.write_links(softwareversion, osversion, radioversion,
                              oses, cores, radios,
                              avlty, False, None, temp, altsw)


if __name__ == "__main__":
    grab_args()
