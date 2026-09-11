"""Tests for the CLI entry point and the rss sub-commands it exposes."""

import logging
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from cli import app
from rss.domain import FeedOption, Subscription
from rss.entries.list.feedbin import GetFeedEntriesResult
from rss.entries.mark_unread.feedbin import CreateUnreadEntriesResult, UnreadEntriesResponse
from rss.subscriptions.add.feedbin import CreateSubscriptionResult

runner = CliRunner()

# What Feedbin hands back once it has a feed: the subscription it stored.
SUBSCRIPTION = Subscription(
    feed_id=2338770,
    feed_url="https://example.com/feed.xml",
    id=1,
    site_url="https://example.com",
    title="Example",
)

# A subscription that Feedbin would happily create, so a dry run that wrongly reaches
# the API fails on "was it called" rather than on an unusable mock return value.
CREATED_SUBSCRIPTION = (CreateSubscriptionResult.CREATED, SUBSCRIPTION)

# The two feeds Feedbin offers when a site advertises more than one.
FEED_OPTION_A = FeedOption(feed_url="https://example.com/posts.xml", title="Example posts")
FEED_OPTION_B = FeedOption(feed_url="https://example.com/notes.xml", title="Example notes")

# The wording typer.confirm() echoes before a real subscription is created. A dry run
# must never reach it, so its absence from the output is what "non-interactive" means.
CONFIRMATION_PROMPT = "Subscribe to"

# Every non-dry run stops at that prompt, so each has to answer it to reach Feedbin.
CONFIRMATION_ANSWER = "y\n"

# DRY_RUN is a repo-wide convention an operator may well have exported. A test of what
# `rss add` does for real has to switch it off rather than inherit whatever the shell set.
NOT_A_DRY_RUN = {"DRY_RUN": "false"}


def reported_failures(caplog: pytest.LogCaptureFixture) -> str:
    """Everything a command told the user went wrong.

    Rich wraps console output to the terminal width, so the log records are the only
    place the failure text survives intact.
    """
    return "\n".join(
        record.getMessage() for record in caplog.records if record.levelno == logging.ERROR
    )


def test_help_lists_rss_and_modem_commands() -> None:
    """cli.py --help must list both sub-commands without import errors."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "rss" in result.output
    assert "modem" in result.output


def test_rss_help_lists_add_and_entries_commands() -> None:
    """cli.py rss --help must list rss sub-commands without import errors."""
    result = runner.invoke(app, ["rss", "--help"])
    assert result.exit_code == 0
    assert "add" in result.output
    assert "entries" in result.output


def test_rss_entries_help_lists_list_and_mark_unread_commands() -> None:
    """cli.py rss entries --help must list the entries sub-commands."""
    result = runner.invoke(app, ["rss", "entries", "--help"])
    assert result.exit_code == 0
    assert "list" in result.output
    assert "mark-unread" in result.output


def test_dry_run_flag_does_not_create_a_subscription() -> None:
    """A --dry-run subscribe must exit cleanly without prompting or calling Feedbin."""
    with patch("rss.cli.create_subscription", return_value=CREATED_SUBSCRIPTION) as create:
        result = runner.invoke(
            app,
            ["rss", "add", "https://example.com", "--dry-run"],
            env=NOT_A_DRY_RUN,
        )

    create.assert_not_called()
    assert CONFIRMATION_PROMPT not in result.output
    assert result.exit_code == 0


@pytest.mark.parametrize("dry_run_value", ["true", "True", "TRUE"])
def test_dry_run_environment_variable_is_case_insensitive(dry_run_value: str) -> None:
    """DRY_RUN must skip the subscription however the operator capitalises 'true'."""
    with patch("rss.cli.create_subscription", return_value=CREATED_SUBSCRIPTION) as create:
        result = runner.invoke(
            app,
            ["rss", "add", "https://example.com"],
            env={"DRY_RUN": dry_run_value},
        )

    create.assert_not_called()
    assert result.exit_code == 0


def test_subscribing_to_a_new_feed_exits_zero() -> None:
    """A feed Feedbin subscribes to must succeed the command and say so once."""
    with patch("rss.cli.create_subscription", return_value=CREATED_SUBSCRIPTION):
        result = runner.invoke(
            app,
            ["rss", "add", "https://example.com"],
            input=CONFIRMATION_ANSWER,
            env=NOT_A_DRY_RUN,
        )

    # The result values already begin with the check mark, so printing one alongside
    # them says "✅ ✅ Subscription created". One check mark means one is being added.
    assert result.output.count("✅") == 1
    assert result.exit_code == 0


def test_subscribing_to_an_already_subscribed_feed_exits_zero() -> None:
    """A feed the user already subscribes to must succeed the command, not fail it."""
    with patch(
        "rss.cli.create_subscription",
        return_value=(CreateSubscriptionResult.EXISTS, SUBSCRIPTION),
    ):
        result = runner.invoke(
            app,
            ["rss", "add", "https://example.com"],
            input=CONFIRMATION_ANSWER,
            env=NOT_A_DRY_RUN,
        )

    assert CreateSubscriptionResult.EXISTS.value in result.output
    assert result.exit_code == 0


def test_subscribing_to_a_url_without_a_feed_exits_non_zero(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A URL Feedbin finds no feed at must fail the command and say the feed is missing."""
    with patch(
        "rss.cli.create_subscription",
        return_value=(CreateSubscriptionResult.NOT_FOUND, "https://example.com"),
    ):
        result = runner.invoke(
            app,
            ["rss", "add", "https://example.com"],
            input=CONFIRMATION_ANSWER,
            env=NOT_A_DRY_RUN,
        )

    assert CreateSubscriptionResult.NOT_FOUND.value in reported_failures(caplog)
    assert result.exit_code == 1


