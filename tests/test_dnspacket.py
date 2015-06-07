import unittest
from dns.protocol import RecursiveDNSMessage, Question
import struct


# assumption: all dns packets are queries
class TestRecursiveDNSMessageHeader(unittest.TestCase):
    def _get_header(self):
        dnspacket = RecursiveDNSMessage()
        dnspacket.identifier = 3
        dnspacket.questions.append(Question())
        dnspacket.questions.append(Question())
        header = struct.unpack_from("!HHHHHH", dnspacket.pack_struct())
        return header

    def test_has_id(self):
        header = self._get_header()
        assert header[0] == 3

    def test_packet_is_query(self):
        header = self._get_header()

        flags = header[1]
        qr = flags & 0x8000
        assert qr == 0

    def test_opcode_is_0(self):
        header = self._get_header()

        flags = header[1]
        rcode = flags & (0b01111000 << 8)
        assert rcode == 0

    def test_aa_is_0(self):
        header = self._get_header()

        flags = header[1]
        aa = flags & 0x0400
        assert aa == 0

    def test_tc_is_0(self):
        header = self._get_header()

        flags = header[1]
        tc = flags & 0x0200
        assert tc == 0

    def test_recursion_is_desired(self):
        header = self._get_header()

        flags = header[1]
        rd = flags & (1 << 8)
        assert rd > 0

    def test_ra_is_0(self):
        header = self._get_header()

        flags = header[1]
        ra = flags & 0b10000000
        assert ra == 0

    def test_z_is_0(self):
        header = self._get_header()

        flags = header[1]
        z = flags & 0b01110000
        assert z == 0

    def test_rcode_is_0(self):
        header = self._get_header()

        flags = header[1]
        rcode = flags & 0b00001111
        assert rcode == 0

    def test_num_count_sections(self):
        header = self._get_header()
        assert header[2] == 2
        assert header[3] == 0
        assert header[4] == 0
        assert header[5] == 0
