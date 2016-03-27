#!/usr/bin/env python3
#pylint: disable=no-self-use,unused-argument,line-too-long
"""Test the networkutils module."""

import os
import xml.etree.ElementTree
from shutil import rmtree
from hashlib import sha512
try:
    import unittest.mock as mock
except ImportError:
    import mock
import httmock
import requests
import bbarchivist.networkutils as bn

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_networkutils"):
        os.mkdir("temp_networkutils")
    os.chdir("temp_networkutils")


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_networkutils", ignore_errors=True)


def cl_good_mock(url, request):
    """
    HTTMock mock for content_length.
    """
    headers = {'content-length': '525600'}
    return httmock.response(status_code=200,
                            headers=headers)


def conn_error_mock(url, request):
    """
    HTTMock mock for content_length, connection error.
    """
    raise requests.ConnectionError


@httmock.urlmatch(netloc=r'(.*\.)?google\.com$')
def download_mock(url, request):
    """
    HTTMock mock for downloading.
    """
    content = b"Jackdaws love my big sphinx of quartz"*5000
    headers = {'content-length': len(content)}
    return httmock.response(status_code=200,
                            content=content,
                            headers=headers)


@httmock.urlmatch(netloc=r'(.*\.)?google\.com$')
def download_mock_fail(url, request):
    """
    HTTMock mock for download failure.
    """
    content = b"Jackdaws love my big sphinx of quartz"*5000
    headers = {'content-length': len(content)}
    return httmock.response(status_code=404,
                            content=content,
                            headers=headers)


@httmock.urlmatch(netloc=r'(.*\.)?google\.com$')
def download_mock_huge(url, request):
    """
    HTTMock mock for downloading big files.
    """
    content = b"Jackdaws love my big sphinx of quartz"*5000000
    headers = {'content-length': len(content)}
    return httmock.response(status_code=200,
                            content=content,
                            headers=headers)


@httmock.urlmatch(scheme="http://appworld.blackberry.com/ClientAPI/checkcarrier?homemcc=302&homemnc=220&devicevendorid=-1&pin=0")
def cc_good_mock(url, request):
    """
    Mock for carrier checking, best case.
    """
    goodbody = str('<?xml version="1.0" encoding="UTF-8"?><response ttl="604800000"><country id="36" name="Canada"/><carrier id="126" name="TELUS (CA)" icon="344294" downloadlimit="50" allowedoverride="true"/></response>')
    return goodbody


@httmock.urlmatch(scheme="http://appworld.blackberry.com/ClientAPI/checkcarrier?homemcc=302&homemnc=220&devicevendorid=-1&pin=0")
def cc_bad_mock(url, request):
    """
    Mock for carrier checking, worst case.
    """
    badbody = str('<?xml version="1.0" encoding="UTF-8"?><response ttl="600000"><country id="222" name="United States"/><carrier id="0" name="default" icon="-1" downloadlimit="50" allowedoverride="false"/></response>')
    return badbody


def av_good_mock(url, request):
    """
    Mock for availability, best case.
    """
    return {'status_code': 301, 'text': 'Light side'}


def av_bad_mock(url, request):
    """
    Mock for availability, worst case.
    """
    return {'status_code': 404, 'text': 'Dark side'}


def ps_good_mock(url, request):
    """
    Mock for PTCRB lookup, best case.
    """
    thebody = "CER-59665-001 - Rev2-x05-05\nOS Version: 10.3.0.1052 Radio Version: 10.3.0.1053 SW Release Version: 10.3.0.675\nInitial\nAug 18, 2014"
    return {'status_code': 200, 'content': thebody}


def ps_bad_mock(url, request):
    """
    Mock for PTCRB lookup, worst case.
    """
    thebody = "CER-59665-001 - Rev2-x05-05\nOS Version: 10.3.2.698 Radio Version: 10.3.2.699 SW Release Version: 10.3.2.700 OS Version: 10.3.2.698 Radio Version: 10.3.2.699 SW Release Version: 10.3.2.700\nInitial\nSma 1, 2016"
    return {'status_code': 200, 'content': thebody}


def ps_priv_mock(url, request):
    """
    Mock for PTCRB lookup, Android cert.
    """
    thebody = "HW Version CER-62542-001 Rev 7-x08-01	AAD027\nInitial\nAug 18, 2014"
    return {'status_code': 200, 'content': thebody}


