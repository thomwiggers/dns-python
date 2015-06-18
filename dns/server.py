# -*- coding: utf8 -*-

from __future__ import print_function, absolute_import

import asyncio
import random
import sys

import protocol
from client import resolve_question

caching = False

cache = {
    'a.root-servers.net': [
        {'type': 'A', 'address': '198.41.0.4', 'ttl': 3600000}],
    'b.root-servers.net': [
        {'type': 'A', 'address': '192.228.79.201', 'ttl': 3600000}],
    'c.root-servers.net': [
        {'type': 'A', 'address': '192.33.4.12', 'ttl': 3600000}],
    'd.root-servers.net': [
        {'type': 'A', 'address': '199.7.91.13', 'ttl': 3600000}],
    'e.root-servers.net': [
        {'type': 'A', 'address': '192.203.230.10', 'ttl': 3600000}],
    'f.root-servers.net': [
        {'type': 'A', 'address': '192.5.5.241', 'ttl': 3600000}],
    'g.root-servers.net': [
        {'type': 'A', 'address': '192.36.148.17', 'ttl': 3600000}],
    'h.root-servers.net': [
        {'type': 'A', 'address': '192.36.148.17', 'ttl': 3600000}],
    'i.root-servers.net': [
        {'type': 'A', 'address': '192.36.148.17', 'ttl': 3600000}],
    'j.root-servers.net': [
        {'type': 'A', 'address': '192.58.128.30', 'ttl': 3600000}],
    'k.root-servers.net': [
        {'type': 'A', 'address': '193.0.14.129', 'ttl': 3600000}],
    'l.root-servers.net': [
        {'type': 'A', 'address': '199.7.83.42', 'ttl': 3600000}],
    'm.root-servers.net': [
        {'type': 'A', 'address': '202.12.27.33', 'ttl': 3600000}],
    '.': [{'type': 'NS', 'nsdname': 'a.root-servers.net', 'ttl': 3600000},
          {'type': 'NS', 'nsdname': 'b.root-servers.net', 'ttl': 3600000},
          {'type': 'NS', 'nsdname': 'c.root-servers.net', 'ttl': 3600000},
          {'type': 'NS', 'nsdname': 'd.root-servers.net', 'ttl': 3600000},
          {'type': 'NS', 'nsdname': 'f.root-servers.net', 'ttl': 3600000},
          {'type': 'NS', 'nsdname': 'g.root-servers.net', 'ttl': 3600000},
          {'type': 'NS', 'nsdname': 'h.root-servers.net', 'ttl': 3600000},
          {'type': 'NS', 'nsdname': 'i.root-servers.net', 'ttl': 3600000},
          {'type': 'NS', 'nsdname': 'j.root-servers.net', 'ttl': 3600000},
          {'type': 'NS', 'nsdname': 'k.root-servers.net', 'ttl': 3600000},
          {'type': 'NS', 'nsdname': 'l.root-servers.net', 'ttl': 3600000},
          {'type': 'NS', 'nsdname': 'm.root-servers.net', 'ttl': 3600000}]
}


def _get_ip_from_packet(packet, name):
    return _get_result_from_packet(packet, protocol.Type.A, name).address


def _get_result_from_packet(packet, type_, name):
    for record in packet.answers + packet.additional:
        if not record.name == name:
            continue

        if isinstance(record, protocol.CNAMERecord):
            return _get_result_from_packet(packet, type_, record.cname)
        elif record.type_ == type_:
            return record


class DNSServerProtocol(object):

    def __init__(self):
        if not caching:
            self.cache = cache.copy()
        else:
            self.cache = cache

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        print('Received %s from %s' % (data, addr))

        packet = protocol.DNSPacket.from_struct(data)

        for question in packet.questions:
            self.handle_question(question)

    def handle_question(self, question):
        """ Ik weet het even niet meer"""
        # Vraag NS voor '.'
        # Vraag NS van domein op aan root
        # Vraag A van eerste NS op aan root
        # Vraag NS van domein op aan gekregen NS
        # if: CNAME voor domein: vraag A op voor CNAME
        # elif: A record: done
        # else: NS record: vraag A record op voor NS

        previous_server = None
        server = self.resolve_name(protocol.Type.NS, '.').nsdname
        for x in range(50):
            result = self.resolve_name(question.qtype.name, question.qname,
                                       server, previous_server)
            if result.is_authorative:
                return result.answers[0]
            else:
                for x in result.authorities:
                    if x.type_ == protocol.Type.NS:
                        previous_server = server
                        server = x.nsdname

        raise Exception("Too many queries")

    def resolve_name(self, type_, name, server=None, previous_server=None):
        result = self.lookup_cache(type_, name)
        if not result and server:
            ns = self.resolve_name(protocol.Type.A, server, previous_server)
            ns_ip = _get_ip_from_packet(ns)
            result = resolve_question(type_, name, ns_ip)
            self.cache_packet(result)
            return self.lookup_cache(type_, name)

        return result

    def cache_packet(self, packet):
        """Stores a packet in the local cache"""
        for record in (packet.answers
                       + packet.authorities
                       + packet.additional):
            self.cache[record.name] = record.to_dict()

    def lookup_cache(self, type_, name):
        records = cache.get(name, [])
        random.shuffle(records)
        for record in records:
            print(record)
            if record['type'] == type_.name:
                return protocol.ResourceRecord.from_dict(name, record)


def run():
    """
    DNS Client implementation in Python

    Usage:
        server.py [options]

    options:
        -c, --caching
        -p, --port port
        -r, --round_robin
        -t, --ttl time_to_live
    """
    import docopt
    import textwrap
    args = docopt.docopt(textwrap.dedent(run.__doc__), sys.argv[1:])

    if not sys.version_info > (3, 4, 0):
        print("You need to use Python 3.4")
        exit(2)

    loop = asyncio.get_event_loop()
    print("Starting DNS server")

    caching = args['--caching']
    port = int(args['--port']) if args['--port'] else 53
    round_robin = args['--round_robin']
    ttl = args['--ttl']

    listen = loop.create_datagram_endpoint(
        DNSServerProtocol, local_addr=('127.0.0.1', port))

    transport, async_protocol = loop.run_until_complete(listen)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    transport.close()
    loop.close()

if __name__ == '__main__':
    run()
