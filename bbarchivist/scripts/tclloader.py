#!/usr/bin/env python3
"""Generate autoloader from TCL autoloader template."""

import shutil  # directory work
import sys  # load arguments
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
    parser.add_argument(
        "-nw",
        "--no-wipe",
        dest="wipe",
        help="Don't include lines to wipe userdata",
        action="store_false",
        default=True)
    args = parser.parse_args(sys.argv[1:])
    parser.set_defaults()
    tclloader_main(args.loaderfile, args.loadername, args.directory, args.localtools, args.compress, args.wipe)


def tclloader_extract(loaderfile, loaderdir, directory=False):
    """
    Extract autoloader template zip if needed.

    :param loaderfile: Path to input file.
    :type loaderfile: str

    :param loaderdir: Path to output folder.
    :type loaderdir: str

    :param directory: If the input file is a folder. Default is False.
    :type directory: bool
    """
    if not directory:
        print("EXTRACTING FILE")
        archiveutils.extract_zip(loaderfile, loaderdir)


def tclloader_fastboot(localtools=False):
    """
    Download fastboot if needed.

    :param localtools: If fastboot is to be copied from the input itself. Default is False.
    :type localtools: bool
    """
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
    return localtools


def tclloader_compress(compress=False, loadername=None):
    """
    Compress the final autoloader if needed.

    :param compress: If the final loader is to be compressed. Default is False.
    :type compress: bool

    :param loadername: Name of final autoloader.
    :type loadername: str
    """
    if compress:
        print("PACKING LOADER")
        archiveutils.pack_tclloader(loadername, loadername)
        print("COMPRESSION FINISHED")


def tclloader_main(loaderfile, loadername=None, directory=False, localtools=False, compress=False, wipe=True):
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

    :param wipe: If the final loader wipes userdata. Default is True.
    :type wipe: bool
    """
    scriptutils.slim_preamble("TCLLOADER")
    loaderdir, osver = scriptutils.tclloader_prep(loaderfile, directory)
    tclloader_extract(loaderfile, loaderdir, directory)
    localtools = tclloader_fastboot(localtools)
    loadername, platform = scriptutils.tclloader_filename(loaderdir, osver, loadername)
    print("CREATING LOADER")
    loadergen.generate_tclloader(loaderdir, loadername, platform, localtools, wipe)
    shutil.rmtree("plattools")
    tclloader_compress(compress, loadername)
    print("LOADER COMPLETE!")


if __name__ == "__main__":
    grab_args()
    decorators.enter_to_exit(False)
