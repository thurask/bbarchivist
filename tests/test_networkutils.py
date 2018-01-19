#!/usr/bin/env python3
"""Test the networkutils module."""

import os
from hashlib import sha512
from shutil import rmtree

import bbarchivist.networkutils as bn
import httmock
import requests

try:
    import unittest.mock as mock
except ImportError:
    import mock

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2018 Thurask"


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


@httmock.all_requests
def cl_good_mock(url, request):
    """
    HTTMock mock for content_length.
    """
    headers = {'content-length': '525600'}
    return httmock.response(status_code=200, headers=headers)


@httmock.all_requests
def conn_error_mock(url, request):
    """
    HTTMock mock for content_length, connection error.
    """
    raise requests.ConnectionError


@httmock.all_requests
def download_mock(url, request):
    """
    HTTMock mock for downloading.
    """
    content = b"Jackdaws love my big sphinx of quartz" * 5000
    headers = {'content-length': len(content)}
    return httmock.response(status_code=200, content=content, headers=headers)


@httmock.all_requests
def download_mock_fail(url, request):
    """
    HTTMock mock for download failure.
    """
    content = b"Jackdaws love my big sphinx of quartz" * 5000
    headers = {'content-length': len(content)}
    return httmock.response(status_code=404, content=content, headers=headers)


@httmock.all_requests
def download_mock_huge(url, request):
    """
    HTTMock mock for downloading big files.
    """
    content = b"Jackdaws love my big sphinx of quartz" * 5000000
    headers = {'content-length': len(content)}
    return httmock.response(status_code=200, content=content, headers=headers)


@httmock.all_requests
def cc_good_mock(url, request):
    """
    Mock for carrier checking, best case.
    """
    goodbody = str('<?xml version="1.0" encoding="UTF-8"?><response ttl="604800000"><country id="36" name="Canada"/><carrier id="126" name="TELUS (CA)" icon="344294" downloadlimit="50" allowedoverride="true"/></response>')
    return goodbody


@httmock.all_requests
def cc_bad_mock(url, request):
    """
    Mock for carrier checking, worst case.
    """
    badbody = str('<?xml version="1.0" encoding="UTF-8"?><response ttl="600000"><country id="222" name="United States"/><carrier id="0" name="default" icon="-1" downloadlimit="50" allowedoverride="false"/></response>')
    return badbody


@httmock.all_requests
def av_good_mock(url, request):
    """
    Mock for availability, best case.
    """
    return {'status_code': 301, 'text': 'Light side'}


@httmock.all_requests
def av_bad_mock(url, request):
    """
    Mock for availability, worst case.
    """
    return {'status_code': 404, 'text': 'Dark side'}


@httmock.all_requests
def ps_good_mock(url, request):
    """
    Mock for PTCRB lookup, best case.
    """
    thebody = "<table></table><table><td>CER-59665-001 - Rev2-x05-05</td><td>10.3.3.2205</td><td>snek</td><td>OS Version: 10.3.0.1052 Radio Version: 10.3.0.1053 SW Release Version: 10.3.0.675</td></table>"
    return {'status_code': 200, 'content': thebody}


@httmock.all_requests
def ps_bad_mock(url, request):
    """
    Mock for PTCRB lookup, worst case.
    """
    thebody = "<table></table><table><td>CER-59665-001 - Rev2-x05-05</td><td>OS Version: 10.3.2.698 Radio Version: 10.3.2.699 SW Release Version: 10.3.2.700 OS Version: 10.3.2.698 Radio Version: 10.3.2.699 SW Release Version: 10.3.2.700</td></table>"
    return {'status_code': 200, 'content': thebody}


@httmock.all_requests
def ps_priv_mock(url, request):
    """
    Mock for PTCRB lookup, Android cert.
    """
    thebody = "<table></table><table><td>HW Version CER-62542-001 Rev 7-x08-01</td><td>AAD027</td></table>"
    return {'status_code': 200, 'content': thebody}


@httmock.all_requests
def gh_mock(url, request):
    """
    Mock for kernel lookup.
    """
    thebody = '<a href="/blackberry/android-linux-kernel/tree/msm8992/AAC724" class="branch-name css-truncate-target">msm8992/AAC724</a>' if "=3" not in request.url else '<div class="no-results-message">There aren’t any more  branches.</div>'
    return {'status_code': 200, 'content': thebody}


@httmock.all_requests
def ls_mock(url, request):
    """
    Mock for loader scraping.
    """
    thebody = '<p><b>BlackBerry DTEK50</b></p><table><tbody><tr><td style="padding-right: 20px;">BlackBerry common SW for STH100-1 &amp; STH100-2 devices</td><td>AAG326</td><td><a href="https://bbapps.download.blackberry.com/Priv/bbry_qc8952_64_sfi_autoloader_user-common-AAG326.zip" target="_blank">Click Here</a></td></tr></tbody></table>' if "blackberrymobile" not in request.url else '<ul class="list-two special-a"></ul><li><ul class="list-two special-b"><li class="list-two-a"><p>BlackBerry common SW for BBB100-1 devices use this if you bought your device direct from retailer or through a carrier other than those listed below.</p></li><li class="list-two-b"><p>AAK399</p></li><li class="list-two-c"><p><a href="http://54.247.87.13/softwareupgrade/BBM/bbry_qc8953_autoloader_user-common-AAK399%20-With%20SHA%20files.zip">Click here</a></p></li></ul>'
    return {'status_code': 200, 'content': thebody}


@httmock.all_requests
def pa_good_mock(url, request):
    """
    Mock for Android autoloader lookup, best case.
    """
    thebody = "https://bbapps.download.blackberry.com/Priv/bbry_qc8992_autoloader_user-common-AAD250.zip"
    return {'status_code': 200, 'content': thebody}


