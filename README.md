# 👨‍💻 Scripts

[![.github/workflows/modem-restart.yaml](https://github.com/ooloth/scripts/actions/workflows/modem-restart.yaml/badge.svg)](https://github.com/ooloth/scripts/actions/workflows/modem-restart.yaml)

These scripts are highly experimental and subject to change and are intended for my personal use and learning.

Feel free to copy anything you find useful, but don't rely on anything here remaining stable!

## 🤫 Secrets

- To avoid ever exposing the secrets used by these scripts as plain text (e.g. in a local `.env` file), they are stored in 1Password and [referenced](https://developer.1password.com/docs/cli/secret-reference-syntax/) by their location in the vault my 1Password service account has access to
- To run these scripts as GitHub Actions workflows, one [repository secret](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository) named `OP_SERVICE_ACCOUNT_TOKEN` is needed to provide the service account token to the 1Password CLI
- Locally, the 1Password CLI authenticates me by asking for my fingerprint
