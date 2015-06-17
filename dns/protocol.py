from __future__ import print_function, unicode_literals

from socket import inet_ntoa, inet_aton
import struct


QUERY_CLASS_IN = 1


class Type(object):
    A = 1
    NS = 2
    MD = 3
    MF = 4
    CNAME = 5
    SOA = 6
    MB = 7
    MG = 8
    MR = 9
    NULL = 10
    WKS = 11
    PTR = 12
    HINFO = 13
    MINFO = 14
    MX = 15
    TXT = 16


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


def _extract_string(data, blob):
    r"""Extract a string from the blob

    >>> _extract_string(b'\x04test\x02nl\x00test', b'') == \
    ... (u'test.nl.', bytearray(b'test'))
    True
    >>> _extract_string(b'\x04test\xc0\x00test',
    ...                 b'\x09fietsband\x00') == \
    ... (u'test.fietsband.', bytearray(b'test'))
    True

    """
    string = ''
    data = bytearray(data)
    while data and data[0] != 0:
        if data[0] & 0xc0:
            offset = (data[0] ^ 0xc0) + data[1]
            string += _extract_string(blob[offset:], blob)[0]
            data = data[2:]
            return (string, data)
        else:
            string += data[1:1+data[0]].decode('ascii') + '.'
            data = data[1+data[0]:]

    return (string, data[1:] if data else b'')


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
        (flags, ) = struct.unpack_from("!H", struct_)
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

    @classmethod
    def from_struct(cls, struct_):
        """Create a DNSPacket object from a struct"""
        packet = cls()
        (packet.identifier, _, qdcount,
         ancount, nscount, arcount) = struct.unpack_from('!HHHHHH', struct_)
        packet.flags = DNSHeaderFlags.from_struct(struct_[2:4])

        data = struct_[12:]
        for i in range(qdcount):
            (name, data) = _extract_string(data, struct_)
            (q, data) = Question.from_struct(name, data)
            packet.questions.append(q)

        for i in range(ancount):
            (name, data) = _extract_string(data, struct_)
            (rr, data) = ResourceRecord.from_struct(name, data, struct_)
            packet.answers.append(rr)

        for i in range(nscount):
            (name, data) = _extract_string(data, struct_)
            (rr, data) = ResourceRecord.from_struct(name, data, struct_)
            packet.authorities.append(rr)

        for i in range(arcount):
            (name, data) = _extract_string(data, struct_)
            (rr, data) = ResourceRecord.from_struct(name, data, struct_)
            packet.additional.append(rr)

        return packet

    def pack_struct(self):
        """Pack this packet up"""
        header = self._craft_header()
        body = bytearray()
        for item in (self.questions
                     + self.answers
                     + self.authorities
                     + self.additional):
            body += item.pack_struct()

        return header + body

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
    """DNS Question object"""

    size = 4

    def __init__(self, qname=None, qtype=None, qclass=QUERY_CLASS_IN):
        """Construct a new question"""
        self.qname = qname  # domain name
        self.qtype = qtype  # query type
        self.qclass = qclass

    @classmethod
    def from_struct(cls, name, struct_):
        """Transform a struct (without the name) into a question."""
        (type_, class_) = struct.unpack_from('!HH', struct_)
        return (cls(qname=name, qtype=type_, qclass=class_), struct_[4:])

    def pack_struct(self):
        return _pack_name(self.qname) + struct.pack('!HH',
                                                    self.qtype,
                                                    self.qclass)


class ResourceRecord(object):
    """Resourcerecord parent class"""

    def __init__(self, name=None, ttl=None, rdata=None):
        self.name = name  # domain name
        self.class_ = QUERY_CLASS_IN  # query class
        self.ttl = ttl  # time to live in seconds
        self.rdata = rdata  # resource data

    @classmethod
    def from_struct(cls, name, struct_, blob):
        """Construct a ResourceRecord subclass from a struct. The name
        needs to have already been unpacked.
        """
        (type_, class_, ttl, rdlength) = struct.unpack_from('!HHlH', struct_)
        rdata = struct_[10:10+rdlength]

        assert class_ == QUERY_CLASS_IN, "Only the internet class is supported"

        if type_ == Type.A:
            record = ARecord(name=name, ttl=ttl, rdata=rdata)
        elif type_ == Type.CNAME:
            record = CNAMERecord(blob, name=name, ttl=ttl, rdata=rdata)
        elif type_ == Type.NS:
            record = NSRecord(blob, name=name, ttl=ttl, rdata=rdata)
        else:
            raise NotImplementedError(
                "Got a resource type we don't understand")

        return (record, struct_[10+rdlength:])

    def pack_struct(self):
        return (_pack_name(self.name) +
                struct.pack('!HHlH',
                            self.type_,
                            self.class_,
                            self.ttl,
                            len(self.pack_rdata())
                            ) + self.pack_rdata())


class ARecord(ResourceRecord):
    """DNS A Record"""

    type_ = Type.A
    size = 4

    def __init__(self, address=None, *args, **kwargs):
        """Construct a new A record"""
        super(ARecord, self).__init__(*args, **kwargs)
        self._address = address  # as string, eg. 127.0.0.1

    @property
    def address(self):
        """Get an address"""
        if self._address is None and self.rdata is not None:
            rdata = self.rdata
            if isinstance(rdata, bytearray):
                rdata = rdata.decode('latin1').encode('latin1')
            self._address = inet_ntoa(rdata)
            return self._address
        elif self._address is not None:
            return self._address
        else:
            raise ValueError("No address and no rdata?!")

    def pack_rdata(self):
        """Pack the object as rdata"""
        if self.rdata:
            return self.rdata
        return inet_aton(self._address)


class NSRecord(ResourceRecord):
    """DNS NS Record"""
    type_ = Type.NS

    def __init__(self, _struct, nsdname=None, *args, **kwargs):
        """Construct a NS record"""
        super(NSRecord, self).__init__(*args, **kwargs)
        self._nsdname = nsdname
        self._struct = _struct

    @property
    def nsdname(self):
        """Get nsd data"""
        if self._nsdname is None and self.rdata is not None:
            rdata = self.rdata
            if isinstance(rdata, bytearray):
                rdata = rdata.decode('latin1').encode('latin1')
            self._nsdname = _extract_string(rdata, self._struct)
        elif self._nsdname is not None:
            return self._nsdname
        else:
            return ValueError("No NSDName and no rdata?!")


class CNAMERecord(ResourceRecord):
    """DNS CNAME Record"""
    type_ = Type.CNAME

    def __init__(self, _struct, *args, **kwargs):
        super(CNAMERecord, self).__init__(*args, **kwargs)
        self._struct = _struct
        self._cname = None

    @property
    def cname(self):
        if self._cname is None and self.rdata is not None:
            rdata = self.rdata
            if isinstance(rdata, bytearray):
                rdata = rdata.decode('latin1').encode('latin1')
            (self._cname, data) = _extract_string(rdata, self._struct)
            return self._cname
        elif self._cname is not None:
            return self._cname
        else:
            return ValueError("No CName and no rdata?!")


    @property
    def size(self):
        return len(self.get_rdata())

    def pack_rdata(self):
        raise NotImplementedError("Not yet implemented")
