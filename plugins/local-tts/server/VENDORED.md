# Vendored from kokoro-tts-server

This directory is a copy of the standalone
[kokoro-tts-server](https://github.com/csabakecskemeti/kokoro-tts-server)
project, bundled so the plugin can **build the image itself** when the
published one cannot be pulled — offline, behind a proxy, on an architecture
with no published tag, or simply before the image has been released.

Without it, `/tts server up` could only tell you to go and find a repository
you do not have.

- Upstream commit: `d6c76f1`
- Re-sync with: `scripts/sync-server.sh /path/to/kokoro-tts-server`

The upstream project remains the source of truth: it holds the tests and the
CI that publishes to GHCR. Edit there, then re-sync here.
