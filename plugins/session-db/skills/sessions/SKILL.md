---
name: sessions
description: Search, read and resume past Claude Code sessions from a local full-text archive. Use when the user refers to another or earlier session (by name, id, or topic), asks what was said, decided or done before ("what did we decide about X", "where did I leave off on Y", "find the session where..."), wants to resume or continue earlier work, or when you need context from past work on a project before advising on it.
allowed-tools:
  - Bash
---

# /sessions — search and resume past sessions

Every Claude Code session on this machine is indexed into a SQLite full-text archive at
`~/.claude/session-db/sessions.db`. The archive keeps its own copy of the conversation text, so
sessions stay searchable after Claude Code deletes old transcripts (`cleanupPeriodDays`, 30 by
default). Hooks index new messages at session start and end.

Run everything through:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sessiondb.py" <command> ...
```

Before searching, run `index -q` once: it takes well under a second and picks up messages from
sessions that are still open, including this one.

## Commands

| Command | Use |
|---|---|
| `index -q` | Pick up new messages (incremental). `index <dir>` also imports a backup copy of `~/.claude/projects`. |
| `search "<words>"` | Best-matching messages, with a snippet, date, session and message `#id`. |
| `search "<words>" --by-session` | One line per matching session. Good first step for "which session was that?". |
| `sessions [-p project] [--since 7d]` | Recent sessions with name, date, project and size. |
| `show <session> --around <#id> [-C 6]` | Read the conversation around a search hit. |
| `show <session> [--last 12 \| --head 10 \| --all] [--role user] [--full]` | Read a session's messages. |
| `resume <session>` | The exact command to resume it: `cd <dir> && claude --resume <id>`. |
| `stats` | Size of the archive, top projects, transcripts that exist only in the archive. |

`<session>` can be a full id, an id prefix (`8d779eeb`), or a session name or title
(`neonectar-project`).

Search filters: `-p/--project <substr>`, `-s/--session <session>`, `--role user|assistant|summary`,
`--since 7d|4w|3m|2026-09-01`, `--recent` (newest first), `-n` (limit). Plain words are ANDed;
use `--raw` for FTS5 syntax (`"exact phrase"`, `OR`, `NEAR`, `prefix*`).

## How to answer from it

1. Search. If the first query misses, try different words: the archive holds what was actually
   said, which is often not the word the user uses now.
2. Read around the best hits with `show --around` before concluding. A snippet is not enough
   to report a decision.
3. Answer with the source: session name and id, date, and what was said. Quote the user's own
   words when they matter.
4. If the user wants to continue that work, give them the `resume` command. Resuming only works
   from the directory the session started in, which is why it includes the `cd`.

What is indexed: user and assistant text of main-thread messages, plus compaction summaries.
Tool calls, tool output and subagent transcripts are not indexed.
