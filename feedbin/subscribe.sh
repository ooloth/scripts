#!/usr/bin/env bash

# Subscribe to a new RSS feed in Feedbin and mark its entire backlog as unread

# Usage:
# - ./subscribe.sh https://example.com
# - ./subscribe.sh

# Docs:
# - https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md#create-subscription

set -euo pipefail

source feedbin/validation.sh
source feedbin/subscriptions.sh

main() {
  local url="$1"
  validate_url_arg "$url"

  echo "📥 Fetching my Feedbin subscriptions"
  subscriptions=$(fetch_subscriptions)
  # print_subscriptions "$subscriptions"

  echo "🔍 Checking for an existing subscription to '$url'"
  matching_subscription=$(find_matching_subscription "$url" "$subscriptions")

  if [[ "$matching_subscription" ]]; then
    echo "✅ I'm already subscribed to '$url'"
    # echo "$matching_subscription"
    exit 0
  fi

  echo "🔖 No matching subscription found. Subscribing now..."
  response=$(create_subscription "$url")
  echo "Response: $response"
  http_code=${response: -3}  # get the last 3 digits
  echo "HTTP code: $http_code"

  # TODO: carry on

  # matching_feed_id=$(echo "$matching_subscription" | jq '.feed_id')
  # echo "Matching feed ID: $matching_feed_id"

  # echo "Subscribed to $1 and marked entire backlog as unread."
}

main "$1"
