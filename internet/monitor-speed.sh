#!/usr/bin/env bash

# Schedule regular speed tests to measure your download and upload speeds.
# Check for significant drops in download/upload speeds.

# TODO: run from mini?

while true; do
  speedtest-cli >>internet/speedtest_log.txt
  sleep 3600
done
