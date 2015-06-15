# -*- coding: utf8 -*-

from __future__ import print_function, absolute_import
import sys
import protocol as dns
import socket

UDP_PORT = 53

def resolve(server, destination):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    dnsMessage = dns.RecursiveDNSMessage()
    dnsMessage.identifier = 1

    question = dns.Question(destination, 1)
    dnsMessage.questions.append(question)
    struct = dnsMessage.pack_struct()

    sock.sendto(struct, (server, UDP_PORT))

    data, addr = sock.recvfrom(2048)
    print ("received message:", data)
    sock.close()

def run():
    """
    DNS Client implementation in Python

    Usage:
        client.py [options] <destination>

    Options:
        -s,--server=dns_server  Specifies the dns server used to resolve the hostname.
    """
    import docopt
    import textwrap
    import os
    args = docopt.docopt(textwrap.dedent(run.__doc__), sys.argv[1:])

    if not sys.version_info > (3, 4, 0):
        print("You need to use Python 3.4")
        exit(2)

    resolve(args['<destination>'], args['--server'] or '127.0.0.1')

if __name__ == '__main__':
    run()
