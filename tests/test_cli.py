"""Smoke tests for the top-level CLI entry point."""

from typer.testing import CliRunner

from cli import app

runner = CliRunner()


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
