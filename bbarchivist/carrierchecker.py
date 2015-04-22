#!/usr/bin/env python3

from . import bbconstants
from . import networkutils
from . import utilities
import os


def doMagic(mcc, mnc, device,
            download=False, upgrade=False,
            directory=os.getcwd()):
    """
    Wrap around networkutils' carrier checking code.
    :param mcc: Country code.
    :type mcc: int
    :param mnc: Network code.
    :type mnc: int
    :param device: Device ID (SXX100-#)
    :type device: str
    :param download: Whether or not to download. Default is false.
    :type download: bool
    :param upgrade: Whether or not to use upgrade files. Default is false.
    :type upgrade: bool
    :param directory: Where to store files. Default is local directory.
    :type directory: str
    """
    try:
        devindex = bbconstants._devicelist.index(device.upper())
    except ValueError as e:
        print(str(e).upper())
        print("INVALID DEVICE!")
        raise SystemExit
    model = bbconstants._modellist[utilities.return_model(devindex)]
    hwid = bbconstants._hwidlist[devindex]
    version = bbconstants._version
    print("~~~CARRIERCHECKER VERSION", version + "~~~")
    country, carrier = networkutils.carrier_checker(mcc, mnc)
    print("COUNTRY:", country.upper())
    print("CARRIER:", carrier.upper())
    print("DEVICE:", model.upper())
    print("VARIANT:", device.upper())
    print("HARDWARE ID:", hwid)
    print("\nCHECKING CARRIER...")
    swv, osv, radv, files = networkutils.carrier_update_request(mcc, mnc, hwid,
                                                                download,
                                                                upgrade)
    print("SOFTWARE RELEASE:", swv)
    print("OS VERSION:", osv)
    print("RADIO VERSION:", radv)
    bardir = os.path.join(directory, swv+"-"+model)
    if not os.path.exists(bardir):
        os.makedirs(bardir)
    if download:
        print("\nDOWNLOADING...")
        filedict = {}
        for i in files:
            filedict[str(i)] = i
        download_manager = networkutils.DownloadManager(filedict, bardir)
        download_manager.begin_downloads()
