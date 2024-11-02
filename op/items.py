import subprocess
from typing import Literal

# from op.vaults import get_vault_id

# Docs (service accounts):
# - https://developer.1password.com/docs/service-accounts/get-started/
# - https://developer.1password.com/docs/service-accounts/use-with-1password-cli/
# - https://developer.1password.com/docs/service-accounts/manage-service-accounts/
# - https://developer.1password.com/docs/ci-cd/github-actions/
# - https://developer.1password.com/docs/sdks/
# - https://github.com/1Password/onepassword-sdk-python/blob/main/example/example.py
# - https://developer.1password.com/docs/cli/reference/

SERVICE_ACCOUNT_VAULT = "My Scripts"

Field = Literal["username", "password", "credential"]


def get_item_field_value(item: str, field: Field) -> str:
    result = subprocess.run(
        ["op", "item", "get", item, "--field", field, "--vault", SERVICE_ACCOUNT_VAULT, "--reveal"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()