def gh_mock(url, request):
    """
    Mock for kernel lookup.
    """
    thebody = '<a href="/blackberry/android-linux-kernel/tree/msm8992/AAC724" class="branch-name css-truncate-target">msm8992/AAC724</a>'
    return {'status_code': 200, 'content': thebody}


def pa_good_mock(url, request):
    """
    Mock for Android autoloader lookup, best case.
    """
    thebody = "http://bbapps.download.blackberry.com/Priv/bbry_qc8992_autoloader_user-common-AAD250.zip"
    return {'status_code': 200, 'content': thebody}


def pa_bad_mock(url, request):
    """
    Mock for Android autoloader lookup, worst case.
    """
    thebody = "http://bbapps.download.blackberry.com/Priv/bbry_qc8992_autoloader_user-common-AAD250.zip"
    return {'status_code': 404, 'content': thebody}


def cq_good_mock(url, request):
    """
    Mock for carrier update checking, ideal case.
    """
    thebody = b'<?xml version="1.0" encoding="UTF-8"?><updateDetailResponse version="2.2.1" sessionId="6158fdd7-4ac5-41ad-9849-b4ba9f18a3b5"><data authEchoTS="1366644680359"><status code="0"><friendlyMessage>Success</friendlyMessage><technicalMessage>Success</technicalMessage></status><content><updateDirectives><downloadCapOverCellular unit="MB">1035</downloadCapOverCellular><updateRequired>true</updateRequired><directive type="allowOSDowngrades" value="true"/></updateDirectives><transports><leastCostRouting>true</leastCostRouting><transport ordinal="0">serialbypass</transport><transport ordinal="1">wifigan</transport><transport ordinal="2">wifi</transport><transport ordinal="3">wan</transport><transport ordinal="4">wanroam</transport><transport ordinal="5">wanintlroam</transport></transports><softwareReleaseMetadata softwareReleaseVersion="10.3.1.1877" isSecurity="false" filterSetVersion="10.3.1.45" verbiageVersion="10.3.1.6"><cellularChargesMessage>Warning,this could be really expensive.</cellularChargesMessage></softwareReleaseMetadata><fileSets><fileSet url="http://cdn.fs.sl.blackberry.com/fs/qnx/production/f6832b88958f1c4c3f9bbfd44762e0c516760d8a"><package id="gYABgJBzlFCWITrWvadisQkRdpg" name="com.qnx.qcfm.radio.qc8960.wtr5" path="com.qnx.qcfm.radio.qc8960.wtr5/10.3.1.2727/qc8960.wtr5-10.3.1.2727-nto+armle-v7+signed.bar" downloadSize="53283856" operation="add" version="10.3.1.2727" checksum="swnw5y03_MNK3MqWF9227FynZSyIgiW3Nj42Zv96fmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" type="system:radio"/><package id="gYABgEd1yw2Ezd7gd-uX5-coqaE" name="com.qnx.coreos.qcfm.os.qc8960.factory_sfi.desktop" path="com.qnx.coreos.qcfm.os.qc8960.factory_sfi.desktop/10.3.1.2726/qc8960.factory_sfi.desktop-10.3.1.2726-nto+armle-v7+signed.bar" downloadSize="1909111199" operation="add" version="10.3.1.2726" checksum="eb7KMyZxajwgTkamg3VPHr8mEPT4CxjKF3TbmaoGJjMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" type="system:desktop"/></fileSet></fileSets></content></data><signature><root><cipher>EC521R1</cipher><shaType>SHA512</shaType><sigR>AOm43LzpCmSwglrzvup+oWjb0gRnlmz1DWZnFLTcmfqQ4zPY4w/KmyWXQD9vg6aUQPsfB4Sl7Ejdw/F9G41jNCva</sigR><sigS>AWYQGvQ9JwIDepdt+usc1lX6N3Sk9yElF4ezZNS1w6uhEfjBpRm06rtGA+CWJEAB9tVqvfwE1ByibMz18c6ANOmM</sigS></root><chain ordinal="1"><cipher>EC521R1</cipher><shaType>SHA512</shaType><publicKey notValidUntil="1434256882020" notValidAfter="1434688882020">BAF+BsRg/iDhyw7S3QsKBhc0hvv7xQ5+/QCsxHhzUzjjrQGuY9npBdHxN3hu2dA6NZdCzR+h35T+YNka9bZTe1tjMgB4txezGIuqh3nVmk+Gze69YCZ+22BANs3DNo8q3bYD7K3/kulm2zbZESLq9YnQcCoi336JkSrGNEEPaa1yU27D7Q==</publicKey><sigR>AJSk+Z4JLIyBy3aeSireNR+9Kx+69nLLRublGIq/Y/MrHatkmvKharH48SMZZl3v19p08H8PUfps4f7NgewHOHei</sigR><sigS>AJeRkTgkhkCtQsBi2+oBElFgcbua97vEXco0x5Xs/onMDAvSL0dlbsFXKOtblX6I2pYkUTajAFEZ2MLuCTe5s/l0</sigS></chain></signature></updateDetailResponse>'
    return {'status_code': 200, 'content': thebody}