@httmock.all_requests
def pa_bbm_mock(url, request):
    """
    Mock for Android autoloader lookup, new site.
    """
    thebody = "http://54.247.87.13/softwareupgrade/BBM/bbry_qc8953_autoloader_user-common-AAL093.zip"
    return {'status_code': 200, 'content': thebody}


@httmock.all_requests
def pa_bbm_hash_mock(url, request):
    """
    Mock for Android autoloader lookup, new site.
    """
    thebody = "http://54.247.87.13/softwareupgrade/BBM/bbry_qc8953_autoloader_user-common-AAL093.sha512sum"
    return {'status_code': 200, 'content': thebody}


@httmock.all_requests
def pa_bad_mock(url, request):
    """
    Mock for Android autoloader lookup, worst case.
    """
    thebody = "https://bbapps.download.blackberry.com/Priv/bbry_qc8992_autoloader_user-common-AAD250.zip"
    return {'status_code': 404, 'content': thebody}


@httmock.all_requests
def pa_hash_mock(url, request):
    """
    Mock for Android autoloader hash lookup.
    """
    thebody = "http://us.blackberry.com/content/dam/bbfoundation/hashfiles_priv/default/bbry_qc8992_autoloader_user-common-AAD250.sha256sum"
    return {'status_code': 200, 'content': thebody}


@httmock.all_requests
def cq_good_mock(url, request):
    """
    Mock for carrier update checking, ideal case.
    """
    thebody = b'<?xml version="1.0" encoding="UTF-8"?><updateDetailResponse version="2.2.1" sessionId="6158fdd7-4ac5-41ad-9849-b4ba9f18a3b5"><data authEchoTS="1366644680359"><status code="0"><friendlyMessage>Success</friendlyMessage><technicalMessage>Success</technicalMessage></status><content><updateDirectives><downloadCapOverCellular unit="MB">1035</downloadCapOverCellular><updateRequired>true</updateRequired><directive type="allowOSDowngrades" value="true"/></updateDirectives><transports><leastCostRouting>true</leastCostRouting><transport ordinal="0">serialbypass</transport><transport ordinal="1">wifigan</transport><transport ordinal="2">wifi</transport><transport ordinal="3">wan</transport><transport ordinal="4">wanroam</transport><transport ordinal="5">wanintlroam</transport></transports><softwareReleaseMetadata softwareReleaseVersion="10.3.1.1877" isSecurity="false" filterSetVersion="10.3.1.45" verbiageVersion="10.3.1.6"><cellularChargesMessage>Warning,this could be really expensive.</cellularChargesMessage></softwareReleaseMetadata><fileSets><fileSet url="http://cdn.fs.sl.blackberry.com/fs/qnx/production/f6832b88958f1c4c3f9bbfd44762e0c516760d8a"><package id="gYABgJBzlFCWITrWvadisQkRdpg" name="com.qnx.qcfm.radio.qc8960.wtr5" path="com.qnx.qcfm.radio.qc8960.wtr5/10.3.1.2727/qc8960.wtr5-10.3.1.2727-nto+armle-v7+signed.bar" downloadSize="53283856" operation="add" version="10.3.1.2727" checksum="swnw5y03_MNK3MqWF9227FynZSyIgiW3Nj42Zv96fmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" type="system:radio"/><package id="gYABgEd1yw2Ezd7gd-uX5-coqaE" name="com.qnx.coreos.qcfm.os.qc8960.factory_sfi.desktop" path="com.qnx.coreos.qcfm.os.qc8960.factory_sfi.desktop/10.3.1.2726/qc8960.factory_sfi.desktop-10.3.1.2726-nto+armle-v7+signed.bar" downloadSize="1909111199" operation="add" version="10.3.1.2726" checksum="eb7KMyZxajwgTkamg3VPHr8mEPT4CxjKF3TbmaoGJjMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" type="system:desktop"/></fileSet></fileSets></content></data><signature><root><cipher>EC521R1</cipher><shaType>SHA512</shaType><sigR>AOm43LzpCmSwglrzvup+oWjb0gRnlmz1DWZnFLTcmfqQ4zPY4w/KmyWXQD9vg6aUQPsfB4Sl7Ejdw/F9G41jNCva</sigR><sigS>AWYQGvQ9JwIDepdt+usc1lX6N3Sk9yElF4ezZNS1w6uhEfjBpRm06rtGA+CWJEAB9tVqvfwE1ByibMz18c6ANOmM</sigS></root><chain ordinal="1"><cipher>EC521R1</cipher><shaType>SHA512</shaType><publicKey notValidUntil="1434256882020" notValidAfter="1434688882020">BAF+BsRg/iDhyw7S3QsKBhc0hvv7xQ5+/QCsxHhzUzjjrQGuY9npBdHxN3hu2dA6NZdCzR+h35T+YNka9bZTe1tjMgB4txezGIuqh3nVmk+Gze69YCZ+22BANs3DNo8q3bYD7K3/kulm2zbZESLq9YnQcCoi336JkSrGNEEPaa1yU27D7Q==</publicKey><sigR>AJSk+Z4JLIyBy3aeSireNR+9Kx+69nLLRublGIq/Y/MrHatkmvKharH48SMZZl3v19p08H8PUfps4f7NgewHOHei</sigR><sigS>AJeRkTgkhkCtQsBi2+oBElFgcbua97vEXco0x5Xs/onMDAvSL0dlbsFXKOtblX6I2pYkUTajAFEZ2MLuCTe5s/l0</sigS></chain></signature></updateDetailResponse>'
    return {'status_code': 200, 'content': thebody}


