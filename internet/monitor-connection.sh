#!/usr/bin/env bash

# Continuously ping a reliable server (e.g., Google DNS at 8.8.8.8) and log the results.
# Look for patterns of high latency or packet loss in the ping logs.

# TODO: run from mini?

while true; do
  ping -c 10 8.8.8.8 >>internet/ping_log.txt
  sleep 60
done
