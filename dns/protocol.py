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
        self.is_query = False
        self.questions = []
        self.answers = []
        self.authorities = []
        self.additional = []
        self.identifier = -1

    def from_struct(self, struct_):
        raise NotImplementedError('TODO')

    def pack_struct(self):
        return self._craft_header()

    def _craft_header(self):
        return struct.pack("!HHHHHH",
                           self.identifier,
                           self._craft_flags(),
                           len(self.questions),
                           len(self.answers),
                           len(self.authorities),
                           len(self.additional))

    def _craft_flags(self):
        flags = 0
        if self.is_query:
            flags |= 0b10000000
        flags <<= 8  # upper 8 bits
        return flags


class RecursiveDNSMessage(DNSPacket):
    """A packet for a recursive DNS query"""

    def _craft_flags(self):
        flags = super(RecursiveDNSMessage, self)._craft_flags()
        # set recursive flag
        flags |= 1 << 8  # set on pos 7, so 15-7 = 8
        return flags


class Question(object):

    def __init__(self, qname=None, qtype=None, qclass=QUERY_CLASS_IN):
        self.qname = qname  # domain name
        self.qtype = qtype  # query type
        self.qclass = qclass

    def pack_struct(self):
        return self._pack_names() + struct.pack('!HH', self.qtype, self.qclass)

    def _pack_names(self):
        qname = bytearray()
        for part in self.qname.split('.'):
            qname.append(len(part))
            qname += bytearray(part, 'ascii')
        qname.append(0)
        return qname


class ResourceRecord(object):

    def __init__(self):
        self.name = None  # domain name
        self.type = None  # query type
        self.class_ = QUERY_CLASS_IN  # query class
        self.ttl = None  # time to live in seconds
        self.rdata = None  # resource data

    @classmethod
    def from_struct(self, struct_):
        """Construct a ResourceRecord subclass from a struct"""
        raise NotImplementedError('TODO')

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
        super(CNAMERecord, self).__init__()

    def get_cname(self):
        raise NotImplementedError("Not yet implemented")
