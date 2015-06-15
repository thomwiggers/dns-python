# -*- coding: utf8 -*-

from __future__ import print_function, absolute_import
import sys
import protocol as dns
import socket
import time

UDP_PORT = 53

def resolve(server, destination):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    dnsMessage = dns.RecursiveDNSMessage()
    dnsMessage.identifier = 1
    question = dns.Question(destination, 1)
    dnsMessage.questions.append(question)

    sock.sendto(dnsMessage.pack_struct(), (server, UDP_PORT))

    res = receive_response(sock)

    print(res)
    sock.close()

def receive_response(mySocket, timeout=5):
    startTime = time.time()

    while (startTime + timeout - time.time()) > 0:
        try:
            response, (addr, x) = mySocket.recvfrom(2048)
        except socket.timeout:
            break

        return dns.DNSPacket.from_struct(response)

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
    import os
    args = docopt.docopt(textwrap.dedent(run.__doc__), sys.argv[1:])

    if not sys.version_info > (3, 4, 0):
        print("You need to use Python 3.4")
        exit(2)

    resolve(args['--server'], args['<destination>'])

if __name__ == '__main__':
    run()
