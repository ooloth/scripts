# 🤫 Secrets

- To avoid ever exposing the secrets used by the scripts in this repo as plain text (e.g. in a local `.env` file), they are stored in 1Password and [referenced](https://developer.1password.com/docs/cli/secret-reference-syntax/) by their location in the vault the 1Password service account has access to
- When running these scripts locally, I'm prompted by the 1Password CLI to authenticate with my fingerprint
- To allow running these scripts via GitHub Actions workflows, an `OP_SERVICE_ACCOUNT_TOKEN` [repository secret](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository) is required so the 1Password CLI can authenticate the service account user used in that environment
