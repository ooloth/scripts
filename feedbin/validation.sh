#!/usr/bin/env bash

validate_url_arg() {
  if [ -z "$1" ]; then
    echo "No URL provided. Please provide a URL to subscribe to."
    exit 1
  fi

  if [[ ! "$1" =~ ^https?:// ]]; then
    echo "Please provide a valid URL."; exit 1
  fi
}
