import unittest
from dns.protocol import DNSHeaderFlags
import struct


class TestHeaderFlags(unittest.TestCase):

    def test_pack_struct_empty_header(self):
        flags = DNSHeaderFlags()
        bytestuff = struct.unpack_from("!H", flags.pack_struct())
        byteflags = bytestuff[0]
        assert byteflags == 0x0000

    def test_pack_struct(self):
        flags = DNSHeaderFlags()
        flags.is_response = True
        flags.recursion_desired = True
        flags.opcode = 7
        flags.response_code = 12
        flags.is_authorative_answer = True

        bytestuff = struct.unpack_from("!H", flags.pack_struct())
        byteflags = bytestuff[0]

        assert byteflags == 0b1011110100001100

    def test_from_struct(self):
        byteflags = 0b1011110100001100
        obj = struct.pack("!H", byteflags)

        flags = DNSHeaderFlags.from_struct(obj)
        assert flags.is_response
        assert flags.recursion_desired
        assert flags.opcode == 7
        assert flags.response_code == 12
        assert flags.is_authorative_answer
