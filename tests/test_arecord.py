import unittest

import struct
from socket import inet_aton, inet_ntoa
from dns.protocol import ARecord, QUERY_TYPE_A, QUERY_CLASS_IN


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

    def test_pack_struct(self):
        record = ARecord(name='test.com', address='127.0.0.1', ttl=123)
        struct_ = record.pack_struct()
        packed_name = bytearray(b'\x04test\x03com\x00')

        assert struct_[:len(packed_name)] == packed_name

        data = struct_[len(packed_name):]

        (type_, class_, ttl, length) = struct.unpack_from('!HHlH', data)
        assert type_ == QUERY_TYPE_A
        assert class_ == QUERY_CLASS_IN
        assert ttl == 123
        assert length == 4
