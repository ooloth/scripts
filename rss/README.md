# rss

A CLI for managing [Feedbin](https://feedbin.com) RSS subscriptions and entries via the [Feedbin API](https://github.com/feedbin/feedbin-api).

## Commands

- `rss add <url>` — subscribe to a feed and optionally mark backlog entries as unread
- `rss subscriptions` — manage subscriptions (add, delete, get, update)
- `rss entries` — manage entries (list, mark-unread)

## Note

The automated daily batch workflow (which used the API to sync read state on a schedule) has been retired in favour of the [Feedbin browser extension](https://github.com/feedbin/feedbin-extension). The CLI itself remains active and is used for on-demand subscription and entry management.

## Rules

- Each request starts a new pipeline
- I/O should be kept separate from core logic, and ideally at the beginning and end of each pipeline
- Core logic should be composed of pure functions
- The domain should be modeled via detailed type definitions for all inputs and outputs
- Prefer type aliases that use ubiquitous domain language over primitive types

Sources:

- (add Scott Wlaschin talks)
