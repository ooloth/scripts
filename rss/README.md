## Overview

CLI for managing [Feedbin](https://feedbin.com) RSS subscriptions and entries via the Feedbin API.

Read state syncs through the [Feedbin browser extension](https://github.com/feedbin/feedbin-extension).
These commands cover on-demand subscription and entry management.

## Commands

```
rss add <url>                         Subscribe to a feed URL
rss entries list <feed-id>            List entries for a feed
rss entries mark-unread <entry-ids>   Mark entries as unread
```

`entries list` writes one entry ID per line to stdout and everything else to stderr, so it pipes
into `mark-unread`:

```
uv run cli.py rss entries list 2338770 | xargs uv run cli.py rss entries mark-unread
```

Every command in the block above is checked by `test_readme_documents_only_real_commands` in
`tests/test_cli.py`, so a command that is renamed or removed fails the suite rather than going
stale here.

## Design rules

- Each request starts a new pipeline
- I/O should be kept separate from core logic, and ideally at the beginning and end of each pipeline
- Core logic should be composed of pure functions
- The domain should be modeled via detailed type definitions for all inputs and outputs
- Prefer named domain types over primitive types, via `NewType` so the name is enforced rather than
  merely documented

Sources:

- (add Scott Wlaschin talks)