def cq_bad_mock(url, request):
    """
    Mock for carrier update checking, bad case.
    """
    thebody = b'<?xml version="1.0" encoding="UTF-8"?><updateDetailResponse version="2.2.1" sessionId="6158fdd7-4ac5-41ad-9849-b4ba9f18a3b5"><data authEchoTS="1366644680359"><status code="0"><friendlyMessage>Success</friendlyMessage><technicalMessage>Success</technicalMessage></status><content><updateDirectives><downloadCapOverCellular unit="MB">1035</downloadCapOverCellular><updateRequired>true</updateRequired><directive type="allowOSDowngrades" value="true"/></updateDirectives><transports><leastCostRouting>true</leastCostRouting><transport ordinal="0">serialbypass</transport><transport ordinal="1">wifigan</transport><transport ordinal="2">wifi</transport><transport ordinal="3">wan</transport><transport ordinal="4">wanroam</transport><transport ordinal="5">wanintlroam</transport></transports><fileSets><fileSet url="http://cdn.fs.sl.blackberry.com/fs/qnx/production/f6832b88958f1c4c3f9bbfd44762e0c516760d8a"><package id="gYABgJBzlFCWITrWvadisQkRdpg" name="com.qnx.qcfm.radio.qc8960.wtr5" path="com.qnx.qcfm.radio.qc8960.wtr5/10.3.1.2727/qc8960.wtr5-10.3.1.2727-nto+armle-v7+signed.bar" downloadSize="53283856" operation="add" version="10.3.1.2727" checksum="swnw5y03_MNK3MqWF9227FynZSyIgiW3Nj42Zv96fmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" type="system:radio"/><package id="gYABgEd1yw2Ezd7gd-uX5-coqaE" name="com.qnx.coreos.qcfm.os.qc8960.factory_sfi.desktop" path="com.qnx.coreos.qcfm.os.qc8960.factory_sfi.desktop/10.3.1.2726/qc8960.factory_sfi.desktop-10.3.1.2726-nto+armle-v7+signed.bar" downloadSize="1909111199" operation="add" version="10.3.1.2726" checksum="eb7KMyZxajwgTkamg3VPHr8mEPT4CxjKF3TbmaoGJjMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" type="system:desktop"/></fileSet></fileSets></content></data><signature><root><cipher>EC521R1</cipher><shaType>SHA512</shaType><sigR>AOm43LzpCmSwglrzvup+oWjb0gRnlmz1DWZnFLTcmfqQ4zPY4w/KmyWXQD9vg6aUQPsfB4Sl7Ejdw/F9G41jNCva</sigR><sigS>AWYQGvQ9JwIDepdt+usc1lX6N3Sk9yElF4ezZNS1w6uhEfjBpRm06rtGA+CWJEAB9tVqvfwE1ByibMz18c6ANOmM</sigS></root><chain ordinal="1"><cipher>EC521R1</cipher><shaType>SHA512</shaType><publicKey notValidUntil="1434256882020" notValidAfter="1434688882020">BAF+BsRg/iDhyw7S3QsKBhc0hvv7xQ5+/QCsxHhzUzjjrQGuY9npBdHxN3hu2dA6NZdCzR+h35T+YNka9bZTe1tjMgB4txezGIuqh3nVmk+Gze69YCZ+22BANs3DNo8q3bYD7K3/kulm2zbZESLq9YnQcCoi336JkSrGNEEPaa1yU27D7Q==</publicKey><sigR>AJSk+Z4JLIyBy3aeSireNR+9Kx+69nLLRublGIq/Y/MrHatkmvKharH48SMZZl3v19p08H8PUfps4f7NgewHOHei</sigR><sigS>AJeRkTgkhkCtQsBi2+oBElFgcbua97vEXco0x5Xs/onMDAvSL0dlbsFXKOtblX6I2pYkUTajAFEZ2MLuCTe5s/l0</sigS></chain></signature></updateDetailResponse>'
    return {'status_code': 200, 'content': thebody}


