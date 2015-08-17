#!/usr/bin/env python3

"""This module is used to generate file hashes/checksums and PGP signatures."""

__author__ = "Thurask"
__license__ = "Do whatever"
__copyright__ = "2015 Thurask"

import zlib  # crc32/adler32
import hashlib  # all other hashes
import hmac  # escreens is a hmac, news at 11
import os  # path work
import gnupg  # interface b/w Python, GPG


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
    Takes an instance of gnupg.GPG().

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


def verifier(workingdir, blocksize=16 * 1024 * 1024,
             crc32=False, adler32=False,
             sha1=True, sha224=False, sha256=False,
             sha384=False, sha512=False, md5=True,
             md4=False, ripemd160=False, whirlpool=False,
             splitfiles=True):
    """
    For all files in a directory, perform various hash/checksum functions.
    Take booleans to define hashes, write the output to a/individual .cksum file(s).

    :param workingdir: Path containing files you wish to verify.
    :type workingdir: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int

    :param crc32: Use of CRC32. False by default.
    :type crc32: bool

    :param adler32: Use of Adler-32. False by default.
    :type adler32: bool

    :param sha1: Use of SHA-1. True by default.
    :type sha1: bool

    :param sha224: Use of SHA-224. False by default.
    :type sha224: bool

    :param sha256: Use of SHA-256. False by default.
    :type sha256: bool

    :param sha384: Use of SHA-384. False by default.
    :type sha384: bool

    :param sha512: Use of SHA-512. False by default.
    :type sha512: bool

    :param md5: Use of MD5. True by default.
    :type md5: bool

    :param md4: Use of MD4. False by default. Depends on system.
    :type md4: bool

    :param ripemd160: Use of RIPEMD160. False by default. Depends on system.
    :type ripemd160: bool

    :param whirlpool: Use of Whirlpool. False by default. Depends on system.
    :type whirlpool: bool

    :param splitfiles: Create individual cksum files. True by default.
    :type splitfiles: bool
    """
    hashoutput_crc32 = "CRC32\n"
    hashoutput_adler32 = "ADLER32\n"
    hashoutput_sha1 = "SHA1\n"
    hashoutput_sha224 = "SHA224\n"
    hashoutput_sha256 = "SHA256\n"
    hashoutput_sha384 = "SHA384\n"
    hashoutput_sha512 = "SHA512\n"
    hashoutput_md5 = "MD5\n"
    hashoutput_md4 = "MD4\n"
    hashoutput_ripemd160 = "RIPEMD160\n"
    hashoutput_whirlpool = "WHIRLPOOL\n"
    if os.listdir(workingdir) == []:
        return
    else:
        for file in os.listdir(workingdir):
            if os.path.isdir(os.path.join(workingdir, file)):
                pass  # exclude folders
            elif file.endswith((".cksum", ".asc")):
                pass  # exclude already generated files
            else:
                print("HASHING:", str(file))
                if adler32:
                    print("ADLER32 ", end="")
                    result_adler32 = adler32hash(
                        os.path.join(
                            workingdir,
                            file),
                        blocksize)
                    hashoutput_adler32 += str(result_adler32.upper())
                    hashoutput_adler32 += " "
                    hashoutput_adler32 += str(file)
                    hashoutput_adler32 += " \n"
                if crc32:
                    print("CRC32 ", end="")
                    result_crc32 = crc32hash(
                        os.path.join(
                            workingdir,
                            file),
                        blocksize)
                    hashoutput_crc32 += str(result_crc32.upper())
                    hashoutput_crc32 += " "
                    hashoutput_crc32 += str(file)
                    hashoutput_crc32 += " \n"
                if md4:
                    print("MD4 ", end="")
                    result_md4 = md4hash(
                        os.path.join(
                            workingdir,
                            file),
                        blocksize)
                    hashoutput_md4 += str(result_md4.upper())
                    hashoutput_md4 += " "
                    hashoutput_md4 += str(file)
                    hashoutput_md4 += " \n"
                if md5:
                    print("MD5 ", end="")
                    result_md5 = md5hash(
                        os.path.join(
                            workingdir,
                            file),
                        blocksize)
                    hashoutput_md5 += str(result_md5.upper())
                    hashoutput_md5 += " "
                    hashoutput_md5 += str(file)
                    hashoutput_md5 += " \n"
                if sha1:
                    print("SHA1 ", end="")
                    result_sha1 = sha1hash(
                        os.path.join(
                            workingdir,
                            file),
                        blocksize)
                    hashoutput_sha1 += str(result_sha1.upper())
                    hashoutput_sha1 += " "
                    hashoutput_sha1 += str(file)
                    hashoutput_sha1 += " \n"
                if sha224:
                    print("SHA224 ", end="")
                    result_sha224 = sha224hash(
                        os.path.join(
                            workingdir,
                            file),
                        blocksize)
                    hashoutput_sha224 += str(result_sha224.upper())
                    hashoutput_sha224 += " "
                    hashoutput_sha224 += str(file)
                    hashoutput_sha224 += " \n"
                if sha256:
                    print("SHA256 ", end="")
                    result_sha256 = sha256hash(
                        os.path.join(
                            workingdir,
                            file),
                        blocksize)
                    hashoutput_sha256 += str(result_sha256.upper())
                    hashoutput_sha256 += " "
                    hashoutput_sha256 += str(file)
                    hashoutput_sha256 += " \n"
                if sha384:
                    print("SHA384 ", end="")
                    result_sha384 = sha384hash(
                        os.path.join(
                            workingdir,
                            file),
                        blocksize)
                    hashoutput_sha384 += str(result_sha384.upper())
                    hashoutput_sha384 += " "
                    hashoutput_sha384 += str(file)
                    hashoutput_sha384 += " \n"
                if sha512:
                    print("SHA512 ", end="")
                    result_sha512 = sha512hash(
                        os.path.join(
                            workingdir,
                            file),
                        blocksize)
                    hashoutput_sha512 += str(result_sha512.upper())
                    hashoutput_sha512 += " "
                    hashoutput_sha512 += str(file)
                    hashoutput_sha512 += " \n"
                if ripemd160:
                    print("RIPEMD160 ", end="")
                    result_ripemd160 = ripemd160hash(
                        os.path.join(
                            workingdir,
                            file),
                        blocksize)
                    hashoutput_ripemd160 += str(result_ripemd160.upper())
                    hashoutput_ripemd160 += " "
                    hashoutput_ripemd160 += str(file)
                    hashoutput_ripemd160 += " \n"
                if whirlpool:
                    print("WHIRLPOOL ", end="")
                    result_whirlpool = whirlpoolhash(
                        os.path.join(
                            workingdir,
                            file),
                        blocksize)
                    hashoutput_whirlpool += str(result_whirlpool.upper())
                    hashoutput_whirlpool += " "
                    hashoutput_whirlpool += str(file)
                    hashoutput_whirlpool += " \n"
                print("\n")
                if splitfiles:
                    basename = file + ".cksum"
                    targetname = os.path.join(workingdir, basename)
                    with open(targetname, 'w') as target:
                        if adler32:
                            target.write(hashoutput_adler32 + "\n")
                        if crc32:
                            target.write(hashoutput_crc32 + "\n")
                        if md4:
                            target.write(hashoutput_md4 + "\n")
                        if md5:
                            target.write(hashoutput_md5 + "\n")
                        if sha1:
                            target.write(hashoutput_sha1 + "\n")
                        if sha224:
                            target.write(hashoutput_sha224 + "\n")
                        if sha256:
                            target.write(hashoutput_sha256 + "\n")
                        if sha384:
                            target.write(hashoutput_sha384 + "\n")
                        if sha512:
                            target.write(hashoutput_sha512 + "\n")
                        if ripemd160:
                            target.write(hashoutput_ripemd160 + "\n")
                        if whirlpool:
                            target.write(hashoutput_whirlpool + "\n")
                    if any((crc32, adler32,
                            md4, md5,
                            sha1, sha224, sha256, sha384, sha512,
                            ripemd160, whirlpool)):
                        with open(targetname, 'rb+') as target:
                            target.seek(-2, os.SEEK_END)
                            target.truncate()
                    else:
                        os.remove(targetname)
                    # reset hashes
                    hashoutput_crc32 = "CRC32\n"
                    hashoutput_adler32 = "ADLER32\n"
                    hashoutput_sha1 = "SHA1\n"
                    hashoutput_sha224 = "SHA224\n"
                    hashoutput_sha256 = "SHA256\n"
                    hashoutput_sha384 = "SHA384\n"
                    hashoutput_sha512 = "SHA512\n"
                    hashoutput_md5 = "MD5\n"
                    hashoutput_md4 = "MD4\n"
                    hashoutput_ripemd160 = "RIPEMD160\n"
                    hashoutput_whirlpool = "WHIRLPOOL\n"
        if not splitfiles:
            with open(os.path.join(workingdir, 'all.cksum'), 'w') as target:
                if adler32:
                    target.write(hashoutput_adler32 + "\n")
                if crc32:
                    target.write(hashoutput_crc32 + "\n")
                if md4:
                    target.write(hashoutput_md4 + "\n")
                if md5:
                    target.write(hashoutput_md5 + "\n")
                if sha1:
                    target.write(hashoutput_sha1 + "\n")
                if sha224:
                    target.write(hashoutput_sha224 + "\n")
                if sha256:
                    target.write(hashoutput_sha256 + "\n")
                if sha384:
                    target.write(hashoutput_sha384 + "\n")
                if sha512:
                    target.write(hashoutput_sha512 + "\n")
                if ripemd160:
                    target.write(hashoutput_ripemd160 + "\n")
                if whirlpool:
                    target.write(hashoutput_whirlpool + "\n")
            if any((crc32, adler32,
                    md4, md5,
                    sha1, sha224, sha256, sha384, sha512,
                    ripemd160, whirlpool)):
                with open(os.path.join(workingdir,
                                       'all.cksum'), 'rb+') as target:
                    target.seek(-2, os.SEEK_END)  # navigate to last character
                    target.truncate()  # get rid of trailing \n
            else:
                os.remove(os.path.join(workingdir, 'all.cksum'))


