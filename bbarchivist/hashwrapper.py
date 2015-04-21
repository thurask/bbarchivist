#!/usr/bin/env python3

import os
from . import filehashtools


def verifier(workingdir, blocksize=16 * 1024 * 1024,
             crc32=False, adler32=False,
             sha1=True, sha224=False, sha256=False,
             sha384=False, sha512=False, md5=True,
             md4=False, ripemd160=False, whirlpool=False):
    """
    For all files in a directory, perform various hash/checksum functions.
    on them based on boolean arguments, writing the output to a .cksum file.
    :param workingdir: Path you wish to verify.
    :type workingdir: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    :param crc32: Whether to use CRC32. False by default.
    :type crc32: bool
    :param adler32: Whether to use Adler-32. False by default.
    :type adler32: bool
    :param sha1: Whether to use SHA-1. True by default.
    :type sha1: bool
    :param sha224: Whether to use SHA-224. False by default.
    :type sha224: bool
    :param sha256: Whether to use SHA-256. False by default.
    :type sha256: bool
    :param sha384: Whether to use SHA-384. False by default.
    :type sha384: bool
    :param sha512: Whether to use SHA-512. False by default.
    :type sha512: bool
    :param md5: Whether to use MD5. True by default.
    :type md5: bool
    :param md4: Whether to use MD4. False by default. Dependent on
    system OpenSSL implementation (not in stdlib).
    :type md4: bool
    :param ripemd160: Whether to use RIPEMD160. False by default. Dependent on
    system OpenSSL implementation (not in stdlib).
    :type ripemd160: bool
    :param whirlpool: Whether to use Whirlpool. False by default. Dependent on
    system OpenSSL implementation (not in stdlib).
    :type whirlpool: bool
    """
    target = open(os.path.join(workingdir, 'all.cksum'), 'w')
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
    for file in os.listdir(workingdir):
        if os.path.isdir(os.path.join(workingdir, file)):
            pass  # exclude folders
        elif file.endswith(".cksum"):
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
    target.close()
