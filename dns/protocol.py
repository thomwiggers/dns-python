from __future__ import print_function, unicode_literals
import struct

QUERY_CLASS_IN = 1

QUERY_TYPE_A = 1
QUERY_TYPE_AAAA = 28
QUERY_TYPE_CNAME = 5
QUERY_TYPE_MX = 15
QUERY_TYPE_NS = 2
QUERY_TYPE_SOA = 6
QUERY_TYPE_SRV = 33
QUERY_TYPE_TXT = 16


class DNSPacket(object):
    """A DNS Packet"""

    def __init__(self):
        self.questions = []
        self.answers = []
        self.authorities = []
        self.additional = []
        self.identifier = -1

    def pack_struct(self):
        return self._craft_header() 
    
    def _craft_header(self):
        return struct.pack("HHHHHH", 
                self.identifier,
                self._craft_flags(),
                len(self.questions),
                len(self.answers),
                len(self.authorities),
                len(self.additional)
        )

    def _craft_flags(self):
        return


class RecursiveDNSQuery(DNSPacket):
    """A packet for a recursive DNS query"""
    
    def _craft_flags(self):
        return 0x0100

class Question(object):

    def __init__(self):
        self.qname = None  # domain name
        self.qtype = None  # query type
        self.qclass = QUERY_CLASS_IN


class ResourceRecord(object):

    def __init__(self):
        self.name = None  # domain name
        self.type = None  # query type
        self.class_ = QUERY_CLASS_IN  # query class
        self.ttl = None  # time to live in seconds
        self.rdata = None  # resource data

    def _uncompress(self):
        pass
        # see 4.1.4


class ARecord(ResourceRecord):

    def __init__(self):
        super(ARecord, self).__init__()

    def get_address(self):
        """ See section 3.4.1 TODO"""
        raise NotImplementedError("Not yet implemented")


class CNAMERecord(ResourceRecord):
    def __init__(self):
        super(ARecord, self).__init__()

    def get_cname(self):
        raise NotImplementedError("Not yet implemented")
