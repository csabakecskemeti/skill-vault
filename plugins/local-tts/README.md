# local-tts

A Claude Code plugin that reads Claude's replies out loud with
[Kokoro](https://huggingface.co/hexgrad/Kokoro-82M). Everything runs on your
machine — no API key, and no network call when it speaks.

## How it works

Two pieces, with a clear split of labour:

```
   ┌─ this machine ────────────────────────────────┐   ┌─ container ──────────┐
   │                                               │   │                      │
   │  Stop hook ──► local daemon                   │   │  kokoro-tts-server   │
   │  (per turn,    · dedupe the reply             │   │  · Kokoro + 28 voices│
   │   detached,    · filter out code/tables       │   │  · POST /v1/audio/   │
   │   ~0.3s)       · split into sentences  ───────┼──►│      speech          │
   │                · play the audio       ◄───────┼───┤  · returns WAV bytes │
   │                                               │   │                      │
   └───────────────────────────────────────────────┘   └──────────────────────┘
                     :42821
```

**The container synthesizes. The daemon orchestrates and plays.** The daemon is
not where the model lives — it dedupes the reply, filters it, splits it into
sentences, asks a backend for audio, and plays what comes back. That is why
swapping the backend changes nothing about how the plugin behaves.

Playback can never move into the container: on macOS Docker runs inside a Linux
VM with no CoreAudio access and no `/dev/snd`, so a container physically cannot
make sound. It hands back bytes.

Three things make it usable turn after turn:

**The hook never blocks.** It buffers the payload, hands it to a detached
worker, and returns in ~0.3 s. A turn never waits on synthesis or playback.

**Sentence streaming.** Kokoro emits nothing until it has synthesized a whole
passage, so a long answer would mean a long silence. `split_chunks()` breaks
text into sentence-sized pieces — a deliberately short one first — and requests
chunk *N+1* while chunk *N* is still playing.

**An aggressive filter.** Code, tables, diffs, tracebacks, HTML and shell
transcripts are unlistenable. `strip_unspeakable()` drops them by *line* before
any markdown stripping, and also drops a dangling lead-in ("Here is the diff:")
whose content was just removed. Long paths collapse to their basename. So this:

````markdown
## Fixed
The off-by-one was in `client.py`:
```python
for i in range(retries): backoff(i)
```
| file | change |
|---|---|
It now stops after **three** attempts.
````

is spoken as: *"Fixed. It now stops after three attempts."*

Filtering and splitting live in the plugin rather than the server, so they work
identically on every backend — including `embedded`, which has no server to ask.

## Backends

| Backend | Model runs | Setup | First audio | Notes |
|---|---|---|---|---|
| `embedded` (default) | in the daemon | `./setup.sh` (~1.1 GB venv) | **0.2–0.8 s** | Fastest. Needs Python deps locally |
| `http` | in a container, or any OpenAI-compatible service | `/tts server up` (1.9 GB image) | **~2.6 s** | No Python deps here. Docker on macOS is CPU-only — no Metal — hence slower |

```
clean → split → [chunk 1] ─┐
                [chunk 2] ─┼─► backend ──► WAV bytes ──► played on this machine
                [chunk 3] ─┘
```

Chunks are requested one ahead of playback, so audio starts on chunk one on
either backend.

### What `/tts server up` does

It is idempotent and says which of four situations it found — already
serving, container stopped, image present, or nothing local at all. The last is
the slow case and announces itself first:

```
FIRST-TIME SETUP: no local image found.
Pulling ghcr.io/csabakecskemeti/kokoro-tts-server:latest -- this is a multi-GB
download and will take several minutes. It happens once; later starts are seconds.
```

A locally built image wins over the published one — if you built it, you meant
it. If the pull fails it tells you to build from
[`kokoro-tts-server`](../kokoro-tts-server) rather than dying quietly.

The plugin checks `/health` for `service` and `api_version`, so it can tell
"server is down" from "server speaks a contract I don't understand". A server
that isn't a `kokoro-tts-server` is allowed through and treated as a generic
OpenAI `/v1/audio/speech` endpoint.

The host port is **42821** — deliberately odd, since 8080 collides with almost
everything, and below the macOS ephemeral range (49152+) so it can't clash with
a transient bind. Override with `KOKORO_TTS_PORT`.

## Install

```
/plugin marketplace add csabakecskemeti/skill-vault
/plugin install local-tts@skill-vault
```

Or point at a local checkout with `/plugin marketplace add /path/to/this/repo`.

Then pick a backend. `embedded` is the default, because it needs no Docker and
is the faster of the two; switch to `http` when you would rather not keep a
1.1 GB venv on this machine.

### Container (no Python deps here)

Only Docker is required.

```sh
/tts server up          # pull-or-start the container, wait for /health
/tts backend http       # switch the plugin over (restarts the daemon)
/tts status             # confirm reachable and API-compatible
```

### Embedded (lowest latency)

Needs `espeak-ng` (Kokoro's phonemizer) and Python 3.9+.

```sh
brew install espeak-ng          # or: sudo apt-get install espeak-ng
./setup.sh                      # venv + torch + model cache
/tts backend embedded
```

`setup.sh` builds `~/.local/share/local-tts/venv` (~1.1 GB) outside the plugin
directory, so a plugin update never discards it. It refuses to run without
`espeak-ng` rather than failing later.

## Use

Speaking is on by default; it starts working after the next reply.

| Command | Effect |
|---|---|
| `/tts` | Voice, speed, backend and daemon status |
| `/tts off` / `/tts on` | Stop / resume speaking replies |
| `/tts stop` | Cut off what is playing right now |
| `/tts voice bm_george` | Switch voice (restarts the daemon) |
| `/tts speed 1.15` | 0.5–2.0; ~1.15 is a good skim speed |
| `/tts backend embedded\|http` | Switch synthesis backend |
| `/tts server up\|down\|status\|logs\|pull\|rm` | Manage the TTS container |
| `/tts log` | Tail the daemon log |
| `/speak <text>` | Say something one-off |

`scripts/tts-ctl.sh` exposes the same surface from a shell and honours
`LOCAL_TTS_HOME` if you want the runtime somewhere other than
`~/.local/share/local-tts`.

## Config

`~/.local/share/local-tts/config.json`:

| Key | Default | Meaning |
|---|---|---|
| `enabled` | `true` | Whether the Stop hook speaks |
| `voice` | `af_heart` | 28 voices; `scripts/config.py voices` lists them |
| `speed` | `1.0` | Playback rate |
| `lang_code` | `a` | `a` American, `b` British — set automatically with the voice |
| `max_chars` | `1200` | Longer replies truncate at a sentence boundary |
| `backend` | `embedded` | `embedded` or `http` |
| `server_url` | `http://localhost:42821` | Used by the `http` backend |
| `request_timeout` | `120` | Seconds to wait on the `http` backend |

## Notes

- Only the final text of each turn is spoken. Tool calls and intermediate
  messages are skipped, and a repeated `Stop` for the same reply is deduped.
- The daemon **refuses to start** when it cannot synthesize — missing venv, or
  an unreachable/incompatible server. Accepting text and failing into an unread
  log is a worse failure than never starting, so `/tts status` names the cause.
- The daemon exits after three idle hours on either backend, and restarts on the
  next reply. On `embedded` that hands back the model's ~1 GB; on `http` there
  was never a model here to hand back.
- Playback uses `afplay`, falling back to `paplay`/`aplay`/`ffplay`.
- The container bakes in the model **and all 28 voice tensors**, and runs with
  `HF_HUB_OFFLINE=1`. Without the voices, a first request for a new voice
  silently downloaded from HuggingFace — which defeats the point of a local
  service and fails outright on an offline host.
- Switching backends or voices restarts the daemon: the pipeline is built per
  language at load time.

## Next

- An MCP surface over the server engine, so other clients get `speak`,
  `clean_text` and `split_text` as tools. MCP can't replace the Stop hook —
  tools are called *during* generation, but the final reply only exists after
  it, so the hook stays the trigger.
- An MLX backend for native Apple-silicon speed. It can't be containerized,
  for the same reason the container is CPU-only: no Metal in the Docker VM.
