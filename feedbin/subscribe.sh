#!/usr/bin/env bash

# Overall goal: Add a new RSS feed to Feedbin and mark its entire backlog as unread

# Requirements:
# - Feedbin account
# - Feedbin username and password
# - Feedbin API key

# Usage:
# - ./subscribe.sh https://example.com
# - ./subscribe.sh

# Set the Feedbin username and password
FEEDBIN_USERNAME="username"
FEEDBIN_PASSWORD="password"
FEEDBIN_API_KEY="api_key"

# Check if a URL was provided as an argument
if [ -z "$1" ]; then
    echo "No URL provided. Please provide a URL to subscribe to."
    exit 1
fi

# Extract the domain from the URL
DOMAIN=$(echo "$1" | awk -F/ '{print $3}')

# Subscribe to the feed using the Feedbin API
curl -u "$FEEDBIN_USERNAME:$FEEDBIN_PASSWORD" -X POST "https://api.feedbin.com/v2/subscriptions.json" -d "feed_url=$1" -d "api_key=$FEEDBIN_API_KEY"

# Mark the entire backlog of the feed as unread
curl -u "$FEEDBIN_USERNAME:$FEEDBIN_PASSWORD" -X POST "https://api.feedbin.com/v2/unread_entries.json" -d "feed_id=$DOMAIN" -d "api_key=$FEEDBIN_API_KEY"

echo "Subscribed to $1 and marked entire backlog as unread."
