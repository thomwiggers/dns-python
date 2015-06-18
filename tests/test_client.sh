#!/bin/sh

set -e

echo -n "Checking ip lookup "
dns-client -s 8.8.8.8 rded.nl | grep -q 195.169.207.54 && echo "OK"
echo -n "Checking authorative name server "
dns-client -s kate.ns.cloudflare.com mail.rded.nl | grep -q Non-authorative && false || echo "OK"

echo -n "Checking cname lookup "
dns-client -s 8.8.8.8 mail.rded.nl | grep -q clearlyreta.rded.nl && echo "OK"

echo -n "Checking non-existing domain "
dns-client -s 8.8.8.8 doesntexist.rded.nl | grep -q NXDOMAIN && echo "OK"