def bl_big_mock(url, request):
    """
    Mock for bundle lookup, large output.
    """
    bigbody = b'<?xml version="1.0" encoding="UTF-8"?><availableBundlesResponse version="1.0.0" sessionId="bc8c11a3-76ba-4b46-ad60-413b3cc84a3a"><data authEchoTS="1366644680359"><status code="0"><friendlyMessage>Success</friendlyMessage><technicalMessage>Success</technicalMessage></status><content><bundle version="10.0.9.2372"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.0.10.672"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.1.0.1720"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.1.0.2050"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.1.0.4633"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.2.0.1791"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.2.0.1803"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.2.1.1925"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.2.1.2141"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.2.1.3247"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.2.1.3442"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.3.1.2708"><type>system:os</type><type>system:radio</type><type>application</type></bundle></content></data><signature><root><cipher>EC521R1</cipher><shaType>SHA512</shaType><sigR>ALa00xPpT1Zh30xKI8N0AXZF7Iy1d8mxzG8S0UK4Cg5JU8pOO5gMWqlw/UtHNgeU4zz05HPnxZanfylLzSzrqz2p</sigR><sigS>Af/9DdaSMbug8zoMku5nYmyQEfZcSjEHL0Q6zjPWTp4FcfO0GobnlMGNYZ0Bs8mkv6I1jEoQJknCk8m1hUE/izIs</sigS></root><chain ordinal="1"><cipher>EC521R1</cipher><shaType>SHA512</shaType><publicKey notValidUntil="1434253249861" notValidAfter="1434685249861">BAA6ueT5fEqEOQPsjAixWQLXPnrAlCepWbJzHu23I9U3Z91BNvseHiYj+HHzgKQwoS3j5wY2p7EGFtN3xj+fDDjdagHJCnio5O+zcQCld1t4E8+mI6ZBbqFjIAVuIIZB8t+HWECU8964xZPOVDRbWs1d021/shKfFqWovYNPR01i3C0ZfQ==</publicKey><sigR>AIr1WJPu863N3Gux2thgntYxL0EpeB89V7ghVC31cr9sT/LaPGItPFivYC0UwPvfG8w43fIejSSYqNphtkG7aB7U</sigR><sigS>AQNhvojvKZ6l087eK25dSbkqGpJwFEKdLUh9+6NixDingge8VYlR0p7OmjNIp0VY0OwhDCe99oEbT8uuRXWg6hFP</sigS></chain></signature></availableBundlesResponse>'
    return {'status_code': 200, 'content': bigbody}


