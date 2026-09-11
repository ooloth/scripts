"""
To avoid ever exposing the secrets used by the scripts in this repo as plain text (e.g. in a local `.env` file), they
are stored in 1Password and referenced by their location in the vault the 1Password service account has access to.

When running these scripts locally, I'm prompted by the 1Password CLI to authenticate with my fingerprint. To support
running these scripts via GitHub Actions workflows, an OP_SERVICE_ACCOUNT_TOKEN repository secret is needed to allow
the 1Password CLI to authenticate the service account user used in that environment.

Docs:
 - https://developer.1password.com/docs/cli/secret-reference-syntax/
 - https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository
"""

import subprocess

# Docs (service accounts):
# - https://developer.1password.com/docs/service-accounts/get-started/
# - https://developer.1password.com/docs/service-accounts/use-with-1password-cli/
# - https://developer.1password.com/docs/service-accounts/manage-service-accounts/
# - https://developer.1password.com/docs/ci-cd/github-actions/
# - https://developer.1password.com/docs/sdks/
# - https://github.com/1Password/onepassword-sdk-python/blob/main/example/example.py
# - https://developer.1password.com/docs/cli/reference/

VAULT = "Scripts"


def build_secret_reference(item: str, field: str) -> str:
    """
    Generate a 1Password secret reference.

    See: https://developer.1password.com/docs/cli/secret-reference-syntax#a-field-without-a-section
    """
    return f"op://{VAULT}/{item}/{field}"


PasswordOrStringifiedJson = str


class SecretUnavailable(RuntimeError):
    """A 1Password reference could not be read.

    Environmental, not a bug: the item is misnamed, the field is missing, the
    vault is not shared with this account, or nobody is signed in.
    """


def get_secret(item: str, field: str) -> PasswordOrStringifiedJson:
    """
    Generate a 1Password secret reference and retrieve the secret's value.

    Raises SecretUnavailable naming the reference that failed. Callers log the
    message, so it says which reference and what 1Password said about it, not
    just that a subprocess exited non-zero. The reference is a pointer rather
    than a value, so it is safe to put in a message; the secret never is.
    """
    secret_reference = build_secret_reference(item, field)

    try:
        result = subprocess.run(
            ["op", "read", secret_reference],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as e:
        raise SecretUnavailable(
            f"Could not read {secret_reference}: the 1Password CLI is not installed. "
            "See https://developer.1password.com/docs/cli/get-started/"
        ) from e
    except subprocess.CalledProcessError as e:
        raise SecretUnavailable(
            f"Could not read {secret_reference}: {e.stderr.strip() or 'op exited ' + str(e.returncode)}"
        ) from e

    return result.stdout.strip()