@httmock.all_requests
def cq_upgrade_mock(url, request):
    """
    Mock for carrier update checking, upgrade bars.
    """
    thebody = b'<?xml version="1.0" encoding="UTF-8"?><updateDetailResponse version="2.2.1" sessionId="6158fdd7-4ac5-41ad-9849-b4ba9f18a3b5"><data authEchoTS="1366644680359"><status code="0"><friendlyMessage>Success</friendlyMessage><technicalMessage>Success</technicalMessage></status><content><updateDirectives><downloadCapOverCellular unit="MB">1035</downloadCapOverCellular><updateRequired>true</updateRequired><directive type="allowOSDowngrades" value="true"/></updateDirectives><transports><leastCostRouting>true</leastCostRouting><transport ordinal="0">serialbypass</transport><transport ordinal="1">wifigan</transport><transport ordinal="2">wifi</transport><transport ordinal="3">wan</transport><transport ordinal="4">wanroam</transport><transport ordinal="5">wanintlroam</transport></transports><softwareReleaseMetadata softwareReleaseVersion="10.3.1.1877" isSecurity="false" filterSetVersion="10.3.1.45" verbiageVersion="10.3.1.6"><cellularChargesMessage>Warning,this could be really expensive.</cellularChargesMessage></softwareReleaseMetadata><fileSets><fileSet url="http://cdn.fs.sl.blackberry.com/fs/qnx/production/f6832b88958f1c4c3f9bbfd44762e0c516760d8a"><package id="gYABgJBzlFCWITrWvadisQkRdpg" name="com.qnx.qcfm.radio.qc8960.wtr5" path="com.qnx.qcfm.radio.qc8960.wtr5/10.3.1.2727/qc8960.wtr5-10.3.1.2727-nto+armle-v7+signed.bar" downloadSize="53283856" operation="add" version="10.3.1.2727" checksum="swnw5y03_MNK3MqWF9227FynZSyIgiW3Nj42Zv96fmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" type="system:radio"/><package id="gYABgEd1yw2Ezd7gd-uX5-coqaE" name="com.qnx.coreos.qcfm.os.qc8960.factory_sfi" path="com.qnx.coreos.qcfm.os.qc8960.factory_sfi/10.3.1.2726/qc8960.factory_sfi-10.3.1.2726-nto+armle-v7+signed.bar" downloadSize="1909111199" operation="add" version="10.3.1.2726" checksum="eb7KMyZxajwgTkamg3VPHr8mEPT4CxjKF3TbmaoGJjMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" type="system:os"/></fileSet></fileSets></content></data><signature><root><cipher>EC521R1</cipher><shaType>SHA512</shaType><sigR>AOm43LzpCmSwglrzvup+oWjb0gRnlmz1DWZnFLTcmfqQ4zPY4w/KmyWXQD9vg6aUQPsfB4Sl7Ejdw/F9G41jNCva</sigR><sigS>AWYQGvQ9JwIDepdt+usc1lX6N3Sk9yElF4ezZNS1w6uhEfjBpRm06rtGA+CWJEAB9tVqvfwE1ByibMz18c6ANOmM</sigS></root><chain ordinal="1"><cipher>EC521R1</cipher><shaType>SHA512</shaType><publicKey notValidUntil="1434256882020" notValidAfter="1434688882020">BAF+BsRg/iDhyw7S3QsKBhc0hvv7xQ5+/QCsxHhzUzjjrQGuY9npBdHxN3hu2dA6NZdCzR+h35T+YNka9bZTe1tjMgB4txezGIuqh3nVmk+Gze69YCZ+22BANs3DNo8q3bYD7K3/kulm2zbZESLq9YnQcCoi336JkSrGNEEPaa1yU27D7Q==</publicKey><sigR>AJSk+Z4JLIyBy3aeSireNR+9Kx+69nLLRublGIq/Y/MrHatkmvKharH48SMZZl3v19p08H8PUfps4f7NgewHOHei</sigR><sigS>AJeRkTgkhkCtQsBi2+oBElFgcbua97vEXco0x5Xs/onMDAvSL0dlbsFXKOtblX6I2pYkUTajAFEZ2MLuCTe5s/l0</sigS></chain></signature></updateDetailResponse>'
    return {'status_code': 200, 'content': thebody}