def bl_little_mock(url, request):
    """
    Mock for bundle lookup, small output.
    """
    littlebody = b'<?xml version="1.0" encoding="UTF-8"?><availableBundlesResponse version="1.0.0" sessionId="7762de1a-909c-4afb-88fe-57acb69e9049"><data authEchoTS="1366644680359"><status code="0"><friendlyMessage>Success</friendlyMessage><technicalMessage>Success</technicalMessage></status><content><bundle version="10.3.1.2726"><type>system:os</type><type>system:radio</type><type>application</type></bundle></content></data><signature><root><cipher>EC521R1</cipher><shaType>SHA512</shaType><sigR>AN80t5quXy/WiTy0Lw0llAIGmRVogdfRttDOCbWh6uUquvAvAt2YAN1OOCLJbOOFn5SppytUJi34wXOxiopv2RjX</sigR><sigS>APPbsvblhDzEhpef8wQBgxCrTJ851e/BeVBLUzlGG7ovy220QdQHeG8ahk9bMeoTmnIkWc6f/kCs+h7hGkel+OYT</sigS></root><chain ordinal="1"><cipher>EC521R1</cipher><shaType>SHA512</shaType><publicKey notValidUntil="1434252700605" notValidAfter="1434684700605">BAHbALLG0oyfF7ZvmxOjz1NFODaTEd9gvdqaqgSwuTi39Jv87q0ZWfY7kVSxWAyuumQYfIpy+9ruTd4z7cNvXJ0u8ACJvuo3xzNpgCah74Wpqcvr+EuNGkVe0IAZDXZSGPeZC739vkPitYiqJDP8joOuFTIdpUop/qJj+YckijR9RujdUw==</publicKey><sigR>Aaou0PAOGD7njwYckvvAGlepOmDSbRV2clsaskubz01+sQ9YlLhwctCAPS9n9kpdnnYbg2TDvh6XN3lUFgmfGvJl</sigR><sigS>AN34KjWeSGVIBz4KTlHzMGMpKfDKsOQPT5UVsy+tczBhKdAeDYGaU5Yc/YFaAOz7RuxjIbHkohuHESqDcXCnvif6</sigS></chain></signature></availableBundlesResponse>'
    return {'status_code': 200, 'content': littlebody}


def sr_good_mock(url, request):
    """
    Mock for software release lookup, SR found.
    """
    goodbody = b'<?xml version="1.0" encoding="UTF-8"?><srVersionLookupResponse version="2.0.0"><data authEchoTS="1366644680359"><status code="0"><friendlyMessage>Success</friendlyMessage><technicalMessage>Success</technicalMessage></status><content><softwareReleaseVersion>10.3.2.516</softwareReleaseVersion></content></data><signature><root><cipher>EC521R1</cipher><shaType>SHA512</shaType><sigR>QnnSA+ZMae96eC82GU+VNUFGPHsqD4n7MydOacSsEwygn2Fs+41jiXZpQ8mZ51ft4eTWAlmbdpecZMqlSPbaS/4=</sigR><sigS>AQlCb2Wk87R/jwMxQCP8jElfE88nzelzqmpyakkXokRhy8kkec67R6wQIek+TJvXRsxS6hHqIhjjA5wO/NWaM5Z0</sigS></root><chain ordinal="1"><cipher>EC521R1</cipher><shaType>SHA512</shaType><publicKey notValidUntil="1434253530830" notValidAfter="1434685530830">BACDEf0rUyqeoahFj57x02KvWvq8ztyl2ekJabpghmvv256KGhkuxTj6ugD6cvf6jYOIyjx6og0XRj/cnycNb1dhrwDNwOOB/qgE+RNWWDcUL8M/Lm2nyT+kru3IZ6MWBedYKine+dZHFpJk+x26QnXsEYgtMR4rCbIVC2Ooc8vCIV29rQ==</publicKey><sigR>APicruleHOD+jCsLmaSRIDePoyICdUBQkz/jq3tpyp1jnmN6K29r35UBnsYlGtnlUKscVg5uQbCSemO5+KWYa96R</sigR><sigS>ATzJc0Ev+2ep9eFgmtn6wdt+B2TAo1n3K5lvrfKGiyFrUNEbBdIejk3afL/IwKV3euSNx+iwHrscKtrrjWIfrTgB</sigS></chain></signature></srVersionLookupResponse>'
    return {'status_code': 200, 'content': goodbody}


