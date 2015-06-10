from __future__ import unicode_literals

import unittest
import struct

from dns.protocol import (ResourceRecord, ARecord, CNAMERecord, QUERY_TYPE_A,
                          QUERY_TYPE_CNAME, QUERY_CLASS_IN)


class ResourceRecordTest(unittest.TestCase):
    """Test our resource records"""

    def test_arecord_from_struct(self):
        struct_ = struct.pack('!HHLH',
                              QUERY_TYPE_A,
                              QUERY_CLASS_IN,
                              42,
                              12)
        struct_ += bytearray(b'foobarbazbiz')
        name = "thomwiggers.nl"
        instance = ResourceRecord.from_struct(name, struct_)

        assert isinstance(instance, ARecord)
        assert instance.type_ == QUERY_TYPE_A
        assert instance.ttl == 42
        assert instance.rdata == bytearray(b'foobarbazbiz')

    def test_cname_from_struct(self):
        struct_ = struct.pack('!HHLH',
                              QUERY_TYPE_CNAME,
                              QUERY_CLASS_IN,
                              42,
                              12)
        struct_ += bytearray(b'foobarbazbiz')
        name = "thomwiggers.nl"
        instance = ResourceRecord.from_struct(name, struct_)

        assert isinstance(instance, CNAMERecord)
        assert instance.type_ == QUERY_TYPE_CNAME
        assert instance.ttl == 42
        assert instance.rdata == bytearray(b'foobarbazbiz')
