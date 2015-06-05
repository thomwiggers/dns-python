import unittest
from dns.protocol import DNSPacket 
import struct

#assumption: all dns packets are queries
class TestDnsPacketQueryHeader(unittest.TestCase):
    def _get_header(self):
        dnspacket = DNSPacket(3)
        header = struct.unpack_from("HH", dnspacket.pack_struct())
        return header

    def test_has_id(self):
        header = self._get_header()
        
        assert header[0] == 3

    def test_packet_is_query(self):
        header = self._get_header()

        flags = header[1]
        qr = flags & 0x8000  
        assert qr == 0x0000

    def test_opcode_is_0(self):
        header = self._get_header()

        flags = header[1]
        rcode = flags & 0x7800 
        assert rcode == 0x0000

    def test_aa_is_0(self):
        header = self._get_header()

        flags = header[1]
        aa = flags & 0x0400
        assert aa == 0x0000

    def test_tc_is_0(self):
        header = self._get_header()

        flags = header[1]
        tc = flags & 0x0200
        assert tc == 0x0000

    def test_recursion_is_desired(self):
        header = self._get_header()

        flags = header[1]
        rd = flags & 0x0100
        assert rd == 0x0100

    def test_ra_is_0(self):
        header = self._get_header()

        flags = header[1]
        ra = flags & 0x0080
        assert ra == 0x0000

    def test_z_is_0(self):
        header = self._get_header()
       
        flags = header[1]
        z = flags & 0x0040
        assert z == 0x0000

    def test_ad_is_0(self):
        header = self._get_header()

        flags = header[1]
        ad = flags & 0x0020
        assert ad == 0x0000

    def test_cd_is_0(self):
        header = self._get_header()

        flags = header[1]
        cd = flags & 0x0010
        assert cd == 0x0000

    def test_rcode_is_0(self):
        header = self._get_header()

        flags = header[1]
        rcode = flags & 0x000f
        assert rcode == 0x0000
