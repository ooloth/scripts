#!/usr/bin/env bash

# Overall goal: Find out if I've already subscribed to a feed in Feedbin

# Usage:
# - ./subscriptions.sh https://example.com
# - ./subscriptions.sh

# Docs:
# - https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md

set -euo pipefail

USERNAME=$(op item get "Feedbin" --field username)
PASSWORD=$(op item get --reveal "Feedbin" --field password)
API="https://api.feedbin.com/v2"

fetch_subscriptions() {
  curl -s -u "$USERNAME:$PASSWORD" "$API/subscriptions.json"
}

print_subscriptions() {
  echo "$1" | jq '.[] | {feed_id: .feed_id, title: .title, site_url: .site_url, feed_url: .feed_url}'
}

find_matching_subscription() {
  local url="$1"
  local subscriptions="$2"

  url_without_trailing_slash=$(echo "$url" | sed 's/\/$//')

  # Compare the input URL to each site_url, disregarding trailing slashes
  echo "$subscriptions" | jq --arg input_url "$url_without_trailing_slash" \
  '.[] | select(.site_url | rtrimstr("/") == $input_url) | {feed_id: .feed_id, site_url: .site_url}'
}

# See: https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md#create-subscription
create_subscription() {
  local url="$1"

  response=$(curl -v -u "$USERNAME:$PASSWORD" \
  -H "Content-Type: application/json; charset=utf-8" \
  -X POST -d "{\"feed_url\": \"$url\"}" "$API/subscriptions.json")

  echo "$response"

  # If the response includes multiple items, the user needs to choose which feed URL to subscribe to
  # if [[ $(echo "$response" | jq '. | length') -gt 1 ]]; then
  #   echo "Multiple feeds found. Please choose one:"
  #   # Display options with numbers
  #   echo "$response" | jq -r '.[] | "\(.title) \(.feed_url)"' | nl -w 2 -s '. '

  #   # Read user choice
  #   read -pr "Enter the number of the feed you want to subscribe to: " choice

  #   # Get the selected feed URL
  #   feed_url=$(echo "$response" | jq -r --argjson choice "$choice" '.[$choice - 1] | .feed_url')

  #   echo "Selected feed URL: $feed_url"
  # else
  #   # If only one feed is found, automatically select it
  #   feed_url=$(echo "$response" | jq -r '.[0] | .feed_url')
  # fi
}
