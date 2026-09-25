# session-db

A searchable archive of your Claude Code sessions. Find what was said or decided in any past
session, read around it, see what each session touched, and get the exact command to resume it.
Optionally, keep a short summary card per session, made by a model you choose.

Claude Code deletes session transcripts after `cleanupPeriodDays` (30 by default). This plugin
copies the conversational text into its own SQLite database, so history stays searchable after
the originals are gone.

## Install

```
/plugin marketplace add csabakecskemeti/skill-vault
/plugin install session-db@skill-vault
```

Nothing else is needed: the first command you run (or the next session start) builds the index,
and later runs only read what is new. Requires Python 3.9+ with SQLite FTS5 (macOS and most
Linux builds have it). No packages.

To import an older backup copy of `~/.claude/projects` as well:

```bash
sessiondb.py index /path/to/backup/projects ~/.claude/projects
```

## Use

Ask Claude in any session. The `sessions` skill triggers on things like:

- "what did we decide about the neonectar contract?"
- "find the session where I set up the Coinbase MCP"
- "where did I leave off on sysdesign_ai?"

Or call it yourself (`sessiondb.py` lives in the plugin's `scripts/`):

```bash
sessiondb.py search "rejection feedback" --by-session
sessiondb.py show 07c2edd0 --around 502 -C 6
sessiondb.py sessions -p neonectar --status
sessiondb.py card neonectar-project
sessiondb.py resume neonectar-project
#   cd ~/Documents/workspace/neonectar && claude --resume 8d779eeb-...
```

## Summary cards (opt-in)

A card is a short JSON summary of one session: title, goal, status, a timeline of phases,
decisions, outcomes, open threads and key facts. Every item cites the message `#id` it came
from, so it can be checked with `show --around`. Cards are searchable (`search --cards`).

**Cards are off by default.** Summarizing needs an LLM, and which one (and who pays for it) is
your call. Turn them on with one of:

```bash
# headless `claude -p` on your own Claude Code login; counts against your plan
sessiondb.py cards-setup claude --model haiku

# any OpenAI-compatible endpoint: local vLLM or Ollama, OpenAI, OpenRouter, ...
sessiondb.py cards-setup openai --base-url 'http://localhost:11434/v1' --model qwen3
sessiondb.py cards-setup openai --base-url '${SPARK_BASE_URL_LAN}/v1' --model local-model \
    --key-env SPARK_API_KEY --no-thinking

sessiondb.py cards-setup off
sessiondb.py config          # what is set up now
```

Each setup runs a one-call test. The config lives next to the database
(`~/.claude/session-db/config.json`); `${VAR}` in `base_url` is expanded from the environment,
and keys are only ever read from the environment variable you name.

**When cards are made.** In the background, from the session hooks, for a session that has
been quiet for 30 minutes and has at least 6 messages (first card) or 20 new ones (update). At
most 5 sessions per run. `card <session> --refresh` updates one on demand; `cards --all`
backfills everything. All thresholds are in `config.json` under `cards`.

**How, and what it costs.** Two levels, because rewriting one running card batch by batch
drifts toward the latest batch and forgets how long sessions started:

1. The session's messages are cut into stretches of ~60k characters (each message capped at
   3,000), and each stretch is summarized independently. Stretch summaries are stored, so
   each message is summarized once, ever.
2. The card is written in one pass over all stretch summaries, in order. That input is a few
   thousand tokens even for a very long session.

Only conversation text is sent, never tool output. On one archive of 81 sessions the whole
history was about 400k tokens, the largest session about 91k, and a typical day adds 5–40k.
With `claude -p`, the Claude Code system prompt is replaced and tools are disabled, so per-call
overhead is a few hundred tokens. A card for a 700-message session took about a minute on a
local Qwen and under a minute on Haiku.

## How it works

- **Source:** `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`, one JSON event per line.
- **Indexed:** user and assistant text from the main thread, plus compaction summaries. System
  reminders and command wrappers are stripped. From tool calls, only files written
  (Write/Edit) and git commits/pushes are kept. Tool output and subagent transcripts are
  skipped.
- **Always current:** every read command first reads whatever is new (a no-change run only
  stats each file). `SessionStart`/`SessionEnd` hooks also run it in the background, which
  rescues transcripts Claude Code is about to delete at startup, and then update due cards.
- **Incremental:** transcripts are append-only, so each file is read from the byte offset the
  last run stopped at. Messages are keyed by event `uuid`, so re-reading never duplicates.
- **Session names:** `/rename` titles are used when present, else Claude's generated title.
- **Resume:** records the directory each session started in, because `claude --resume` only
  finds a session from there.
- **Local and private:** the database is created readable only by you (`0600`). Nothing is
  redacted: a key or password that appeared in a session is in the archive too, on purpose,
  since this may be the only place it survives.

Database: `~/.claude/session-db/sessions.db` (override with `SESSION_DB` or `--db`).

| Table | Holds |
|---|---|
| `sessions` | id, name, title, start dir, project, branch, first/last dates, counts, host |
| `messages` | one row per message: uuid, session, timestamp, role, text; FTS5-indexed |
| `touches` | files written and git operations per session |
| `segments` | stretch summaries (cards only) |
| `cards` | one card per session and the last message it covers; FTS5-indexed |
| `files` | per-transcript byte offset for incremental indexing |

## Later

- **Retiring sessions.** Suggest, never delete: mark sessions dormant after inactivity (and
  when their projectz project is archived) so they rank lower; an exclude list for folders
  that should not be indexed; a manual `forget <session>`.
- **Multiple machines.** Rows record their `host`, so archives from several machines can be
  merged. No sync yet.
- **Semantic search** on top of the keyword index, for when the words used now differ from the
  words used then.
- **Local-only sessions and a PII-safe local agent.** Deliberately not built here. The idea: a
  session (or a whole projectz project, e.g. client work) flagged `local-only` stays findable,
  but its content is only ever shown to, or summarized by, a local model. Enforcing that inside
  this plugin would only be a guardrail, since any agent with shell access can open the
  database file. Real enforcement is a separate system: a local agent that alone holds
  sensitive data and answers cloud agents with what it judges safe to share. Until then, which
  model reads what is the user's choice, made through what they run Claude Code on and what
  they pass to `cards-setup`.
