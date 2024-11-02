import subprocess
from typing import Literal

# Docs (service accounts):
# - https://developer.1password.com/docs/service-accounts/get-started/
# - https://developer.1password.com/docs/service-accounts/use-with-1password-cli/
# - https://developer.1password.com/docs/service-accounts/manage-service-accounts/
# - https://developer.1password.com/docs/ci-cd/github-actions/
# - https://developer.1password.com/docs/sdks/
# - https://github.com/1Password/onepassword-sdk-python/blob/main/example/example.py
# - https://developer.1password.com/docs/cli/reference/

SERVICE_ACCOUNT_VAULT = "Scripts"

Field = Literal["username", "password", "credential"]


def get_secret_by_reference(secret_reference: str | None) -> str:
    if not secret_reference:
        raise ValueError("A secret reference is required")

    result = subprocess.run(
        ["op", "read", secret_reference],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


# def get_item_field_value(item: str, field: Field) -> str:
#     result = subprocess.run(
#         ["op", "item", "get", item, "--field", field, "--vault", SERVICE_ACCOUNT_VAULT, "--reveal"],
#         capture_output=True,
#         text=True,
#         check=True,
#     )
#     return result.stdout.strip()
