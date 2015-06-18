# -*- coding: utf8 -*-

from __future__ import print_function, absolute_import
import random
import sys
import socket
import time

import protocol

UDP_PORT = 53


def resolve_question(type_, name, server, recursive=True, port=UDP_PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    dnsMessage = protocol.DNSPacket()
    dnsMessage.flags.recursion_desired = recursive
    dnsMessage.identifier = random.getrandbits(16)
    question = protocol.Question(name, type_)
    dnsMessage.questions.append(question)

    sock.sendto(dnsMessage.pack_struct(), (server, port))

    res = receive_response(sock, dnsMessage.identifier)
    sock.close()
    return res


def resolve(server, destination, port):
    res = resolve_question(protocol.Type.A, destination, server, port=port)
    print_result(res, server, destination, port)


def print_result(dns, server, destination, port):
    print("Server: \t{}".format(server))
    print("Address: \t{}#{}\n".format(server, port))

    if len(dns.answers) == 0:
        print("** server can't find {}: NXDOMAIN".format(destination))
        return
    if not dns.flags.is_authorative_answer:
        print("Non-authorative answer:")
    for answer in dns.answers:
        if isinstance(answer, protocol.CNAMERecord):
            print("{}\t canonical name = {}".format(answer.name, answer.cname))
        elif isinstance(answer, protocol.ARecord):
            print("Name:   {}".format(answer.name))
            print("Address: {}".format(answer.address))


def receive_response(mySocket, identifier, timeout=5):
    startTime = time.time()

    while (startTime + timeout - time.time()) > 0:
        try:
            response, (addr, x) = mySocket.recvfrom(2048)
        except socket.timeout:
            break

        result = protocol.DNSPacket.from_struct(response)
        if result.identifier != identifier:
            raise Exception("Got a message for another id")

        return result


def run():
    """
    DNS Client implementation in Python

    Usage:
        client.py [options] -s server <destination>

    options:
        -s, --server dns_server
        -p, --port port
    """
    import docopt
    import textwrap
    args = docopt.docopt(textwrap.dedent(run.__doc__), sys.argv[1:])

    if not sys.version_info > (3, 4, 0):
        print("You need to use Python 3.4")
        exit(2)

    port = int(args['--port']) if args['--port'] else 53
    resolve(args['--server'], args['<destination>'], port)

if __name__ == '__main__':
    run()