def test_subscribing_to_a_site_with_several_feeds_uses_the_chosen_feed() -> None:
    """When Feedbin offers several feeds, the one the user picks must be subscribed to."""
    with (
        patch(
            "rss.cli.create_subscription",
            side_effect=[
                (CreateSubscriptionResult.MULTIPLE_CHOICES, [FEED_OPTION_A, FEED_OPTION_B]),
                CREATED_SUBSCRIPTION,
            ],
        ) as create,
        patch("rss.cli._ask_for_feed_choice", return_value=FEED_OPTION_B),
    ):
        result = runner.invoke(
            app,
            ["rss", "add", "https://example.com"],
            input=CONFIRMATION_ANSWER,
            env=NOT_A_DRY_RUN,
        )

    assert create.call_args_list[1].args == (FEED_OPTION_B.feed_url,)
    assert result.exit_code == 0


def test_listing_entries_of_a_missing_feed_exits_non_zero(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A feed lookup that finds nothing must fail the command and say the feed is missing."""
    with patch("rss.cli.get_feed_entries", return_value=(GetFeedEntriesResult.NOT_FOUND, 999)):
        result = runner.invoke(app, ["rss", "entries", "list", "999"])

    assert GetFeedEntriesResult.NOT_FOUND.value in reported_failures(caplog)
    assert result.exit_code == 1


def test_listing_entries_of_an_existing_feed_exits_zero() -> None:
    """A successful feed lookup must succeed the command."""
    with patch("rss.cli.get_feed_entries", return_value=(GetFeedEntriesResult.OK, [])):
        result = runner.invoke(app, ["rss", "entries", "list", "999"])

    assert result.exit_code == 0


def test_marking_entries_unread_exits_non_zero_when_feedbin_errors(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """An HTTP error while marking entries unread must fail the command and report the error."""
    with patch(
        "rss.cli.create_unread_entries",
        return_value=(CreateUnreadEntriesResult.HTTP_ERROR, "boom"),
    ):
        result = runner.invoke(app, ["rss", "entries", "mark-unread", "123"])

    assert CreateUnreadEntriesResult.HTTP_ERROR.value in reported_failures(caplog)
    assert result.exit_code == 1


def test_marking_entries_unread_exits_zero_on_success() -> None:
    """Entries Feedbin accepts as unread must succeed the command."""
    marked_unread = UnreadEntriesResponse(marked_as_unread=[123], not_marked_as_unread=[])

    with patch(
        "rss.cli.create_unread_entries",
        return_value=(CreateUnreadEntriesResult.OK, marked_unread),
    ):
        result = runner.invoke(app, ["rss", "entries", "mark-unread", "123"])

    assert result.exit_code == 0