@httmock.all_requests
def cq_blitz_mock(url, request):
    """
    Mock for carrier update checking, blitz.
    """
    thebody = b'<?xml version="1.0" encoding="UTF-8"?><updateDetailResponse version="2.2.1" sessionId="6158fdd7-4ac5-41ad-9849-b4ba9f18a3b5"><data authEchoTS="1366644680359"><status code="0"><friendlyMessage>Success</friendlyMessage><technicalMessage>Success</technicalMessage></status><content><updateDirectives><downloadCapOverCellular unit="MB">1035</downloadCapOverCellular><updateRequired>true</updateRequired><directive type="allowOSDowngrades" value="true"/></updateDirectives><transports><leastCostRouting>true</leastCostRouting><transport ordinal="0">serialbypass</transport><transport ordinal="1">wifigan</transport><transport ordinal="2">wifi</transport><transport ordinal="3">wan</transport><transport ordinal="4">wanroam</transport><transport ordinal="5">wanintlroam</transport></transports><softwareReleaseMetadata softwareReleaseVersion="10.3.1.1877" isSecurity="false" filterSetVersion="10.3.1.45" verbiageVersion="10.3.1.6"><cellularChargesMessage>Warning,this could be really expensive.</cellularChargesMessage></softwareReleaseMetadata><fileSets><fileSet url="http://cdn.fs.sl.blackberry.com/fs/qnx/production/f6832b88958f1c4c3f9bbfd44762e0c516760d8a"><package id="gYABgJBzlFCWITrWvadisQkRdpg" name="com.qnx.qcfm.radio.qc8960.wtr5" path="com.qnx.qcfm.radio.qc8960.wtr5/10.3.1.2727/qc8960.wtr5-10.3.1.2727-nto+armle-v7+signed.bar" downloadSize="53283856" operation="add" version="10.3.1.2727" checksum="swnw5y03_MNK3MqWF9227FynZSyIgiW3Nj42Zv96fmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" type="system:package"/><package id="gYABgEd1yw2Ezd7gd-uX5-coqaE" name="com.qnx.coreos.qcfm.os.qc8960.factory_sfi" path="com.qnx.coreos.qcfm.os.qc8960.factory_sfi/10.3.1.2726/qc8960.factory_sfi-10.3.1.2726-nto+armle-v7+signed.bar" downloadSize="1909111199" operation="add" version="10.3.1.2726" checksum="eb7KMyZxajwgTkamg3VPHr8mEPT4CxjKF3TbmaoGJjMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" type="system:os"/></fileSet></fileSets></content></data><signature><root><cipher>EC521R1</cipher><shaType>SHA512</shaType><sigR>AOm43LzpCmSwglrzvup+oWjb0gRnlmz1DWZnFLTcmfqQ4zPY4w/KmyWXQD9vg6aUQPsfB4Sl7Ejdw/F9G41jNCva</sigR><sigS>AWYQGvQ9JwIDepdt+usc1lX6N3Sk9yElF4ezZNS1w6uhEfjBpRm06rtGA+CWJEAB9tVqvfwE1ByibMz18c6ANOmM</sigS></root><chain ordinal="1"><cipher>EC521R1</cipher><shaType>SHA512</shaType><publicKey notValidUntil="1434256882020" notValidAfter="1434688882020">BAF+BsRg/iDhyw7S3QsKBhc0hvv7xQ5+/QCsxHhzUzjjrQGuY9npBdHxN3hu2dA6NZdCzR+h35T+YNka9bZTe1tjMgB4txezGIuqh3nVmk+Gze69YCZ+22BANs3DNo8q3bYD7K3/kulm2zbZESLq9YnQcCoi336JkSrGNEEPaa1yU27D7Q==</publicKey><sigR>AJSk+Z4JLIyBy3aeSireNR+9Kx+69nLLRublGIq/Y/MrHatkmvKharH48SMZZl3v19p08H8PUfps4f7NgewHOHei</sigR><sigS>AJeRkTgkhkCtQsBi2+oBElFgcbua97vEXco0x5Xs/onMDAvSL0dlbsFXKOtblX6I2pYkUTajAFEZ2MLuCTe5s/l0</sigS></chain></signature></updateDetailResponse>'
    return {'status_code': 200, 'content': thebody}


@httmock.all_requests
def cq_bad_mock(url, request):
    """
    Mock for carrier update checking, bad case.
    """
    thebody = b'<?xml version="1.0" encoding="UTF-8"?><updateDetailResponse version="2.2.1" sessionId="6158fdd7-4ac5-41ad-9849-b4ba9f18a3b5"><data authEchoTS="1366644680359"><status code="0"><friendlyMessage>Success</friendlyMessage><technicalMessage>Success</technicalMessage></status><content><updateDirectives><downloadCapOverCellular unit="MB">1035</downloadCapOverCellular><updateRequired>true</updateRequired><directive type="allowOSDowngrades" value="true"/></updateDirectives><transports><leastCostRouting>true</leastCostRouting><transport ordinal="0">serialbypass</transport><transport ordinal="1">wifigan</transport><transport ordinal="2">wifi</transport><transport ordinal="3">wan</transport><transport ordinal="4">wanroam</transport><transport ordinal="5">wanintlroam</transport></transports><fileSets><fileSet url="http://cdn.fs.sl.blackberry.com/fs/qnx/production/f6832b88958f1c4c3f9bbfd44762e0c516760d8a"><package id="gYABgJBzlFCWITrWvadisQkRdpg" name="com.qnx.qcfm.radio.qc8960.wtr5" path="com.qnx.qcfm.radio.qc8960.wtr5/10.3.1.2727/qc8960.wtr5-10.3.1.2727-nto+armle-v7+signed.bar" downloadSize="53283856" operation="add" version="10.3.1.2727" checksum="swnw5y03_MNK3MqWF9227FynZSyIgiW3Nj42Zv96fmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" type="system:radio"/><package id="gYABgEd1yw2Ezd7gd-uX5-coqaE" name="com.qnx.coreos.qcfm.os.qc8960.factory_sfi.desktop" path="com.qnx.coreos.qcfm.os.qc8960.factory_sfi.desktop/10.3.1.2726/qc8960.factory_sfi.desktop-10.3.1.2726-nto+armle-v7+signed.bar" downloadSize="1909111199" operation="add" version="10.3.1.2726" checksum="eb7KMyZxajwgTkamg3VPHr8mEPT4CxjKF3TbmaoGJjMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" type="system:desktop"/></fileSet></fileSets></content></data><signature><root><cipher>EC521R1</cipher><shaType>SHA512</shaType><sigR>AOm43LzpCmSwglrzvup+oWjb0gRnlmz1DWZnFLTcmfqQ4zPY4w/KmyWXQD9vg6aUQPsfB4Sl7Ejdw/F9G41jNCva</sigR><sigS>AWYQGvQ9JwIDepdt+usc1lX6N3Sk9yElF4ezZNS1w6uhEfjBpRm06rtGA+CWJEAB9tVqvfwE1ByibMz18c6ANOmM</sigS></root><chain ordinal="1"><cipher>EC521R1</cipher><shaType>SHA512</shaType><publicKey notValidUntil="1434256882020" notValidAfter="1434688882020">BAF+BsRg/iDhyw7S3QsKBhc0hvv7xQ5+/QCsxHhzUzjjrQGuY9npBdHxN3hu2dA6NZdCzR+h35T+YNka9bZTe1tjMgB4txezGIuqh3nVmk+Gze69YCZ+22BANs3DNo8q3bYD7K3/kulm2zbZESLq9YnQcCoi336JkSrGNEEPaa1yU27D7Q==</publicKey><sigR>AJSk+Z4JLIyBy3aeSireNR+9Kx+69nLLRublGIq/Y/MrHatkmvKharH48SMZZl3v19p08H8PUfps4f7NgewHOHei</sigR><sigS>AJeRkTgkhkCtQsBi2+oBElFgcbua97vEXco0x5Xs/onMDAvSL0dlbsFXKOtblX6I2pYkUTajAFEZ2MLuCTe5s/l0</sigS></chain></signature></updateDetailResponse>'
    return {'status_code': 200, 'content': thebody}


