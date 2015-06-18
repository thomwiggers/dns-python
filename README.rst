===============================
DNS client and server
===============================

.. image:: https://travis-ci.org/thomwiggers/dns-python.png?branch=master
   :target: https://travis-ci.org/thomwiggers/dns-python


Simple python implementation of a DNS server and client for a networking course

* Free software: GPLv3 license
.. * Documentation: http://OneBot.rtfd.org.

Implementation details
----------------------

* We've used the Python language. Python 3.4 and virtualenv are required to install
  the server. We will do this for you when running the dns_client.sh and dns_resolver.sh

* We used several classes to deal with the packets, the headers and the records. These
  support classes and function are found in dns/protocol.sh . We craft our packets by
  using struct.pack on all classes and elements of the packet class. Resource records
  know how to pack themselves. The flags pack themselves using bit masks of its
  properties. Hostnames are packed in one of our functions.

* The packet identifiers (for transaction IDS)  are randomly generated, other fields
  follow the RFCs, respecting our limitations.

* We used the AsyncIO library to implement multithreading.

Limitations
-----------

* The server and client don't really account for dropped UDP packets. The server
  will expect clients to re-request everything.

* SOA records aren't created or returned for non-existant names. The 'no
  results' error rcode won't be set, as the specification specifies that this
  flag is only to be set by authorative name servers.

* Only A and CNAME records are supported.

* The DNS server will only return Answers and the requested Questions.

* We will only return one A record

* Only IPv4 is supported

* Caching only writes on close and is only read on open
