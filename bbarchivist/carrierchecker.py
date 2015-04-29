#!/usr/bin/env python3

try:
    from . import bbconstants  # @UnusedImport
except SystemError:
    import bbconstants  # @UnresolvedImport @Reimport
try:
    from . import networkutils  # @UnusedImport
except SystemError:
    import networkutils  # @UnresolvedImport @Reimport
try:
    from . import utilities  # @UnusedImport
except SystemError:
    import utilities  # @UnresolvedImport @Reimport
import os


def doMagic(mcc, mnc, device,
            download=False, upgrade=False,
            directory=os.getcwd(),
            export=False):
    """
    Wrap around :mod:`bbarchivist.networkutils` carrier checking.

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

    :param export: Whether or not to write URLs to a file. Default is false.
    :type export: bool
    """
    try:
        devindex = bbconstants._devicelist.index(device.upper())
    except ValueError as e:
        print(str(e).upper())
        print("INVALID DEVICE!")
        raise SystemExit
    model = bbconstants._modellist[utilities.return_model(devindex)]
    family = bbconstants._familylist[utilities.return_family(devindex)]
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
    if export:
        print("\nEXPORTING...")
        with open(swv + "-" + family + ".txt", "w") as target:
            target.write("OS: " + osv + "\n")
            target.write("RADIO: " + swv + "\n")
            target.write("SOFTWARE: " + radv + "\n")
            target.write("DEVICE TYPE: " + family.upper() + "\n")
            target.write("\nFILES\n")
            for i in files:
                target.write(i + "\n")
        print("\nFINISHED!!!")
    if download:
        bardir = os.path.join(directory, swv + "-" + family)
        if not os.path.exists(bardir):
            os.makedirs(bardir)
        filedict = {}
        for i in files:
            filedict[str(i)] = i
        print("\nDOWNLOADING...")
        download_manager = networkutils.DownloadManager(filedict, bardir)
        download_manager.begin_downloads()
        print("\nFINISHED!!!")
