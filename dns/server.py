# -*- coding: utf8 -*-

from __future__ import print_function, absolute_import

import asyncio
from collections import defaultdict
import random
import sys

import protocol
from client import resolve_question

caching = False

cache = defaultdict(list)

cache.update({
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
})


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
        results = []

        for question in packet.questions:
            results += self.handle_question(question)

        self.return_results(packet.identifier, results, addr)

    def connection_lost(self, exc):
        pass

    def return_results(self, identifier, results, addr):
        packet = protocol.DNSPacket()
        packet.flags.is_response = True
        packet.answers = results
        packet.identifier = identifier

        self.transport.sendto(packet.pack_struct(), addr)

    def handle_question(self, question):
        """ Ik weet het even niet meer"""
        # Vraag NS voor '.'
        # Vraag NS van domein op aan root
        # Vraag A van eerste NS op aan root
        # Vraag NS van domein op aan gekregen NS
        # if: CNAME voor domein: vraag A op voor CNAME
        # elif: A record: done
        # else: NS record: vraag A record op voor NS

        record = self.lookup_cache(question.qtype, question.qname)
        if not record:
            # try cnames
            records = []
            record = self.lookup_cache(protocol.Type.CNAME, question.qname)
            while record:
                records.append(record)
                record = self.lookup_cache(protocol.Type.CNAME, record.cname)
            if len(records) > 0:
                record = self.lookup_cache(question.qtype, records[-1].cname)
            if record:
                return records + [record]

        last_ns_ip = None

        server = None
        current_name = question.qname.split('.')
        while len(current_name) > 0:
            fullname = ('.'.join(current_name)).strip('.') + '.'
            nsrecord = self.lookup_cache(protocol.Type.NS, fullname)
            if nsrecord is not None:
                server = nsrecord.nsdname
                break
            current_name = current_name[1:]

        print("Found NS Cache for ", fullname)
        for x in range(50):
            print('resolving ip for ns', server)
            cached = self.lookup_cache(protocol.Type.A, server)
            if cached:
                last_ns_ip = cached.address
            else:
                print('trying to find name server ip', server)
                q = protocol.Question(server, protocol.Type.A)
                last_ns_ip = self.handle_question(q)[0].address
            print('found', last_ns_ip)

            result = self.resolve_name(question.qtype,
                                       question.qname,
                                       last_ns_ip)
            if not result:
                return []
            if result.type_ == question.qtype:
                print('returning result', result)
                return [result]
            elif result.type_ == protocol.Type.CNAME:
                print('cname!')
                q = protocol.Question(result.cname, question.qtype)
                return [result] + self.handle_question(q)
            elif result.type_ == protocol.Type.NS:
                server = result.nsdname

        raise Exception("Too many tries")

    def resolve_name(self, type_, name, server):
        result = self.lookup_cache(type_, name)
        if result:
            return result
        else:
            print('sending question over the network')
            packet = resolve_question(type_, name, server, recursive=False)
            self.cache_packet(packet)
            for rr in (packet.answers
                       + packet.authorities
                       + packet.additional):
                if rr.name == name:
                    return rr
                elif rr.type_ == protocol.Type.NS:
                    return rr

    def cache_packet(self, packet):
        """Stores a packet in the local cache"""
        for record in (packet.answers
                       + packet.authorities
                       + packet.additional):
            print(record)
            self.cache[record.name] += [record.to_dict()]

    def lookup_cache(self, type_, name):
        random.shuffle(self.cache[name])
        for record in self.cache[name]:
            if record['type'] == type_.name:
                print(record)
                res = protocol.ResourceRecord.from_dict(name, record)
                return res


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