def sr_bad_mock(url, request):
    """
    Mock for software release lookup, SR not found.
    """
    badbody = b'<?xml version="1.0" encoding="UTF-8"?><srVersionLookupResponse version="2.0.0"><data authEchoTS="1366644680359"><status code="0"><friendlyMessage>Success</friendlyMessage><technicalMessage>Success</technicalMessage></status><content><softwareReleaseVersion>SR not in system</softwareReleaseVersion></content></data><signature><root><cipher>EC521R1</cipher><shaType>SHA512</shaType><sigR>YMd1frOGcmTxawdRMnCsPB7C/x4xik5LyHVtsTBVPVl/id+yGT5vcLfcSL9z0g5HK0iGl99J4tCvlBO12+NTU7c=</sigR><sigS>AcbRzaMX6cQ/RGfk7m7tUora+W/nvBHonKJNpHuudYAoMbKRX0CofnNB9f2QXNiPZfSHpLYZ1YkuZ9cEHDmhCitD</sigS></root><chain ordinal="1"><cipher>EC521R1</cipher><shaType>SHA512</shaType><publicKey notValidUntil="1434251625739" notValidAfter="1434683625739">BAHxY5kl7VQ37IN1b1nWKCFGdc+s5Wm6VNLINp4rfUyfQavysqbn90Le+Q76J5CLaxXHVm+3ras0DqXT2s/6f+vBAgGWDNykX5Rc4m+J+0r2nw9XlERO0jDINNlPiz7SuIttP8UNgdQIHtyjPzdna7gvjfH3MBw/vQ4aUukklBHGakZVXA==</publicKey><sigR>AUjqIq5u1DTdz2pY68ChgP38rjRY5naKcBX4h6db8qfjdJTQZ5nEPB/2ujkouj8MQAB/Mx62aoGjG8X1acFR0oiK</sigR><sigS>AZ90jlOJis7nyLLLBT72oaFBzljw3v7F2MmiPS5H4VEytKoDjHX5lLrYcuVTspBTvBp68EzFHauWvJD74bVb4ciM</sigS></chain></signature></srVersionLookupResponse>'
    return {'status_code': 200, 'content': badbody}


def sr_fail_mock(url, request):
    """
    Mock for software release lookup, XML parse error.
    """
    badbody = b'<?xml version="1.0" encoding="UTF-8"?></srVersionLookupResponse>'
    return {'status_code': 200, 'content': badbody}


def timeout_mock(url, request):
    """
    Mock for software release lookup, timeout.
    """
    raise requests.exceptions.Timeout


class TestClassNetworkutils:
    """
    Test network utilities and support functions.
    """
    def test_grab_pem(self):
        """
        Test finding CA certs.
        """
        with open("cacert.pem", "w") as targetfile:
            targetfile.write("Jackdaws love my big sphinx of quartz")
        assert bn.grab_pem() == os.path.abspath("cacert.pem")
        if os.path.exists("cacert.pem"):
            os.remove("cacert.pem")

    def test_get_content_length(self):
        """
        Test content-length header checking, best case.
        """
        theurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/7d1bb9fefe23b1c3123f748ff9e0f80cc78f006c"
        with httmock.HTTMock(cl_good_mock):
            assert bn.get_length(theurl) == 525600

    def test_content_length_null(self):
        """
        Test content-length header checking, no URL given.
        """
        assert bn.get_length(None) == 0

    def test_content_length_bad(self):
        """
        Test content-length header checking, connection error.
        """
        someurl = "http://www.qrrbrbirlbel.yu"
        with httmock.HTTMock(conn_error_mock):
            assert bn.get_length(someurl) == 0

    def test_download(self):
        """
        Test downloading.
        """
        with httmock.HTTMock(download_mock_huge):
            bn.download("http://google.com/smack.dat")
        shahash = sha512()
        with open("smack.dat", 'rb') as file:
            while True:
                data = file.read()
                if not data:
                    break
                shahash.update(data)
        assert shahash.hexdigest() == "5fc8a2aff4d2a1c84763362dd5d8b18412b8644cfd92a8d400821228c9c9c279aba909f01e9819e0d1a7eb0cc52126fada3545424f8f43a7fa3ec7396769062e"
        if os.path.exists("smack.dat"):
            while True:
                try:
                    os.remove("smack.dat")
                except PermissionError:
                    continue
                else:
                    break

    def test_download_fail(self, capsys):
        """
        Test download failure.
        """
        with httmock.HTTMock(download_mock_fail):
            bn.download("http://google.com/smack.dat")
        assert "HTTP 404" in capsys.readouterr()[0]

    def test_download_bootstrap(self):
        """
        Test multiple downloading.
        """
        baseurl = "http://google.com/"
        urllist = []
        for i in ["idle", "cleese", "gilliam", "jones", "palin", "chapman"]:
            urllist.append(baseurl + i + ".dat")
        with httmock.HTTMock(download_mock):
            bn.download_bootstrap(urllist, workers=7)
        filelist = [x.replace("http://google.com/", "") for x in urllist]
        for file in filelist:
            with open(file, 'rb') as filehandle:
                shahash = sha512()
                while True:
                    data = filehandle.read()
                    if not data:
                        break
                    shahash.update(data)
                assert shahash.hexdigest() == "02c25df184ba5ed0eb7faa43b61fc2d0752a8230cc23d3f3085af55919198f83d1664277c6c4c00d78c0f95528fe8ab9f6dc145b8f9cc4b9a0f24482a1630bd9"
        for file in filelist:
            if os.path.exists(file):
                while True:
                    try:
                        os.remove(file)
                    except PermissionError:
                        continue
                    else:
                        break

    def test_create_base_url(self):
        """
        Test base URL creation.
        """
        assert bn.create_base_url("10.3.2.9000") == "http://cdn.fs.sl.blackberry.com/fs/qnx/production/7d1bb9fefe23b1c3123f748ff9e0f80cc78f006c"

    def test_return_npc(self):
        """
        Test NPC generation.
        """
        assert bn.return_npc(10, 42) == "01004230"

    def test_avail_clean_avail(self):
        """
        Test availability cleaning, with an available software release.
        """
        result = {"p": "10.3.2.2836"}
        assert bn.clean_availability(result, "p") == ("10.3.2.2836", "PD")

    def test_avail_clean_fail(self):
        """
        Test availability cleaning, with an unavailable software release.
        """
        result = {"a1": "SR not in system"}
        assert bn.clean_availability(result, "a1") == ("SR not in system", "  ")



