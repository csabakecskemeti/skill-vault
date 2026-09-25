# session-db

A searchable archive of your Claude Code sessions. Find what was said or decided in any past
session, read around it, and get the exact command to resume it.

Claude Code deletes session transcripts after `cleanupPeriodDays` (30 by default). This plugin
copies the conversational text into its own SQLite database, so history stays searchable after
the originals are gone.

## Install

```
/plugin marketplace add csabakecskemeti/skill-vault
/plugin install session-db@skill-vault
```

Then build the index once (later runs are incremental and happen automatically):

```bash
python3 ~/.claude/plugins/cache/skill-vault/session-db/*/scripts/sessiondb.py index
```

Requires Python 3.9+ with SQLite FTS5 (the macOS and most Linux builds have it). No packages.

## Use

Ask Claude in any session. The `sessions` skill triggers on things like:

- "what did we decide about the neonectar contract?"
- "find the session where I set up the Coinbase MCP"
- "where did I leave off on sysdesign_ai?"

Or call it yourself (`sessiondb.py` in the plugin's `scripts/`):

```bash
sessiondb.py search "rejection feedback" --by-session
sessiondb.py show 07c2edd0 --around 1312 -C 6
sessiondb.py sessions -p neonectar
sessiondb.py resume neonectar-project
#   cd ~/Documents/workspace/neonectar && claude --resume 8d779eeb-...
```

## How it works

- **Source:** `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`, one JSON event per line.
- **Indexed:** user and assistant text from the main thread, plus compaction summaries.
  System reminders and command wrappers are stripped. Tool calls, tool results and subagent
  transcripts are skipped.
- **Incremental:** transcripts are append-only, so each file is read from the byte offset the
  last run stopped at. Messages are keyed by their event `uuid`, so re-reading never duplicates.
- **Automatic:** `SessionStart` and `SessionEnd` hooks run the indexer in the background. A lock
  file makes overlapping runs skip.
- **Session names:** `/rename` titles (`custom-title`) are used when present, else Claude's
  generated title.
- **Resume:** records the directory each session started in, because `claude --resume` only
  finds a session from there.

Database: `~/.claude/session-db/sessions.db` (override with `SESSION_DB` or `--db`).

| Table | Holds |
|---|---|
| `sessions` | id, name, title, start dir, project, branch, first/last dates, counts, host |
| `messages` | one row per message: uuid, session, timestamp, role, text |
| `messages_fts` | FTS5 index over `messages.text` (porter stemming) |
| `files` | per-transcript byte offset for incremental indexing |

## Not yet

- **Multiple machines.** Each row records its `host`, so archives from several machines can be
  merged later. There is no sync yet.
- **Semantic search.** Keyword search only for now.
