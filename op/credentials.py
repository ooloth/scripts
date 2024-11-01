import subprocess


def get_username(item: str) -> str:
    result = subprocess.run(
        ["op", "item", "get", item, "--field", "password"], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def get_password(item: str) -> str:
    result = subprocess.run(
        ["op", "item", "get", "--reveal", item, "--field", "password"], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()