@httmock.all_requests
def bl_big_mock(url, request):
    """
    Mock for bundle lookup, large output.
    """
    bigbody = b'<?xml version="1.0" encoding="UTF-8"?><availableBundlesResponse version="1.0.0" sessionId="bc8c11a3-76ba-4b46-ad60-413b3cc84a3a"><data authEchoTS="1366644680359"><status code="0"><friendlyMessage>Success</friendlyMessage><technicalMessage>Success</technicalMessage></status><content><bundle version="10.0.9.2372"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.0.10.672"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.1.0.1720"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.1.0.2050"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.1.0.4633"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.2.0.1791"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.2.0.1803"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.2.1.1925"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.2.1.2141"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.2.1.3247"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.2.1.3442"><type>system:os</type><type>system:radio</type><type>application</type></bundle><bundle version="10.3.1.2708"><type>system:os</type><type>system:radio</type><type>application</type></bundle></content></data><signature><root><cipher>EC521R1</cipher><shaType>SHA512</shaType><sigR>ALa00xPpT1Zh30xKI8N0AXZF7Iy1d8mxzG8S0UK4Cg5JU8pOO5gMWqlw/UtHNgeU4zz05HPnxZanfylLzSzrqz2p</sigR><sigS>Af/9DdaSMbug8zoMku5nYmyQEfZcSjEHL0Q6zjPWTp4FcfO0GobnlMGNYZ0Bs8mkv6I1jEoQJknCk8m1hUE/izIs</sigS></root><chain ordinal="1"><cipher>EC521R1</cipher><shaType>SHA512</shaType><publicKey notValidUntil="1434253249861" notValidAfter="1434685249861">BAA6ueT5fEqEOQPsjAixWQLXPnrAlCepWbJzHu23I9U3Z91BNvseHiYj+HHzgKQwoS3j5wY2p7EGFtN3xj+fDDjdagHJCnio5O+zcQCld1t4E8+mI6ZBbqFjIAVuIIZB8t+HWECU8964xZPOVDRbWs1d021/shKfFqWovYNPR01i3C0ZfQ==</publicKey><sigR>AIr1WJPu863N3Gux2thgntYxL0EpeB89V7ghVC31cr9sT/LaPGItPFivYC0UwPvfG8w43fIejSSYqNphtkG7aB7U</sigR><sigS>AQNhvojvKZ6l087eK25dSbkqGpJwFEKdLUh9+6NixDingge8VYlR0p7OmjNIp0VY0OwhDCe99oEbT8uuRXWg6hFP</sigS></chain></signature></availableBundlesResponse>'
    return {'status_code': 200, 'content': bigbody}


@httmock.all_requests
def bl_little_mock(url, request):
    """
    Mock for bundle lookup, small output.
    """
    littlebody = b'<?xml version="1.0" encoding="UTF-8"?><availableBundlesResponse version="1.0.0" sessionId="7762de1a-909c-4afb-88fe-57acb69e9049"><data authEchoTS="1366644680359"><status code="0"><friendlyMessage>Success</friendlyMessage><technicalMessage>Success</technicalMessage></status><content><bundle version="10.3.1.2726"><type>system:os</type><type>system:radio</type><type>application</type></bundle></content></data><signature><root><cipher>EC521R1</cipher><shaType>SHA512</shaType><sigR>AN80t5quXy/WiTy0Lw0llAIGmRVogdfRttDOCbWh6uUquvAvAt2YAN1OOCLJbOOFn5SppytUJi34wXOxiopv2RjX</sigR><sigS>APPbsvblhDzEhpef8wQBgxCrTJ851e/BeVBLUzlGG7ovy220QdQHeG8ahk9bMeoTmnIkWc6f/kCs+h7hGkel+OYT</sigS></root><chain ordinal="1"><cipher>EC521R1</cipher><shaType>SHA512</shaType><publicKey notValidUntil="1434252700605" notValidAfter="1434684700605">BAHbALLG0oyfF7ZvmxOjz1NFODaTEd9gvdqaqgSwuTi39Jv87q0ZWfY7kVSxWAyuumQYfIpy+9ruTd4z7cNvXJ0u8ACJvuo3xzNpgCah74Wpqcvr+EuNGkVe0IAZDXZSGPeZC739vkPitYiqJDP8joOuFTIdpUop/qJj+YckijR9RujdUw==</publicKey><sigR>Aaou0PAOGD7njwYckvvAGlepOmDSbRV2clsaskubz01+sQ9YlLhwctCAPS9n9kpdnnYbg2TDvh6XN3lUFgmfGvJl</sigR><sigS>AN34KjWeSGVIBz4KTlHzMGMpKfDKsOQPT5UVsy+tczBhKdAeDYGaU5Yc/YFaAOz7RuxjIbHkohuHESqDcXCnvif6</sigS></chain></signature></availableBundlesResponse>'
    return {'status_code': 200, 'content': littlebody}


