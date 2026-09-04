# local-tts

A Claude Code plugin that reads Claude's replies out loud with
[Kokoro](https://huggingface.co/hexgrad/Kokoro-82M) running **entirely on your
machine**. No API key, no network call at speak time.

## How it works

```
Stop hook ──► stop-hook.sh ──► stop_hook.py ──► unix socket ──► daemon.py
 (per turn)    (detached,       (last reply       (~/.local/     (holds Kokoro
                returns in       from the          share/         in memory)
                ~0.3s)           transcript)       local-tts)
```

Three things make it usable turn after turn:

**A warm daemon.** Loading torch + Kokoro costs ~40 seconds. Paying that per
reply would be absurd, so the model lives in a long-running process behind a
unix socket. The hook only enqueues text and returns, so a turn never waits on
audio.

**Sentence streaming.** Kokoro synthesizes a whole passage before yielding a
single sample, so a long answer would mean a long silence. `split_chunks()`
breaks the text into sentence-sized pieces — a short one first — and the daemon
runs synthesis and playback as two stages of a pipeline: chunk *N+1* is
generated while chunk *N* is still playing.

Measured on an M-series Mac: **0.2 s to first audio** on a warm daemon, versus
~3 s if the whole reply were synthesized before playback.

**An aggressive filter.** Code blocks, tables, diffs, tracebacks, HTML and
shell transcripts are unlistenable. `strip_unspeakable()` drops those by
*line* before any markdown stripping happens, and also drops a dangling lead-in
("Here is the diff:") whose content was just removed. Long file paths collapse
to their basename. So this:

```markdown
## Fixed
The off-by-one was in `client.py`:
```python
for i in range(retries): backoff(i)
```
| file | change |
|---|---|
It now stops after **three** attempts.
```

is spoken as: *"Fixed. It now stops after three attempts."*

## Backends

Synthesis is pluggable; filtering, chunking and playback are not — they live in
the plugin so they behave identically either way.

| Backend | Where the model runs | Setup | Notes |
|---|---|---|---|
| `embedded` (default) | in the daemon, on this machine | `./setup.sh` (~1.1 GB venv) | Fastest; needs Python deps locally |
| `http` | in a container or any OpenAI-compatible service | `/tts server up` | No Python deps here; Docker on macOS is CPU-only, so slower |

```
clean → split → [chunk 1] ─┐
                [chunk 2] ─┼─► backend ──► WAV bytes ──► play on this machine
                [chunk 3] ─┘
```

Chunks are requested one ahead of playback, so audio starts on chunk one
regardless of backend.

### Using the container backend

Build the image from the companion project
[`kokoro-tts-server`](../kokoro-tts-server), then:

```sh
/tts server up          # start it and wait for /health
/tts backend http       # switch the plugin over (restarts the daemon)
/tts status             # confirm it is reachable and API-compatible
```

The plugin checks `/health` for `service` and `api_version`, so a mismatched
container reports as incompatible rather than failing later on a bad request.
A server that isn't a `kokoro-tts-server` is allowed through and treated as a
generic OpenAI `/v1/audio/speech` endpoint.

## Install

Requires `espeak-ng` (Kokoro's phonemizer) and Python 3.9+ for the `embedded`
backend. The `http` backend needs neither — only Docker.

```sh
brew install espeak-ng          # or: sudo apt-get install espeak-ng
./setup.sh                      # builds a venv, pulls torch, caches the model
```

`setup.sh` creates `~/.local/share/local-tts/venv` (~1.1 GB), kept outside the
plugin directory so a plugin update never discards it.

Then add the plugin to Claude Code:

```
/plugin marketplace add csabakecskemeti/skill-vault
/plugin install local-tts@skill-vault
```

Or point at a local checkout with `/plugin marketplace add /path/to/this/repo`.

## Use

Speaking is on by default; it just starts working after the next reply.

| Command | Effect |
|---|---|
| `/tts` | Show voice, speed and daemon status |
| `/tts off` / `/tts on` | Stop / resume speaking replies |
| `/tts stop` | Cut off what is playing right now |
| `/tts voice bm_george` | Switch voice (restarts the daemon) |
| `/tts speed 1.15` | 0.5–2.0; ~1.15 is a good skim speed |
| `/tts backend http` | Switch synthesis backend (`embedded` or `http`) |
| `/tts server up` / `down` | Start or stop the TTS container |
| `/tts log` | Tail the daemon log |
| `/speak <text>` | Say something one-off |

`scripts/tts-ctl.sh` exposes the same surface from a shell, and honours
`LOCAL_TTS_HOME` if you want the runtime somewhere other than
`~/.local/share/local-tts`.

## Config

`~/.local/share/local-tts/config.json`:

| Key | Default | Meaning |
|---|---|---|
| `enabled` | `true` | Whether the Stop hook speaks |
| `voice` | `af_heart` | Kokoro voice; `scripts/config.py voices` lists them |
| `speed` | `1.0` | Playback rate |
| `lang_code` | `a` | `a` American, `b` British — set automatically with the voice |
| `max_chars` | `1200` | Longer replies are truncated at a sentence boundary |
| `backend` | `embedded` | `embedded` or `http` |
| `server_url` | `http://localhost:42821` | Used by the `http` backend |

The daemon exits after three idle hours to give back its ~1 GB.

## Notes

- Only the final text of each turn is spoken; tool calls and intermediate
  messages are skipped, and a repeated `Stop` for the same reply is deduped.
- Playback uses `afplay`, falling back to `paplay`/`aplay`/`ffplay`.
- The standalone service now lives in
  [`kokoro-tts-server`](../kokoro-tts-server) — a Docker image exposing an
  OpenAI-compatible `/v1/audio/speech`. It deliberately does not play audio: a
  container has no sound device, so playback stays here.
- **Next:** an MCP surface over the same server engine, and an MLX backend for
  native Apple-silicon speed (MLX cannot be containerized — no Metal in the
  Docker VM).
