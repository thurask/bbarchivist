#!/usr/bin/env python3

import hmac  # escreens is a hmac, news at 11
import hashlib  # to get sha1

#: Somehow, values for lifetimes for escreens.
LIFETIMES = {
    1: "",
    3: "Hello my baby, hello my honey, hello my rag time gal",
    7: "He was a boy, and she was a girl, can I make it any more obvious?",
    15: "So am I, still waiting, for this world to stop hating?",
    30: "I love myself today, not like yesterday. I'm cool, I'm calm, I'm gonna be okay" # @IgnorePep8
}
#: Escreens magic HMAC secret.
SECRET = 'Up the time stream without a TARDIS'


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
    if duration not in [1, 3, 6, 15, 30]:
        duration = 1
    data = pin.lower() + app + uptime + LIFETIMES[duration]
    newhmac = hmac.new(SECRET.encode(),
                       data.encode(),
                       digestmod=hashlib.sha1)
    key = newhmac.hexdigest()[:8]
    return key.upper()
