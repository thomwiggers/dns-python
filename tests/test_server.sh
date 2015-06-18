#!/bin/bash

set -e

cd /tmp/

rm -f cache

dns-server -p 1053 > /tmp/dnsserver.out &

echo -n "Requesting A record from server "
dig clearlyreta.rded.nl @localhost -p 1053 | grep -q 148.251.109.127 && echo "OK" || exit
echo -n "Requesting CNAME record from server "
dig mail.rded.nl @localhost -p 1053 | grep -q CNAME && echo "OK" || exit

killall -INT dns-server

dns-server -p 1053 --caching > /tmp/dnsserver.out &

echo -n "Requesting A record from server "
dig clearlyreta.rded.nl @localhost -p 1053 | grep -q 148.251.109.127 && echo "OK" || exit

echo -n "Requesting CNAME record from server "
dig mail.rded.nl @localhost -p 1053 | grep -q CNAME && echo "OK" || exit

killall -INT dns-server

echo -n "Checking cached record "
grep -q 'Found NS Cache for  rded.nl.' /tmp/dnsserver.out && echo "OK" || exit

echo -n "Checking cached record after restart "
dns-server -p 1053 --caching --ttl 0 > /tmp/dnsserver.out &
dig mail.rded.nl @localhost -p 1053 | grep -q CNAME && echo "OK" || exit
grep -q 'Found NS Cache for  rded.nl.' /tmp/dnsserver.out && echo "OK" || exit

killall -INT dns-server

rm -f cache
dns-server -p 1053 --caching --ttl 0 > /tmp/dnsserver.out &

echo -n "Requesting A record from server "
dig clearlyreta.rded.nl @localhost -p 1053 | grep -q 148.251.109.127 && echo "OK" || exit

echo -n "Requesting A record from server "
dig clearlyreta.rded.nl @localhost -p 1053 | grep -q 148.251.109.127 && echo "OK" || exit

killall -INT dns-server

echo -n "Checking if old records are pruned "
grep -q 'Pruning' /tmp/dnsserver.out && echo "OK" || exit