def gpgrunner(workingdir, keyid=None, passphrase=None, selective=False):
    """
    Create ASCII-armored PGP signatures for all files in a given directory.

    :param workingdir: Path containing files you wish to verify.
    :type workingdir: str

    :param keyid: Key to use. 8-character hexadecimal, with or without 0x.
    :type keyid: str

    :param passphrase: Passphrase for given key.
    :type passphrase: str

    :param selective: Filtering filenames/extensions. Default is false.
    :type selective: bool
    """
    try:
        gpg = gnupg.GPG()
    except ValueError:
        print("COULD NOT FIND GnuPG!")
        raise SystemExit
    else:
        if not keyid.startswith("0x"):
            keyid = "0x" + keyid.upper()
        for file in os.listdir(workingdir):
            if os.path.isdir(os.path.join(workingdir, file)):
                pass  # exclude folders
            else:
                if not file.endswith((".cksum", ".asc")):
                    print("VERIFYING:", str(file))
                    if selective:
                        if file.endswith(
                            (".7z",
                             ".tar.xz",
                             ".tar.bz2",
                             ".tar.gz",
                             ".zip",
                             ".exe")
                        ) and file.startswith(
                                ("Q10",
                                 "Z10",
                                 "Z30",
                                 "Z3",
                                 "Passport")):
                            try:
                                gpgfile(os.path.join(
                                    workingdir,
                                    file
                                ),
                                    gpg,
                                    keyid=keyid,
                                    passphrase=passphrase)
                            except Exception as e:
                                print("SOMETHING WENT WRONG")
                                print(str(e))
                                raise SystemExit
                    else:
                        try:
                            gpgfile(os.path.join(
                                workingdir,
                                file
                            ),
                                gpg,
                                keyid=keyid,
                                passphrase=passphrase)
                        except Exception as e:
                            print("SOMETHING WENT WRONG")
                            print(str(e))
                            raise SystemExit
