#!/usr/bin/env python3

import hmac
import hashlib
try:
    from . import bbconstants  # @UnusedImport
except SystemError:
    import bbconstants  # @UnresolvedImport @Reimport


def calculate_escreens(pin, app, uptime, duration=30):
    """
    Calculate key for the Engineering Screens based on input.

    :param pin: PIN to check. 8 character hexadecimal, lowercase.
    :type pin: str

    :param app: App version. 10.x.y.zzzz.
    :type app: str

    :param uptime: Uptime in ms.
    :type uptime: str

    :param duration: 1, 3, 6, 15, 30 (days).
    :type duration: str
    """
    duration = int(duration)
    data = pin.lower() + app + uptime + bbconstants._lifetimes[duration]
    newhmac = hmac.new(bbconstants._secret.encode(),
                       data.encode(),
                       digestmod=hashlib.sha1)
    key = newhmac.hexdigest()[:8]
    return key.upper()
