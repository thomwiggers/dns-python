import unittest
from dns.protocol import Question, Type, QUERY_CLASS_IN
import struct


class TestQuestion(unittest.TestCase):

    def test_constructor(self):
        q = Question('foo.bar.com', Type.A)
        assert q.qname == 'foo.bar.com'
        assert q.qtype == Type.A
        assert q.qclass == QUERY_CLASS_IN

    def test_to_struct(self):
        q = Question('foo.bar.com', Type.A)
        bytestuff = q.pack_struct()

        assert bytestuff[:13] == bytearray(b'\x03foo\x03bar\x03com\x00')
        qtype, qclass = struct.unpack_from('!HH', bytestuff, offset=13)
        assert qtype == Type.A.value
        assert qclass == QUERY_CLASS_IN

    def test_from_struct(self):
        q = Question.from_struct('foobar.com', struct.pack('!HH',
                                                           Type.A.value,
                                                           QUERY_CLASS_IN))[0]

        assert q.qname == 'foobar.com'
        assert q.qtype == Type.A
        assert q.qclass == QUERY_CLASS_IN
