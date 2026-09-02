# Claude API Key Setup for SICE Portal Hub

## Purpose

This document prepares the **Linux-hosted SICE Portal Hub** for the later AI Summary module. The current War Room build does **not** call Claude and does not contain any Anthropic credential. The API key must remain server-side and must never be placed in `SICE_WAR_ROOM.html`, another browser-delivered HTML file, JavaScript, `localStorage`, a backup export, or a Git repository.

## Create the Key

Sign in to the [Claude Console API-key page][1]. Create a key named **`SICE Portal Hub — Linux`**, select the appropriate workspace, and set an expiry period that suits the operational review cycle. Anthropic displays a newly created key only once; if it is lost, create and replace it rather than attempting to recover it.[1]

> Do not send the key through chat, include it in screenshots, or paste it into any HTML/JavaScript source file.

## Store It Locally on Linux

On the Linux system that runs the SICE local server, create a restricted configuration directory and environment file:

```bash
install -d -m 700 "$HOME/.config/sice"
nano "$HOME/.config/sice/claude.env"
```

Add exactly one line to the new file, replacing the value locally with the newly created key:

```bash
ANTHROPIC_API_KEY='sk-ant-REPLACE-LOCALLY'
```

Then restrict the file to the local user:

```bash
chmod 600 "$HOME/.config/sice/claude.env"
```

| Location | Required state | Reason |
|---|---|---|
| `~/.config/sice/claude.env` | Owned by the Linux user; mode `600` | Keeps the key outside the portal directory and its backup/export paths. |
| `SICE_WAR_ROOM.html` and other front-end files | No API key or token | Browser code can be inspected by anyone with page access. |
| Future AI Summary endpoint in `sice_server.py` | Reads the environment value server-side | The Claude API accepts a key through request authentication; the browser should call only the local SICE endpoint.[2] |

## Planned Integration Boundary

The subsequent AI Summary module should add a dedicated **local server endpoint** that reads `ANTHROPIC_API_KEY` only from the process environment, calls Anthropic’s Messages API, applies strict request-size limits, and returns only the completed summary to the browser. The key must never be written to logs or echoed in diagnostic responses. Anthropic’s official guidance identifies `ANTHROPIC_API_KEY` as the standard environment-variable name and the API expects authentication on server-to-server requests.[1] [2]

The local server launcher should load the secret immediately before the server starts. This will be implemented only with the AI Summary build, after the key exists and the intended source material, prompt policy, data-retention rules, and output audience are confirmed.

## References

[1]: https://platform.claude.com/docs/en/get-api-key "Anthropic: Get your Claude API key"
[2]: https://platform.claude.com/docs/en/api/overview "Anthropic: API overview and authentication"
