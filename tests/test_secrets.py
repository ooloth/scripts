"""Tests for reading secrets out of 1Password."""

import subprocess
from unittest.mock import patch

import pytest

from common.secrets import SecretUnavailable, build_secret_reference, get_secret

# What `op read` prints to stderr when the item named in the reference is not in the
# vault. This is the failure that made every Feedbin command fail, and the message it
# produced said only that a subprocess exited non-zero.
ITEM_NOT_FOUND = (
    "[ERROR] could not read secret 'op://Scripts/Feedbin/username': could not get item "
    'Scripts/Feedbin: "Feedbin" isn\'t an item in the "Scripts" vault.\n'
)


def test_reference_points_at_the_field_in_the_scripts_vault() -> None:
    """The reference 1Password is asked for names the vault, item and field."""
    assert build_secret_reference("Feedbin API", "username") == "op://Scripts/Feedbin API/username"


def test_a_secret_is_returned_without_surrounding_whitespace() -> None:
    """`op read` ends its output with a newline that is not part of the secret."""
    with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0, "hunter2\n", "")):
        assert get_secret("Feedbin API", "password") == "hunter2"


def test_a_missing_item_says_which_reference_failed_and_why() -> None:
    """The message has to name the reference and repeat what 1Password said about it.

    Without both, a misnamed item surfaces as "Unexpected error" and the reader has
    no way to tell a typo from an expired session.
    """
    failure = subprocess.CalledProcessError(1, ["op"], stderr=ITEM_NOT_FOUND)

    with patch("subprocess.run", side_effect=failure):
        with pytest.raises(SecretUnavailable) as caught:
            get_secret("Feedbin", "username")

    message = str(caught.value)
    assert "op://Scripts/Feedbin/username" in message
    assert 'isn\'t an item in the "Scripts" vault' in message


def test_a_missing_1password_cli_says_so_rather_than_raising_file_not_found() -> None:
    """`op` absent is a setup problem, and the message points at the install docs."""
    with patch("subprocess.run", side_effect=FileNotFoundError("op")):
        with pytest.raises(SecretUnavailable) as caught:
            get_secret("Feedbin API", "username")

    message = str(caught.value)
    assert "1Password CLI is not installed" in message
    assert "op://Scripts/Feedbin API/username" in message


def test_a_silent_failure_still_names_the_exit_code() -> None:
    """Some `op` failures print nothing, so the message falls back to the exit code."""
    with patch("subprocess.run", side_effect=subprocess.CalledProcessError(9, ["op"], stderr="")):
        with pytest.raises(SecretUnavailable, match="op exited 9"):
            get_secret("Feedbin API", "username")


def test_the_secret_value_never_reaches_the_error_message() -> None:
    """A failure message is logged, so it must carry the reference and not the value."""
    failure = subprocess.CalledProcessError(1, ["op"], output="hunter2", stderr=ITEM_NOT_FOUND)

    with patch("subprocess.run", side_effect=failure):
        with pytest.raises(SecretUnavailable) as caught:
            get_secret("Feedbin", "username")

    assert "hunter2" not in str(caught.value)
