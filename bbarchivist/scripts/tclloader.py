#!/usr/bin/env python3
"""Generate autoloader from TCL autoloader template."""

import os  # path work
import shutil  # directory work
import sys  # load arguments
import requests  # session
from bbarchivist import archiveutils  # zip work
from bbarchivist import decorators  # enter to exit
from bbarchivist import loadergen  # packing loader
from bbarchivist import networkutils  # download android tools
from bbarchivist import scriptutils  # default parser
from bbarchivist import utilities  # argument filters

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2017 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`tclloader.tclloader_main` with those arguments.
    """
    parser = scriptutils.default_parser("bb-tclloader", "Create autoloaders from TCL templates")
    parser.add_argument("loaderfile",
        help="Loader zip file or directory",
        type=utilities.file_exists)
    parser.add_argument(
        "-n",
        "--name",
        dest="loadername",
        help="Manually specify loader name",
        metavar="NAME",
        default=None)
    parser.add_argument(
        "-d",
        "--directory",
        dest="directory",
        help="Use a directory instead of a zip file",
        action="store_true",
        default=False)
    parser.add_argument(
        "-l",
        "--localtools",
        dest="localtools",
        help="Use local fastboot tools instead of remote",
        action="store_true",
        default=False)
    parser.add_argument(
        "-c",
        "--compress",
        dest="compress",
        help="Compress final autoloader",
        action="store_true",
        default=False)
    args = parser.parse_args(sys.argv[1:])
    parser.set_defaults()
    tclloader_main(args.loaderfile, args.loadername, args.directory, args.localtools, args.compress)


def tclloader_main(loaderfile, loadername=None, directory=False, localtools=False, compress=False):
    """
    Scan every PRD and produce latest versions.

    :param loaderfile: Path to input file/folder.
    :type loaderfile: str

    :param loadername: Name of final autoloader. Default is auto-generated.
    :type loadername: str

    :param directory: If the input file is a folder. Default is False.
    :type directory: bool

    :param localtools: If fastboot is to be copied from the input itself. Default is False.
    :type localtools: bool

    :param compress: If the final loader is to be compressed. Default is False.
    :type compress: bool
    """
    scriptutils.slim_preamble("TCLLOADER")
    loaderdir = loaderfile if directory else loaderfile.replace(".zip", "")
    osver = loaderdir.split("-")[-1]
    if not directory:
        print("EXTRACTING FILE")
        archiveutils.extract_zip(loaderfile, loaderdir)
    if not localtools:
        print("DOWNLOADING FASTBOOT")
        networkutils.download_android_tools("plattools")
        print("VERIFYING FASTBOOT")
        andver = archiveutils.verify_android_tools("plattools")
        if andver:
            print("FASTBOOT OK, EXTRACTING")
            archiveutils.extract_android_tools("plattools")
        else:
            print("FASTBOOT DOWNLOAD FAILED, REVERTING TO LOCAL")
            localtools = True
    platform = os.listdir(os.path.join(loaderdir, "target", "product"))[0]
    if loadername is None:
        loadername = "{0}_autoloader_user-all-{1}".format(platform, osver)
    print("CREATING LOADER")
    loadergen.generate_tclloader(loaderdir, loadername, platform, localtools)
    shutil.rmtree("plattools")
    if compress:
        print("PACKING LOADER")
        archiveutils.pack_tclloader(loadername, loadername)
        print("COMPRESSION FINISHED")
    print("LOADER COMPLETE!")

if __name__ == "__main__":
    grab_args()
    decorators.enter_to_exit(False)
