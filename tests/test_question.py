import unittest
from dns.protocol import Question, QUERY_TYPE_A, QUERY_CLASS_IN
import struct


class TestQuestion(unittest.TestCase):

    def test_constructor(self):
        q = Question('foo.bar.com', QUERY_TYPE_A)
        assert q.qname == 'foo.bar.com'
        assert q.qtype == QUERY_TYPE_A
        assert q.qclass == QUERY_CLASS_IN

    def test_to_struct(self):
        q = Question('foo.bar.com', QUERY_TYPE_A)
        bytestuff = q.pack_struct()

        assert bytestuff[:13] == bytearray(b'\x03foo\x03bar\x03com\x00')
        qtype, qclass = struct.unpack_from('!HH', bytestuff, offset=13)
        assert qtype == QUERY_TYPE_A
        assert qclass == QUERY_CLASS_IN

    def test_from_struct(self):
        q = Question.from_struct('foobar.com', struct.pack('!HH',
                                                           QUERY_TYPE_A,
                                                           QUERY_CLASS_IN))[0]

        assert q.qname == 'foobar.com'
        assert q.qtype == QUERY_TYPE_A
        assert q.qclass == QUERY_CLASS_IN
