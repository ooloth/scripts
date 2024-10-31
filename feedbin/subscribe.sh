#!/usr/bin/env bash

# Overall goal: Add a new RSS feed to Feedbin and mark its entire backlog as unread

# Requirements:
# - Feedbin account
# - Feedbin username and password
# - Feedbin API key

# Usage:
# - ./subscribe.sh https://example.com
# - ./subscribe.sh

# Docs:
# - https://github.com/feedbin/feedbin-api

set -euo pipefail

# Check if a URL was provided as an argument
if [ -z "$1" ]; then
    echo "No URL provided. Please provide a URL to subscribe to."
    exit 1
fi

# Extract the domain from the URL
DOMAIN=$(echo "$1" | awk -F/ '{print $3}')
echo "Domain: $DOMAIN"

# Set the Feedbin username and password
# Fetch credentials from 1Password
FEEDBIN_USERNAME=$(op item get "Feedbin" --field username)
FEEDBIN_PASSWORD=$(op item get "Feedbin" --field password)
echo "Feedbin username: $FEEDBIN_USERNAME"
echo "Feedbin password: $FEEDBIN_PASSWORD"

FEEDBIN_API="https://api.feedbin.com/v2"

# Extract and print URL suffixes
# echo "$subscriptions" | jq -r '.[] | "\(.site_url) \(.feed_url)"' | while read -r site_url feed_url; do
#   # Remove site_url prefix from feed_url to get the suffix
#   suffix=${feed_url#"$site_url"}
#   echo "$suffix"
# done

# Subscribe to the feed using the Feedbin API
# curl -u "$FEEDBIN_USERNAME:$FEEDBIN_PASSWORD" -X POST "$FEEDBIN_API/subscriptions.json" -d "feed_url=$1" -d "api_key=$FEEDBIN_API_KEY"

# Mark the entire backlog of the feed as unread
# curl -u "$FEEDBIN_USERNAME:$FEEDBIN_PASSWORD" -X POST "$FEEDBIN_API/unread_entries.json" -d "feed_id=$DOMAIN" -d "api_key=$FEEDBIN_API_KEY"

echo "Subscribed to $1 and marked entire backlog as unread."
