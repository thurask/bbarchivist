#!/usr/bin/env python3

import zlib  # crc32/adler32
import hashlib  # all other hashes
import hmac  # escreens is a hmac, news at 11


def crc32hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return CRC32 checksum of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    seed = 0
    with open(filepath, 'rb') as file:
        for chunk in iter(lambda: file.read(blocksize), b''):
            seed = zlib.crc32(chunk, seed)
    final = format(seed & 0xFFFFFFFF, "08x")
    return final


def adler32hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return Adler32 checksum of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    asum = 1
    with open(filepath, 'rb') as file:
        while True:
            data = file.read(blocksize)
            if not data:
                break
            asum = zlib.adler32(data, asum)
            if asum < 0:
                asum += 2 ** 32
    final = format(asum & 0xFFFFFFFF, "08x")
    return final


def sha1hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-1 hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    sha1 = hashlib.sha1()
    with open(filepath, 'rb') as file:
        while True:
            data = file.read(blocksize)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def sha224hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-224 hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    sha224 = hashlib.sha224()
    with open(filepath, 'rb') as file:
        while True:
            data = file.read(blocksize)
            if not data:
                break
            sha224.update(data)
    return sha224.hexdigest()


def sha256hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-256 hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as file:
        while True:
            data = file.read(blocksize)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def sha384hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-384 hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    sha384 = hashlib.sha384()
    with open(filepath, 'rb') as file:
        while True:
            data = file.read(blocksize)
            if not data:
                break
            sha384.update(data)
    return sha384.hexdigest()


def sha512hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-512 hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    sha512 = hashlib.sha512()
    with open(filepath, 'rb') as file:
        while True:
            data = file.read(blocksize)
            if not data:
                break
            sha512.update(data)
    return sha512.hexdigest()


def md4hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return MD4 hash of a file; depends on system SSL library.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    try:
        md4 = hashlib.new('md4')
        with open(filepath, 'rb') as file:
            while True:
                data = file.read(blocksize)
                if not data:
                    break
                md4.update(data)
        return md4.hexdigest()
    except Exception as exc:
        print(str(exc))
        print("MD4 HASH FAILED:\nIS IT AVAILABLE?")


def md5hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return MD5 hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    md5 = hashlib.md5()
    with open(filepath, 'rb') as file:
        while True:
            data = file.read(blocksize)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


def ripemd160hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return RIPEMD160 hash of a file; depends on system SSL library.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    try:
        r160 = hashlib.new('ripemd160')
        with open(filepath, 'rb') as file:
            while True:
                data = file.read(blocksize)
                if not data:
                    break
                r160.update(data)
        return r160.hexdigest()
    except Exception as exc:
        print(str(exc))
        print("RIPEMD160 HASH FAILED:\nIS IT AVAILABLE?")


def whirlpoolhash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return Whirlpool hash of a file; depends on system SSL library.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    try:
        wp = hashlib.new('whirlpool')
        with open(filepath, 'rb') as file:
            while True:
                data = file.read(blocksize)
                if not data:
                    break
                wp.update(data)
        return wp.hexdigest()
    except Exception as exc:
        print(str(exc))
        print("WHIRLPOOL HASH FAILED:\nIS IT AVAILABLE?")


def gpgfile(filepath, gpginst, keyid=None, passphrase=None):
    """
    Make ASCII-armored signature files with a given private key.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param gpginst: Instance of Python GnuPG executable.
    :type gpginst: gnupg.GPG()

    :param keyid: Key ID. 0xABCDEF01
    :type keyid: str

    :param passphrase: Passphrase for key.
    :type passphrase: str
    """
    with open(filepath, "rb") as file:
        gpginst.sign_file(file,
                          detach=True,
                          keyid=keyid,
                          passphrase=passphrase,
                          output=file.name + ".asc")


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
    duration = int(duration)
    if duration not in [1, 3, 6, 15, 30]:
        duration = 1
    data = pin.lower() + app + uptime + LIFETIMES[duration]
    newhmac = hmac.new(SECRET.encode(),
                       data.encode(),
                       digestmod=hashlib.sha1)
    key = newhmac.hexdigest()[:8]
    return key.upper()