class TestClassNetworkutilsParsing:
    """
    Test functions that require parsing of XML/HTML.
    """
    def test_availability_good(self):
        """
        Test availability, best case.
        """
        theurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/7d1bb9fefe23b1c3123f748ff9e0f80cc78f006c"
        with httmock.HTTMock(av_good_mock):
            assert bn.availability(theurl)

    def test_availability_bad(self):
        """
        Test availability, worst case.
        """
        theurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/7d1bb9fefe23b1c3123f748ff9e0f80cc78f006c"
        with httmock.HTTMock(av_bad_mock):
            assert not bn.availability(theurl)

    def test_availability_error(self):
        """
        Test availability, connection error.
        """
        theurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/7d1bb9fefe23b1c3123f748ff9e0f80cc78f006c"
        with httmock.HTTMock(conn_error_mock):
            assert not bn.availability(theurl)

    def test_carrier_checker_good(self):
        """
        Test carrier checking, best case.
        """
        with httmock.HTTMock(cc_good_mock):
            assert bn.carrier_checker(302, 220) == ('Canada', 'TELUS (CA)')

    def test_carrier_checker_bad(self):
        """
        Test carrier checking, worst case.
        """
        with httmock.HTTMock(cc_bad_mock):
            assert bn.carrier_checker(666, 666) == ('United States', 'default')

    def test_upd_req_good(self):
        """
        Test carrier update request, ideal case.
        """
        with httmock.HTTMock(cq_good_mock):
            alist = (
                "10.3.1.1877",
                "10.3.1.2726",
                "10.3.1.2727",
                [
                    'http://cdn.fs.sl.blackberry.com/fs/qnx/production/f6832b88958f1c4c3f9bbfd44762e0c516760d8a/com.qnx.qcfm.radio.qc8960.wtr5/10.3.1.2727/qc8960.wtr5-10.3.1.2727-nto+armle-v7+signed.bar',
                    'http://cdn.fs.sl.blackberry.com/fs/qnx/production/f6832b88958f1c4c3f9bbfd44762e0c516760d8a/com.qnx.coreos.qcfm.os.qc8960.factory_sfi.desktop/10.3.1.2726/qc8960.factory_sfi.desktop-10.3.1.2726-nto+armle-v7+signed.bar'
                    ]
                )
            assert bn.carrier_query(302220, "6002E0A") == alist

    def test_upd_req_bad(self):
        """
        Test carrier update request, no software version.
        """
        with httmock.HTTMock(cq_bad_mock):
            alist = (
                "N/A",
                "10.3.1.2726",
                "10.3.1.2727",
                [
                    'http://cdn.fs.sl.blackberry.com/fs/qnx/production/f6832b88958f1c4c3f9bbfd44762e0c516760d8a/com.qnx.qcfm.radio.qc8960.wtr5/10.3.1.2727/qc8960.wtr5-10.3.1.2727-nto+armle-v7+signed.bar',
                    'http://cdn.fs.sl.blackberry.com/fs/qnx/production/f6832b88958f1c4c3f9bbfd44762e0c516760d8a/com.qnx.coreos.qcfm.os.qc8960.factory_sfi.desktop/10.3.1.2726/qc8960.factory_sfi.desktop-10.3.1.2726-nto+armle-v7+signed.bar'
                    ]
                )
            assert bn.carrier_query(302220, "6002E0A") == alist

    def test_sr_lookup_good(self):
        """
        Test software lookup, best case.
        """
        server = "https://cs.sl.blackberry.com/cse/srVersionLookup/2.0.0/"
        with httmock.HTTMock(sr_good_mock):
            assert bn.sr_lookup("10.3.2.798", server) == "10.3.2.516"

    def test_sr_lookup_bad(self):
        """
        Test software lookup, worst case.
        """
        server = "https://cs.sl.blackberry.com/cse/srVersionLookup/2.0.0/"
        with httmock.HTTMock(sr_bad_mock):
            assert bn.sr_lookup("10.3.2.798", server) == "SR not in system"

    def test_sr_lookup_error(self):
        """
        Test software lookup, XML parse error.
        """
        server = "https://cs.sl.blackberry.com/cse/srVersionLookup/2.0.0/"
        with httmock.HTTMock(sr_fail_mock):
            assert bn.sr_lookup("10.3.2.798", server) == "SR not in system"

    def test_sr_lookup_timeout(self):
        """
        Test software lookup, timeout (alpha 1, probably).
        """
        server = "https://cs.sl.blackberry.com/cse/srVersionLookup/2.0.0/"
        with httmock.HTTMock(timeout_mock):
            assert bn.sr_lookup("10.3.2.798", server) == "SR not in system"

    def test_sr_lookup_bootstrap(self):
        """
        Test multiple software lookups.
        """
        with httmock.HTTMock(sr_good_mock):
            findings = bn.sr_lookup_bootstrap("10.3.2.798")
            for key in findings:
                assert findings[key] == "10.3.2.516"

    def test_bundle_lookup_big(self):
        """
        Test bundle lookup, large input.
        """
        with httmock.HTTMock(bl_big_mock):
            assert bn.available_bundle_lookup(302, 220, "8500240A") == [
                "10.0.9.2372",
                "10.0.10.672",
                "10.1.0.1720",
                "10.1.0.2050",
                "10.1.0.4633",
                "10.2.0.1791",
                "10.2.0.1803",
                "10.2.1.1925",
                "10.2.1.2141",
                "10.2.1.3247",
                "10.2.1.3442",
                "10.3.1.2708"
                ]

    def test_bundle_lookup_small(self):
        """
        Test bundle lookup, small input.
        """
        with httmock.HTTMock(bl_little_mock):
            assert bn.available_bundle_lookup(302, 220, "6002E0A") == ["10.3.1.2726"]

    def test_ptcrb_scraper_good(self):
        """
        Test certification checking, best case.
        """
        with httmock.HTTMock(ps_good_mock):
            results = bn.ptcrb_scraper("RGY181LW")
            assert "10.3.0.1052" in results[0]

    def test_ptcrb_scraper_bad(self):
        """
        Test certification checking, worst case.
        """
        with httmock.HTTMock(ps_bad_mock):
            results = bn.ptcrb_scraper("RGY181LW")
            assert "10.3.2.698" in results[0]

    def test_ptcrb_scraper_priv(self):
        """
        Test certification checking.
        """
        with httmock.HTTMock(ps_priv_mock):
            results = bn.ptcrb_scraper("STV100-3")
            assert "AAD027" in results[0]

    def test_kernel_scraper(self):
        """
        Test kernel checking.
        """
        with httmock.HTTMock(gh_mock):
            results = bn.kernel_scraper()
            assert "msm8992/AAC724" in results[0]

    def test_autoloader_scan_good(self):
        """
        Test Android autoloader lookup, best case.
        """
        with httmock.HTTMock(pa_good_mock):
            results = bn.priv_scanner("AAD250")
            assert "user-common-AAD250" in results[0]

    def test_autoloader_scan_bad(self):
        """
        Test Android autoloader lookup, worst case.
        """
        with httmock.HTTMock(pa_bad_mock):
            results = bn.priv_scanner("AAD250")
            assert results is None