@httmock.all_requests
def sr_good_mock(url, request):
    """
    Mock for software release lookup, SR found.
    """
    goodbody = b'<?xml version="1.0" encoding="UTF-8"?><srVersionLookupResponse version="2.0.0"><data authEchoTS="1366644680359"><status code="0"><friendlyMessage>Success</friendlyMessage><technicalMessage>Success</technicalMessage></status><content><softwareReleaseVersion>10.3.2.516</softwareReleaseVersion></content></data><signature><root><cipher>EC521R1</cipher><shaType>SHA512</shaType><sigR>QnnSA+ZMae96eC82GU+VNUFGPHsqD4n7MydOacSsEwygn2Fs+41jiXZpQ8mZ51ft4eTWAlmbdpecZMqlSPbaS/4=</sigR><sigS>AQlCb2Wk87R/jwMxQCP8jElfE88nzelzqmpyakkXokRhy8kkec67R6wQIek+TJvXRsxS6hHqIhjjA5wO/NWaM5Z0</sigS></root><chain ordinal="1"><cipher>EC521R1</cipher><shaType>SHA512</shaType><publicKey notValidUntil="1434253530830" notValidAfter="1434685530830">BACDEf0rUyqeoahFj57x02KvWvq8ztyl2ekJabpghmvv256KGhkuxTj6ugD6cvf6jYOIyjx6og0XRj/cnycNb1dhrwDNwOOB/qgE+RNWWDcUL8M/Lm2nyT+kru3IZ6MWBedYKine+dZHFpJk+x26QnXsEYgtMR4rCbIVC2Ooc8vCIV29rQ==</publicKey><sigR>APicruleHOD+jCsLmaSRIDePoyICdUBQkz/jq3tpyp1jnmN6K29r35UBnsYlGtnlUKscVg5uQbCSemO5+KWYa96R</sigR><sigS>ATzJc0Ev+2ep9eFgmtn6wdt+B2TAo1n3K5lvrfKGiyFrUNEbBdIejk3afL/IwKV3euSNx+iwHrscKtrrjWIfrTgB</sigS></chain></signature></srVersionLookupResponse>'
    return {'status_code': 200, 'content': goodbody}


@httmock.all_requests
def sr_bad_mock(url, request):
    """
    Mock for software release lookup, SR not found.
    """
    badbody = b'<?xml version="1.0" encoding="UTF-8"?><srVersionLookupResponse version="2.0.0"><data authEchoTS="1366644680359"><status code="0"><friendlyMessage>Success</friendlyMessage><technicalMessage>Success</technicalMessage></status><content><softwareReleaseVersion>SR not in system</softwareReleaseVersion></content></data><signature><root><cipher>EC521R1</cipher><shaType>SHA512</shaType><sigR>YMd1frOGcmTxawdRMnCsPB7C/x4xik5LyHVtsTBVPVl/id+yGT5vcLfcSL9z0g5HK0iGl99J4tCvlBO12+NTU7c=</sigR><sigS>AcbRzaMX6cQ/RGfk7m7tUora+W/nvBHonKJNpHuudYAoMbKRX0CofnNB9f2QXNiPZfSHpLYZ1YkuZ9cEHDmhCitD</sigS></root><chain ordinal="1"><cipher>EC521R1</cipher><shaType>SHA512</shaType><publicKey notValidUntil="1434251625739" notValidAfter="1434683625739">BAHxY5kl7VQ37IN1b1nWKCFGdc+s5Wm6VNLINp4rfUyfQavysqbn90Le+Q76J5CLaxXHVm+3ras0DqXT2s/6f+vBAgGWDNykX5Rc4m+J+0r2nw9XlERO0jDINNlPiz7SuIttP8UNgdQIHtyjPzdna7gvjfH3MBw/vQ4aUukklBHGakZVXA==</publicKey><sigR>AUjqIq5u1DTdz2pY68ChgP38rjRY5naKcBX4h6db8qfjdJTQZ5nEPB/2ujkouj8MQAB/Mx62aoGjG8X1acFR0oiK</sigR><sigS>AZ90jlOJis7nyLLLBT72oaFBzljw3v7F2MmiPS5H4VEytKoDjHX5lLrYcuVTspBTvBp68EzFHauWvJD74bVb4ciM</sigS></chain></signature></srVersionLookupResponse>'
    return {'status_code': 200, 'content': badbody}


@httmock.all_requests
def sr_fail_mock(url, request):
    """
    Mock for software release lookup, XML parse error.
    """
    badbody = b'<?xml version="1.0" encoding="UTF-8"?></srVersionLookupResponse>'
    return {'status_code': 200, 'content': badbody}


@httmock.all_requests
def md_base_mock(url, request):
    """
    Mock for metadata lookup.
    """
    thebody = b'bbndkext,10.2.0.1155,ndktargetrepo\nbbndkext,10.3.0.1172,ndktargetrepo\nbbndkext,10.2.1.1940,ndktargetrepo'
    return {'status_code': 200, 'content': thebody}


@httmock.all_requests
def da_mock(url, request):
    """
    Mock for Dev Alpha autoloader URL generation.
    """
    csize = "987654321" if "Snek" in request.url else "12345"
    code = 404 if "BB10" in request.url else 200
    headers = {'content-length': csize}
    return httmock.response(status_code=code, headers=headers)


@httmock.all_requests
def tcl_check_mock(url, request):
    """
    Mock for TCL update checking.
    """
    badbody = b'<?xml version="1.0" encoding="utf-8"?>\n<GOTU><UPDATE_DESC>0</UPDATE_DESC><ENCODING_ERROR>0</ENCODING_ERROR><CUREF>PRD-63764-001</CUREF><VERSION><TYPE>4</TYPE><FV>AAA000</FV><TV>AAM693</TV><SVN>20170717_173202</SVN><RELEASE_INFO><year>2017</year><month>07</month><day>17</day><hour>17</hour><minute>29</minute><second>20</second><timezone>GMT 8</timezone><publisher>jin.zeng.hz</publisher></RELEASE_INFO></VERSION><FIRMWARE><FW_ID>258098</FW_ID><FILESET_COUNT>1</FILESET_COUNT><FILESET><FILE><FILENAME>bbry_qc8953_sfi-user-production_signed-AAM693.zip</FILENAME><FILE_ID>261497</FILE_ID><SIZE>2712821341</SIZE><CHECKSUM>97a9f933c70fbe7c106037aaba19c6aedd9136d2</CHECKSUM><FILE_VERSION>1</FILE_VERSION><INDEX>0</INDEX></FILE></FILESET></FIRMWARE><DESCRIPTION/></GOTU>\n'
    return {'status_code': 200, 'content': badbody}


