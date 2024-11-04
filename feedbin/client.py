from op.secrets import get_secret

_auth = None


def get_auth() -> tuple[str, str]:
    global _auth

    if _auth is None:
        username = get_secret("Feedbin", "username")
        password = get_secret("Feedbin", "password")

        _auth = (username, password)

    return _auth
