from . import bbconstants
from . import networkutils


def doMagic(mcc, mnc, device):
    """
    Wrap around networkutils' carrier checking code.
    :param mcc: Country code.
    :type mcc: int
    :param mnc: Network code.
    :type mnc: int
    :param device: Device ID (SXX100-#)
    :type device: str
    """
    try:
        devindex = bbconstants._devicelist.index(device)
    except ValueError as e:
        print(str(e).upper())
        print("INVALID DEVICE!")
        raise SystemExit
    hwid = bbconstants._hwidlist[devindex]
    version = bbconstants._version
    print("~~~CARRIERCHECKER VERSION", version + "~~~")
    country, carrier = networkutils.carrier_checker(mcc, mnc)
    print("COUNTRY:", country.upper())
    print("CARRIER:", carrier.upper())
    print("DEVICE:", device)
    print("HARDWARE ID:", hwid)
    print("\nCHECKING CARRIER...")
    sw, os, rad = networkutils.carrier_update_request(mcc, mnc, hwid)
    print("SOFTWARE RELEASE:", sw)
    print("OS VERSION:", os)
    print("RADIO VERSION:", rad)
