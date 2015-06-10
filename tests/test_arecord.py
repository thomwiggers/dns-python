import unittest

from socket import inet_aton, inet_ntoa
from dns.protocol import ARecord


class ARecordTest(unittest.TestCase):

    def test_get_address_has_address(self):
        record = ARecord(address='127.0.0.1')
        assert record.address == '127.0.0.1'

    def test_get_address_from_rdata(self):
        record = ARecord()
        record.rdata = inet_aton('127.0.0.1')
        assert record.address == '127.0.0.1'

    def test_pack_rdata(self):
        record = ARecord(address='127.0.0.1')
        assert inet_ntoa(record.pack_rdata()) == '127.0.0.1'
