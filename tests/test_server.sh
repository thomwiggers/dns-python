#!/bin/bash

set -e

cd /tmp/

rm -f cache /tmp/dnsserver.out

dns-server -p 1053 | tee /tmp/dnsserver.out > /dev/null &

echo -n "Requesting A record from server "
dig clearlyreta.rded.nl @localhost -p 1053 | grep -q 148.251.109.127 && echo "OK" || exit
echo -n "Requesting CNAME record from server "
dig mail.rded.nl @localhost -p 1053 | grep -q CNAME && echo "OK" || exit

killall dns-server

dns-server -p 1053 --caching | tee /tmp/dnsserver.out > /dev/null &

echo -n "Requesting A record from server "
dig clearlyreta.rded.nl @localhost -p 1053 | grep -q 148.251.109.127 && echo "OK" || exit

echo -n "Requesting CNAME record from server "
dig mail.rded.nl @localhost -p 1053 | grep -q CNAME && echo "OK" || exit

killall dns-server

echo -n "Checking cached record "
grep -q 'Found NS Cache for  rded.nl.' /tmp/dnsserver.out && echo "OK" || exit

echo -n "Checking cached record after restart "
dns-server -p 1053 --caching --ttl 0 | tee /tmp/dnsserver.out > /dev/null &
dig mail.rded.nl @localhost -p 1053 | grep -q CNAME || exit
grep -q 'Found NS Cache for  rded.nl.' /tmp/dnsserver.out && echo "OK" || exit

killall dns-server

rm -f cache
dns-server -p 1053 --caching --ttl 1 | tee /tmp/dnsserver.out > /dev/null &

echo -n "Requesting A record from server "
dig clearlyreta.rded.nl @localhost -p 1053 | grep -q 148.251.109.127 && echo "OK" || exit

echo "Sleeping for 10 seconds"
sleep 10

echo -n "Requesting A record from server "
dig clearlyreta.rded.nl @localhost -p 1053 | grep -q 148.251.109.127 && echo "OK" || exit

killall dns-server

echo -n "Checking if old records are pruned "
grep -q 'Pruning' /tmp/dnsserver.out && echo "OK" || exit
