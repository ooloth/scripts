# Modem Restart

Because this GitHub Actions workflow requires remote access to my LAN in order to visit the modem settings page, I've leveraged Tailscale to give the GitHub Actions runner temporary access to my local network.

## Tailscale

### Add Tailscale GitHub Action

To temporarily add the GitHub Actions runner as an ephemeral node in my tailnet, I...

1. Added an Oath client with the `devices:write` scope (so the node the workflow creates can be tagged) in my Tailscale admin console
1. Stored the client ID and secret in 1Password (for safekeeping)
1. Stored the client ID and secret in two repository secrets named `TS_OAUTH_CLIENT_ID` and `TS_OAUTH_SECRET` (for the workflow to use)
1. Added the following step to the workflow:

```yaml
- name: Tailscale
  uses: tailscale/github-action@v2
  with:
    oauth-client-id: ${{ secrets.TS_OAUTH_CLIENT_ID }}
    oauth-secret: ${{ secrets.TS_OAUTH_SECRET }}
    tags: tag:ci
```

1. Added the `tag:ci` tag to the Access control rules in the Tailscale admin console:

```json
"tagOwners": {
  "tag:ci": ["autogroup:admin"],
}
```

1. Assigned one of the permanent nodes in my tailnet to act as a subnet router so the temporary workflow node will be able to find my modem's settings using its LAN IP address by running the following command on that device and then approving the subnet router on the Tailscale admin console:

```sh
$ tailscale set --advertise-routes "192.168.2.0/24"
```

After all of those steps, the workflow was finally able to access my modem settings page and restart the modem.

**References:**
- [Turbocharge Your DevOps Workflow with GitHub Actions and Tailscale SSH](https://www.youtube.com/watch?v=WXCokV-FeFw) • Tailscale 📺
- [Tailscale GitHub Action](https://tailscale.com/kb/1276/tailscale-github-action) • Tailscale Docs 📚
- [Discussion: Stuck implementing OAuth Client for GitHub Actions CI/CD · Issue #79](https://github.com/tailscale/github-action/issues/79) • GitHub 💬
- [Update the docs on ACL tag's owners and OAuth client scopes · Issue #104](https://github.com/tailscale/github-action/issues/104) • GitHub 💬
- [Subnet routers](https://www.youtube.com/watch?v=UmVMaymH1-s) • Tailscale 📺
- [Subnet routers](https://tailscale.com/kb/1019/subnets?tab=macos) • Tailscale Docs 📚

## Alternatives considered

To avoid inviting an external server into my tailnet, I thought about scheduling this script to run on a local device via launchd or cron, but that would have required exposing my 1Password Service Account token as plain text, which I wanted to avoid.
