#!/usr/bin/env python3

import os  # path work
import gnupg  # interface b/w Python, GPG
from . import filehashtools  # hash/checksum functions


def verifier(workingdir, blocksize=16 * 1024 * 1024,
             crc32=False, adler32=False,
             sha1=True, sha224=False, sha256=False,
             sha384=False, sha512=False, md5=True,
             md4=False, ripemd160=False, whirlpool=False,
             splitfiles=True):
    """
    For all files in a directory, perform various hash/checksum functions.
    Functions based on boolean arguments, writing the output to a .cksum file.

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
                    result_adler32 = filehashtools.adler32hash(
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
                    result_crc32 = filehashtools.crc32hash(
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
                    result_md4 = filehashtools.md4hash(
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
                    result_md5 = filehashtools.md5hash(
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
                    result_sha1 = filehashtools.sha1hash(
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
                    result_sha224 = filehashtools.sha224hash(
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
                    result_sha256 = filehashtools.sha256hash(
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
                    result_sha384 = filehashtools.sha384hash(
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
                    result_sha512 = filehashtools.sha512hash(
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
                    result_ripemd160 = filehashtools.ripemd160hash(
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
                    result_whirlpool = filehashtools.whirlpoolhash(
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
                if not file.endswith(".cksum"):
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
                                filehashtools.gpgfile(os.path.join(
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
                            filehashtools.gpgfile(os.path.join(
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
