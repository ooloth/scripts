#!/usr/bin/env bash

# Overall goal: Find out if I've already subscribed to a feed in Feedbin

# Requirements:
# - Feedbin account
# - Feedbin username and password

# Usage:
# - ./feeds.sh https://example.com
# - ./feeds.sh

# Docs:
# - https://github.com/feedbin/feedbin-api/blob/master/content/feeds.md

set -euo pipefail

# Check if a URL was provided as an argument
if [ -z "$1" ]; then
  echo "No URL provided. Please provide a URL to check."; exit 1
fi

# Extract the domain from the URL
DOMAIN=$(echo "$1" | awk -F/ '{print $3}')
echo "Domain: $DOMAIN"

# Fetch credentials from 1Password
USERNAME=$(op item get "Feedbin" --field username)
PASSWORD=$(op item get --reveal "Feedbin" --field password)

API="https://api.feedbin.com/v2"

fetch_subscriptions() {
  curl -u "$USERNAME:$PASSWORD" "$API/subscriptions.json"
}

subscriptions=$(fetch_subscriptions)

# Print subscriptions in a readable format
echo "$subscriptions" | jq '.[] | {feed_id: .feed_id, title: .title, site_url: .site_url, feed_url: .feed_url}'

# Remove trailing slash from input URL
input_url=$(echo "$1" | sed 's/\/$//')

# Compare input URL to each site_url while ignoring trailing slashes
matching_feed=$(echo "$subscriptions" | jq --arg input_url "$input_url" '.[] | select(.site_url | rtrimstr("/") == $input_url) | {feed_id: .feed_id, site_url: .site_url}')
echo "Matching feed: $matching_feed"

matching_feed_id=$(echo "$matching_feed" | jq '.feed_id')
echo "Matching feed ID: $matching_feed_id"

# curl -u "$FEEDBIN_USERNAME:$FEEDBIN_PASSWORD" "$FEEDBIN_API/feeds.json" | jq '.[] | {id: .id, feed_url: .feed_url}'

# Check if the feed already exists and return its ID
# matching_feed=""
# matching_feed=$("$response" | jq '.[] | select(.feed_url == "$1") | {id: .id, feed_url: .feed_url}')
# echo "Matching feed: $matching_feed"

# if [ -z "$matching_feed" ]; then
#     echo "Feed not found."
# else
#     echo "Feed found."
# fi
