## Overview

CLI for managing [Feedbin](https://feedbin.com) RSS subscriptions and entries via the Feedbin API.

> **Note:** The automated daily batch workflow (which polled for new entries and sent notifications)
> was disabled in favour of the [Feedbin browser extension](https://github.com/feedbin/feedbin-extension).
> The CLI commands below remain active.

## Commands

```
rss add <url>                        Subscribe to a feed URL
rss subscriptions list               List all subscriptions
rss entries list <feed-id>           List entries for a feed
rss entries mark-unread <entry-ids>  Mark entries as unread
```

## Design rules

- Each request starts a new pipeline
- I/O should be kept separate from core logic, and ideally at the beginning and end of each pipeline
- Core logic should be composed of pure functions
- The domain should be modeled via detailed type definitions for all inputs and outputs
- Prefer type aliases that use ubiquitous domain language over primitive types

Sources:

- (add Scott Wlaschin talks)
