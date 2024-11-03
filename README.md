# 👨‍💻 Scripts

[![.github/workflows/modem-restart.yaml](https://github.com/ooloth/scripts/actions/workflows/modem-restart.yaml/badge.svg)](https://github.com/ooloth/scripts/actions/workflows/modem-restart.yaml)

These scripts are highly experimental and subject to change and are intended for my personal use and learning.

Feel free to copy anything you find useful, but don't rely on anything here remaining stable!

## 🤫 Secrets

- These scripts rely on one [repository secret](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository) named `OP_SERVICE_ACCOUNT_TOKEN` that is used in GitHub Actions workflows
- All other secrets are stored in 1Password and [references to their 1Password locations](https://developer.1password.com/docs/cli/secret-reference-syntax/) are stored as environment variables to avoid storing the actual secret values as plain text anywhere.
