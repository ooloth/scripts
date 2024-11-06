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


def get_secret(item: str, field: str) -> str:
    """
    Generates a 1Password secret reference and retrieves the secret value.
    """
    secret_reference = build_secret_reference(item, field)

    result = subprocess.run(
        ["op", "read", secret_reference],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()
