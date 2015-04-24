#!/usr/bin/env python3

import hmac
import hashlib
from . import bbconstants


def calculate_escreens(pin, app, uptime, duration=30):
    duration = int(duration)
    data = pin + app + uptime + bbconstants._lifetimes[duration]
    newhmac = hmac.new(bbconstants._secret.encode(),
                       data.encode(),
                       digestmod=hashlib.sha1)
    key = newhmac.hexdigest()[:8]
    return key.upper()
