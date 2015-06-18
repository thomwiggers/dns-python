===============================
DNS client and server
===============================

.. image:: https://travis-ci.org/thomwiggers/dns-python.png?branch=master
   :target: https://travis-ci.org/thomwiggers/dns-python


Simple python implementation of a DNS server and client for a networking course

* Free software: GPLv3 license
.. * Documentation: http://OneBot.rtfd.org.

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