@httmock.all_requests
def tcl_request_mock(url, request):
    """
    Mock for TCL download URL request.
    """
    badbody = b'<?xml version="1.0" encoding="utf-8"?>\n<GOTU><FILE_LIST><FILE><FILE_ID>261497</FILE_ID><DOWNLOAD_URL>/ce570ddc079e2744558f191895e524d02a60476f/cfcdde91ea7f810311d1f973726e390f77a9ff1b/258098/261497</DOWNLOAD_URL></FILE></FILE_LIST><SLAVE_LIST><SLAVE>g2slave-ap-north-01.tctmobile.com</SLAVE><SLAVE>g2slave-ap-north-01.tctmobile.com</SLAVE><SLAVE>g2slave-eu-west-01.tctmobile.com</SLAVE><SLAVE>g2slave-eu-west-01.tctmobile.com</SLAVE><SLAVE>g2slave-us-east-01.tctmobile.com</SLAVE><SLAVE>g2slave-us-east-01.tctmobile.com</SLAVE></SLAVE_LIST></GOTU>\n'
    return {'status_code': 200, 'content': badbody}


@httmock.all_requests
def tcl_enc_good_mock(url, request):
    """
    Mock for TCL header checking, best case.
    """
    return httmock.response(status_code=206, headers={'content-length': 4194320})


@httmock.all_requests
def tcl_enc_bad_mock(url, rquest):
    """
    Mock for TCL header checking, worst case.
    """
    return httmock.response(status_code=400, headers={'content-length': 123456})


@httmock.all_requests
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
        urllist = ["http://google.com/{0}.dat".format(i) for i in ["idle", "cleese", "gilliam", "jones", "palin", "chapman"]]
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

    def test_download_bootstrap_fail(self):
        """
        Test multiple downloading, worst case.
        """
        urllist = ["http://google.com/{0}.dat".format(i) for i in ["idle", "cleese", "gilliam", "jones", "palin", "chapman"]]
        with mock.patch("concurrent.futures.ThreadPoolExecutor.submit", mock.MagicMock(side_effect=KeyboardInterrupt)):
            bn.download_bootstrap(urllist, workers=7)

    def test_download_android_tools(self):
        """
        Test downloading Android SDK platform tools.
        """
        os.mkdir("plattools")
        with httmock.HTTMock(download_mock):
            bn.download_android_tools()
        for zipf in os.listdir("plattools"):
            shahash = sha512()
            with open(os.path.join("plattools", zipf), 'rb') as file:
                while True:
                    data = file.read()
                    if not data:
                        break
                    shahash.update(data)
            print("{0}: {1}".format(zipf, shahash.hexdigest()))
            assert shahash.hexdigest() == "02c25df184ba5ed0eb7faa43b61fc2d0752a8230cc23d3f3085af55919198f83d1664277c6c4c00d78c0f95528fe8ab9f6dc145b8f9cc4b9a0f24482a1630bd9"
        rmtree("plattools", ignore_errors=True)

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

    def test_devalpha_export_bootstrap(self):
        """
        Test generating Dev Alpha URLs.
        """
        skels = ["Autoload-DevAlphaX-", "Autoload-DevAlphaSnek", "Autoload-SnekTL100-1-", "Autoload-<SERIES>-"]
        finals = {"http://downloads.blackberry.com/upr/developers/downloads/Autoload-DevAlphaX-10.2.3.4567.exe":"12345",
                  "http://downloads.blackberry.com/upr/developers/downloads/Autoload-SnekTL100-1-10.2.3.4567.exe":"987654321"}
        with httmock.HTTMock(da_mock):
            assert bn.dev_dupe_cleaner(bn.devalpha_urls_bootstrap("10.2.3.4567", skels)) == finals

    def test_devalpha_boostrap_fail(self):
        """
        Test failing to generate Dev Alpha URLs.
        """
        skels = ["Autoload-DevAlphaX-", "Autoload-DevAlphaSnek", "Autoload-SnekTL100-1-", "Autoload-<SERIES>-"]
        with mock.patch("bbarchivist.networkutils.devalpha_urls_bulk", mock.MagicMock(side_effect=KeyboardInterrupt)):
            bn.devalpha_urls_bootstrap("10.2.3.4567", skels)

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
            response = bn.carrier_checker(302, 220)
        assert response == ('Canada', 'TELUS (CA)')

    def test_carrier_checker_bad(self):
        """
        Test carrier checking, worst case.
        """
        with httmock.HTTMock(cc_bad_mock):
            response = bn.carrier_checker(666, 666)
        assert response == ('United States', 'default')

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

    def test_upd_req_upgrade(self):
        """
        Test carrier update request, upgrade.
        """
        with httmock.HTTMock(cq_upgrade_mock):
            alist = (
                "10.3.1.1877",
                "10.3.1.2726",
                "10.3.1.2727",
                [
                    'http://cdn.fs.sl.blackberry.com/fs/qnx/production/f6832b88958f1c4c3f9bbfd44762e0c516760d8a/com.qnx.qcfm.radio.qc8960.wtr5/10.3.1.2727/qc8960.wtr5-10.3.1.2727-nto+armle-v7+signed.bar',
                    'http://cdn.fs.sl.blackberry.com/fs/qnx/production/f6832b88958f1c4c3f9bbfd44762e0c516760d8a/com.qnx.coreos.qcfm.os.qc8960.factory_sfi/10.3.1.2726/qc8960.factory_sfi-10.3.1.2726-nto+armle-v7+signed.bar'
                ]
            )
            assert bn.carrier_query(302220, "6002E0A", upgrade=True) == alist

    def test_upd_req_blitz(self):
        """
        Test carrier update request, blitz.
        """
        with httmock.HTTMock(cq_blitz_mock):
            alist = (
                "10.3.1.1877",
                "10.3.1.2726",
                "",
                [
                    'http://cdn.fs.sl.blackberry.com/fs/qnx/production/f6832b88958f1c4c3f9bbfd44762e0c516760d8a/com.qnx.qcfm.radio.qc8960.wtr5/10.3.1.2727/qc8960.wtr5-10.3.1.2727-nto+armle-v7+signed.bar'
                ]
            )
            assert bn.carrier_query(302220, "6002E0A", blitz=True) == alist

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

    def test_sr_lookup_bootstrap_filtered(self):
        """
        Test multiple software lookups, with filter.
        """
        with httmock.HTTMock(sr_good_mock):
            findings = bn.sr_lookup_bootstrap("10.3.2.798", no2=True)
            for key in findings:
                assert findings[key] == "10.3.2.516"

    def test_sr_boostrap_fail(self):
        """
        Test multiple software lookups, worst case.
        """
        with mock.patch("bbarchivist.networkutils.sr_lookup", mock.MagicMock(side_effect=KeyboardInterrupt)):
            bn.sr_lookup_bootstrap("10.3.2.798")

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
            assert "10.3.3.2205" in results[0]

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
            results = bn.droid_scanner("AAD250", "Priv")
            assert "user-common-AAD250" in results[0]


    def test_autoloader_scan_bad(self):
        """
        Test Android autoloader lookup, worst case.
        """
        with httmock.HTTMock(pa_bad_mock):
            results = bn.droid_scanner("AAD250", "Priv")
            assert results is None

    def test_autoloader_scan_bbm(self):
        """
        Test Android autoloader lookup, new site.
        """
        with httmock.HTTMock(pa_bbm_mock):
            results = bn.droid_scanner("AAL093", "KEYone")
            assert "user-common-AAL093" in results[0]

    def test_autoloader_scan_hash(self):
        """
        Test Android autoloader hash lookup.
        """
        with httmock.HTTMock(pa_hash_mock):
            results = bn.droid_scanner("AAD250", "Priv", "sha256")
            assert "user-common-AAD250" in results[0]

    def test_autoloader_scan_hash_bbm(self):
        """
        Test Android autoloader hash lookup, new site.
        """
        with httmock.HTTMock(pa_bbm_hash_mock):
            results = bn.droid_scanner("AAL093", "KEYone", "sha512")
            assert "user-common-AAL093" in results[0]

    def test_autoloader_scan_list(self):
        """
        Test Android autoloader lookup, list of devices.
        """
        with httmock.HTTMock(pa_good_mock):
            results = bn.droid_scanner("AAD250", ["Priv"])
            assert "user-common-AAD250" in results[0]

    def test_metadata_ndk(self):
        """
        Test grabbing old-style metadata.
        """
        with httmock.HTTMock(md_base_mock):
            results = bn.ndk_metadata()
            assert "1940" in results[1]

    def test_metadata_new(self):
        """
        Test grabbing new-style metadata, simulator.
        """
        with httmock.HTTMock(md_base_mock):
            res1 = bn.sim_metadata()
            assert "1172" in res1[1]
            res2 = bn.runtime_metadata()
            assert "1155" in res2[0]

    def test_loader_scraper(self, capsys):
        """
        Test loader checking.
        """
        with httmock.HTTMock(ls_mock):
            bn.loader_page_scraper()
            assert "BlackBerry common SW for STH100-1 & STH100-2 devices\n    AAG326: https://bbapps.download.blackberry.com/Priv/bbry_qc8952_64_sfi_autoloader_user-common-AAG326.zip" in capsys.readouterr()[0]


