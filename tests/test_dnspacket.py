import unittest
from dns.protocol import (Question, Type, DNSHeaderFlags,
                          ARecord, DNSPacket)
import struct


class DNSPacketTest(unittest.TestCase):

    def test_from_struct(self):
        flags = DNSHeaderFlags()
        flags.is_response = True
        flags.opcode = 1
        flags.is_authorative_answer = 1
        packet = struct.pack('!H', id(self) & 0xffff)
        packet += flags.pack_struct()
        packet += struct.pack('!HHHH', 1, 1, 1, 1)

        q = Question(qname='test.com', qtype=Type.A)
        packet += q.pack_struct()

        a = ARecord(name='foo.com', address='127.0.0.1', ttl=123)
        packet += a.pack_struct()
        packet += a.pack_struct()
        packet += a.pack_struct()

        p = DNSPacket.from_struct(packet)
        assert p.flags.is_response
        assert len(p.questions) == 1
        assert len(p.answers) == 1
        assert len(p.authorities) == 1
        assert len(p.additional) == 1

        assert p.questions[0].qname == 'test.com.'
        assert p.questions[0].qtype == Type.A

        for item in (p.answers, p.authorities, p.additional):
            item[0].name == 'foo.com.'
            item[0].address == '127.0.0.1'
            item[0].ttl == 123
