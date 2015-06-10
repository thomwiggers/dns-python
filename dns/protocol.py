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


def _pack_name(name):
    """Pack names along DNS specs

    >>> _pack_name('foo.com')
    bytearray(b'\\x03foo\\x03com\\x00')
    """
    b = bytearray()
    for part in name.strip('.').split('.'):
        b.append(len(part))
        b += bytearray(part, 'ascii')
    b.append(0)
    return b


class DNSHeaderFlags(object):
    """A wrapper for DNS Header flags"""

    def __init__(self):
        self.is_response = False
        self.opcode = 0  # 0-15
        self.is_authorative_answer = False
        self.is_truncated = False
        self.recursion_desired = False
        self.recursion_available = False
        self.response_code = 0

    def pack_struct(self):
        flags = 0
        flags |= (1 if self.is_response else 0) << 15
        flags |= (self.opcode % 16) << 11
        flags |= (1 if self.is_authorative_answer else 0) << 10
        flags |= (1 if self.is_truncated else 0) << 9
        flags |= (1 if self.recursion_desired else 0) << 8
        flags |= (1 if self.recursion_available else 0) << 7
        flags |= self.response_code % 15

        return struct.pack("!H", flags)

    @classmethod
    def from_struct(cls, struct_):
        obj = struct.unpack_from("!H", struct_)
        flags = obj[0]
        this = cls()
        this.is_response = (flags & 0x8000) > 0
        this.opcode = (flags & 0x7800) >> 11
        this.is_authorative_answer = (flags & 0x0400) > 0
        this.is_truncated = (flags & 0x0200) > 0
        this.recursion_desired = (flags & 0x0100) > 0
        this.recursion_available = (flags & 0x0080) > 0
        this.response_code = (flags & 0x000f)
        return this


class DNSPacket(object):
    """A DNS Packet"""

    def __init__(self):
        self.is_query = False
        self.questions = []
        self.answers = []
        self.authorities = []
        self.additional = []
        self.identifier = -1
        self.flags = DNSHeaderFlags()

    def from_struct(self, struct_):
        raise NotImplementedError('TODO')

    def pack_struct(self):
        return self._craft_header()

    def _craft_header(self):
        id = struct.pack("!H", self.identifier)
        flags = self.flags.pack_struct()
        header_rest = struct.pack(
            "!HHHH",
            len(self.questions),
            len(self.answers),
            len(self.authorities),
            len(self.additional))

        return id + flags + header_rest


class RecursiveDNSMessage(DNSPacket):
    """A packet for a recursive DNS query"""

    def __init__(self):
        super(RecursiveDNSMessage, self).__init__()
        self.flags.recursion_desired = True


class Question(object):

    def __init__(self, qname=None, qtype=None, qclass=QUERY_CLASS_IN):
        self.qname = qname  # domain name
        self.qtype = qtype  # query type
        self.qclass = qclass

    def pack_struct(self):
        return _pack_name(self.qname) + struct.pack('!HH',
                                                    self.qtype,
                                                    self.qclass)


class ResourceRecord(object):

    def __init__(self, name=None, ttl=None, rdata=None):
        self.name = name  # domain name
        self.class_ = QUERY_CLASS_IN  # query class
        self.ttl = ttl  # time to live in seconds
        self.rdata = rdata  # resource data

    @classmethod
    def from_struct(cls, name, struct_):
        """Construct a ResourceRecord subclass from a struct. The name
        needs to have already been unpacked.
        """
        name = name
        (type_, class_, ttl, rdlength) = struct.unpack_from('!HHLH', struct_)
        rdata = struct_[10:10+rdlength]

        assert class_ == QUERY_CLASS_IN, "Only the internet class is supported"

        if type_ == QUERY_TYPE_A:
            return ARecord(name=name, ttl=ttl, rdata=rdata)
        elif type_ == QUERY_TYPE_CNAME:
            return CNAMERecord(name=name, ttl=ttl, rdata=rdata)

        raise NotImplementedError("Got a resource type we don't understand")

    def _uncompress(self):
        pass
        # see 4.1.4

    def pack_struct(self):
        return (_pack_name(self.name) +
                struct.pack('!HHlH',
                            self.type,
                            self.class_,
                            self.ttl,
                            len(self.rdata)
                            ) + self.pack_rdata())


class ARecord(ResourceRecord):

    type_ = QUERY_TYPE_A

    def __init__(self, address=None, *args, **kwargs):
        super(ARecord, self).__init__(*args, **kwargs)
        self.address = address  # as sbtring, eg. 127.0.0.1

    def get_address(self):
        """ See section 3.4.1 TODO"""
        if not self.address:
            self.address = '.'.join(
                map(str, struct.unpack_from('!bbbb', self.rdata)))
        return self.address

    def pack_rdata(self):
        if self.rdata:
            return self.rdata
        return struct.pack('bbbb', *list(map(int, self.address.split('.'))))


class CNAMERecord(ResourceRecord):

    type_ = QUERY_TYPE_CNAME

    def __init__(self, *args, **kwargs):
        super(CNAMERecord, self).__init__(*args, **kwargs)

    def get_cname(self):
        raise NotImplementedError("Not yet implemented")
