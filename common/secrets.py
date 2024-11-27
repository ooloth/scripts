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


def get_secret(item: str, field: str) -> PasswordOrStringifiedJson:
    """
    Generate a 1Password secret reference and retrieve the secret's value.
    """
    secret_reference = build_secret_reference(item, field)

    result = subprocess.run(
        ["op", "read", secret_reference],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()