class TestClassNetworkutilsTcl:
    """
    Test functions that are used for checking for Android updates.
    """

    def test_tcl_check(self):
        """
        Test checking for Android updates.
        """
        with httmock.HTTMock(tcl_check_mock):
            ctxt = bn.tcl_check("PRD-63764-001", export=True)
        tv, fw, fn, fs, fh = bn.parse_tcl_check(ctxt)
        assert tv == "AAM693"
        assert fw == "258098"
        assert fn == "bbry_qc8953_sfi-user-production_signed-AAM693.zip"
        assert fs == "2712821341"
        assert fh == "97a9f933c70fbe7c106037aaba19c6aedd9136d2"

    def test_tcl_check_fail(self):
        """
        Test checking for Android updates, worst case.
        """
        with httmock.HTTMock(pa_bad_mock):
            ctxt = bn.tcl_check("PRD-63764-001")
        assert ctxt is None

    def test_tcl_request(self):
        """
        Test checking for Android update URLs.
        """
        with httmock.HTTMock(tcl_request_mock):
            salt = bn.tcl_salt()
            vkh = bn.vkhash("PRD-63764-001", "AAM693", "258098", salt)
            utxt = bn.tcl_download_request("PRD-63764-001", "AAM693", "258098", salt, vkh, export=True)
        dlurl, encslave = bn.parse_tcl_download_request(utxt)
        assert "/ce570ddc079e2744558f191895e524d02a60476f/cfcdde91ea7f810311d1f973726e390f77a9ff1b/258098/261497" in dlurl

    def test_tcl_request_fail(self):
        """
        Test checking for Android update URLs, worst case.
        """
        with httmock.HTTMock(pa_bad_mock):
            salt = bn.tcl_salt()
            vkh = bn.vkhash("PRD-63764-001", "AAM693", "258098", salt)
            utxt = bn.tcl_download_request("PRD-63764-001", "AAM693", "258098", salt, vkh)
        assert utxt is None

    def test_tcl_encheader(self):
        """
        Test checking header, best case.
        """
        with httmock.HTTMock(tcl_enc_good_mock):
            sentinel = bn.encrypt_header("http://snek.com/snek/update.zip", "snek.com")
        assert sentinel == "HEADER FOUND"

    def test_tcl_encheader_fail(self):
        """
        Test checking header, worst case.
        """
        with httmock.HTTMock(tcl_enc_bad_mock):
            sentinel = bn.encrypt_header("http://snek.com/snek/update.zip", "snek.com")
        assert sentinel is None
