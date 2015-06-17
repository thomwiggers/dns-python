# -*- coding: utf8 -*-

from __future__ import print_function, absolute_import
import sys
import socket
import time

import protocol

UDP_PORT = 53


def resolve(server, destination):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    dnsMessage = protocol.RecursiveDNSMessage()
    dnsMessage.identifier = 1
    question = protocol.Question(destination, 1)
    dnsMessage.questions.append(question)

    sock.sendto(dnsMessage.pack_struct(), (server, UDP_PORT))

    res = receive_response(sock)
    print_result(res, server, destination)
    sock.close()


def print_result(dns, server, destination):
    print("Server: \t{}".format(server))
    print("Address: \t{}#{}\n".format(server, UDP_PORT))

    if not dns.flags.is_authorative_answer:
        print("Non-authorative answer:")
    for answer in dns.answers:
        if isinstance(answer, protocol.NSRecord):
            print("NSName: {}".format(answer.nsdname))

        print("Name:   {}".format(answer.name))
        print("Address: {}".format(answer.address))


def receive_response(mySocket, timeout=5):
    startTime = time.time()

    while (startTime + timeout - time.time()) > 0:
        try:
            response, (addr, x) = mySocket.recvfrom(2048)
        except socket.timeout:
            break

        return protocol.DNSPacket.from_struct(response)


def run():
    """
    DNS Client implementation in Python

    Usage:
        client.py -s server <destination>

    options:
        -s, --server dns_server
    """
    import docopt
    import textwrap
    args = docopt.docopt(textwrap.dedent(run.__doc__), sys.argv[1:])

    if not sys.version_info > (3, 4, 0):
        print("You need to use Python 3.4")
        exit(2)

    resolve(args['--server'], args['<destination>'])

if __name__ == '__main__':
    run()
