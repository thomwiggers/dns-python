from __future__ import unicode_literals

import unittest
import struct

from dns.protocol import (ResourceRecord, ARecord, CNAMERecord, Type,
                          QUERY_CLASS_IN)


class ResourceRecordTest(unittest.TestCase):
    """Test our resource records"""

    def test_arecord_from_struct(self):
        struct_ = struct.pack('!HHlH',
                              Type.A.value,
                              QUERY_CLASS_IN,
                              42,
                              12)
        struct_ += bytearray(b'foobarbazbiz')
        name = "thomwiggers.nl"
        (instance, x) = ResourceRecord.from_struct(name, struct_, b'')

        assert len(x) == 0
        assert isinstance(instance, ARecord)
        assert instance.type_ == Type.A
        assert instance.ttl == 42
        assert instance.rdata == bytearray(b'foobarbazbiz')

    def test_cname_from_struct(self):
        struct_ = struct.pack('!HHlH',
                              Type.CNAME.value,
                              QUERY_CLASS_IN,
                              42,
                              12)
        struct_ += bytearray(b'foobarbazbiz')
        name = "thomwiggers.nl"
        (instance, x) = ResourceRecord.from_struct(name, struct_, b'')

        assert len(x) == 0
        assert isinstance(instance, CNAMERecord)
        assert instance.type_ == Type.CNAME
        assert instance.ttl == 42
        assert instance.rdata == bytearray(b'foobarbazbiz')
