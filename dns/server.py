# -*- coding: utf8 -*-

from __future__ import print_function, absolute_import

import asyncio
import random

import protocol

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


class DNSServerProtocol(object):

    def __init__(self):
        if caching:
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

    def handle_question(question):
        """ Ik weet het even niet meer"""

    def cache_packet(self, packet):
        """Stores a packet in the local cache"""
        for record in (packet.questions
                       + packet.answers
                       + packet.authorities
                       + packet.additional):
            self.cache[record.name] = record.to_dict()

    def lookup_cache(self, type_, name):
        if name == '':
            name = '.'
        records = cache.get(name, [])
        random.shuffle(records)
        for record in records:
            if record['type'] == type_:
                return protocol.ResourceRecord.from_dict(record)


loop = asyncio.get_event_loop()
print("Starting DNS server")

listen = loop.create_datagram_endpoint(
    DNSServerProtocol, local_addr=('127.0.0.1', 53))

transport, async_protocol = loop.run_until_complete(listen)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

transport.close()
loop.close()
