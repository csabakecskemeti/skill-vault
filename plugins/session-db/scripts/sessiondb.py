#!/usr/bin/env python3
"""Searchable archive of Claude Code sessions.

Claude Code keeps session transcripts as JSONL under ~/.claude/projects and
deletes them after `cleanupPeriodDays` (30 by default). This indexes the
conversational text of every session into a SQLite FTS5 database that keeps
its own copy, so history stays searchable after the transcripts are gone.

Standard library only. Indexing is incremental: transcripts are append-only,
so each file is read from the byte offset where the last run stopped.
"""

import argparse
import fcntl
import json
import os
import re
import socket
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone

HOME = os.path.expanduser("~")
DEFAULT_SOURCE = os.path.join(HOME, ".claude", "projects")
DEFAULT_DB = os.environ.get(
    "SESSION_DB", os.path.join(HOME, ".claude", "session-db", "sessions.db")
)
MAX_TEXT = 20000  # per message; long pastes are truncated, not dropped
SCHEMA_VERSION = 1

# Harness-injected text that is noise for search.
NOISE_BLOCK = re.compile(
    r"<(system-reminder|task-notification|local-command-stdout|local-command-stderr)>.*?</\1>",
    re.S,
)
COMMAND_TAG = re.compile(r"</?(command-name|command-message|command-args)>")


# --------------------------------------------------------------------------- db

def connect(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    db = sqlite3.connect(path, timeout=30)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=30000")
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE IF NOT EXISTS files (
            path TEXT PRIMARY KEY, session_id TEXT, size INTEGER, offset INTEGER,
            mtime REAL, indexed_at TEXT
        );
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            name TEXT, ai_title TEXT, cwd TEXT, project TEXT, git_branch TEXT,
            started TEXT, updated TEXT,
            n_user INTEGER DEFAULT 0, n_assistant INTEGER DEFAULT 0,
            first_prompt TEXT, last_prompt TEXT, host TEXT
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            uuid TEXT UNIQUE, session_id TEXT NOT NULL,
            ts TEXT, role TEXT, text TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, ts);
        CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
            text, content='messages', content_rowid='id', tokenize='porter unicode61'
        );
        CREATE TRIGGER IF NOT EXISTS messages_ai AFTER INSERT ON messages BEGIN
            INSERT INTO messages_fts(rowid, text) VALUES (new.id, new.text);
        END;
        CREATE TRIGGER IF NOT EXISTS messages_ad AFTER DELETE ON messages BEGIN
            INSERT INTO messages_fts(messages_fts, rowid, text) VALUES ('delete', old.id, old.text);
        END;
        """
    )
    db.execute(
        "INSERT OR IGNORE INTO meta VALUES ('schema_version', ?)", (str(SCHEMA_VERSION),)
    )
    return db


# ---------------------------------------------------------------------- parsing

def clean(text):
    text = NOISE_BLOCK.sub("", text)
    text = COMMAND_TAG.sub("", text)
    return text.strip()[:MAX_TEXT]


def message_text(event):
    """Human-readable text of a user/assistant event, or '' if it has none."""
    content = (event.get("message") or {}).get("content")
    if isinstance(content, str):
        return clean(content)
    if isinstance(content, list):
        # Only text blocks: tool calls and tool results are mechanics, not conversation.
        parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
        return clean("\n".join(p for p in parts if p))
    return ""


def index_file(db, path, host, force=False):
    """Index new lines of one transcript. Returns the number of messages added."""
    try:
        st = os.stat(path)
    except OSError:
        return 0
    row = db.execute("SELECT size, offset FROM files WHERE path=?", (path,)).fetchone()
    offset = 0
    if row and not force:
        if st.st_size == row["size"]:
            return 0
        if st.st_size > row["offset"]:
            offset = row["offset"]
        # A file that shrank was rewritten: read it again from the start. Messages
        # already stored are kept (uuid dedupe), so nothing is lost either way.

    sid = os.path.splitext(os.path.basename(path))[0]
    sess = {}
    added = 0
    with open(path, "rb") as f:
        f.seek(offset)
        while True:
            line = f.readline()
            if not line:
                break
            if not line.endswith(b"\n"):
                break  # partial line still being written; pick it up next run
            offset += len(line)
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            sid = ev.get("sessionId") or sid
            t = ev.get("type")
            if t == "custom-title" and ev.get("customTitle"):
                sess["name"] = ev["customTitle"]
            elif t == "ai-title" and ev.get("aiTitle"):
                sess["ai_title"] = ev["aiTitle"]
            if ev.get("cwd") and "cwd" not in sess:
                sess["cwd"] = ev["cwd"]
                sess["project"] = os.path.basename(ev["cwd"].rstrip("/")) or ev["cwd"]
            if ev.get("gitBranch"):
                sess["git_branch"] = ev["gitBranch"]
            ts = ev.get("timestamp")
            if ts:
                sess.setdefault("started", ts)
                sess["updated"] = ts
            if t not in ("user", "assistant") or ev.get("isSidechain") or ev.get("isMeta"):
                continue
            text = message_text(ev)
            if not text:
                continue
            role = t
            if t == "user" and ev.get("isCompactSummary"):
                role = "summary"
            cur = db.execute(
                "INSERT OR IGNORE INTO messages(uuid, session_id, ts, role, text) VALUES (?,?,?,?,?)",
                (ev.get("uuid") or f"{sid}:{offset}", sid, ts, role, text),
            )
            if cur.rowcount:
                added += 1
                key = "n_user" if role == "user" else "n_assistant" if role == "assistant" else None
                if key:
                    sess[key] = sess.get(key, 0) + 1
                if role == "user":
                    sess.setdefault("first_prompt", text[:500])
                    sess["last_prompt"] = text[:500]

    upsert_session(db, sid, sess, host)
    db.execute(
        "INSERT OR REPLACE INTO files VALUES (?,?,?,?,?,?)",
        (path, sid, st.st_size, offset, st.st_mtime, now_iso()),
    )
    return added


def upsert_session(db, sid, s, host):
    db.execute("INSERT OR IGNORE INTO sessions(session_id, host) VALUES (?,?)", (sid, host))
    cur = db.execute("SELECT * FROM sessions WHERE session_id=?", (sid,)).fetchone()
    merged = dict(cur)
    for k in ("name", "ai_title", "git_branch", "last_prompt"):
        if s.get(k):
            merged[k] = s[k]
    # `claude --resume` only finds a session from the directory it was started in,
    # so keep the first cwd rather than wherever the session later cd'd to.
    for k in ("cwd", "project"):
        if s.get(k) and not merged[k]:
            merged[k] = s[k]
    if s.get("first_prompt") and not merged["first_prompt"]:
        merged["first_prompt"] = s["first_prompt"]
    if s.get("started") and (not merged["started"] or s["started"] < merged["started"]):
        merged["started"] = s["started"]
    if s.get("updated") and (not merged["updated"] or s["updated"] > merged["updated"]):
        merged["updated"] = s["updated"]
    merged["n_user"] = (merged["n_user"] or 0) + s.get("n_user", 0)
    merged["n_assistant"] = (merged["n_assistant"] or 0) + s.get("n_assistant", 0)
    cols = [k for k in merged if k != "session_id"]
    db.execute(
        f"UPDATE sessions SET {', '.join(c + '=?' for c in cols)} WHERE session_id=?",
        [merged[c] for c in cols] + [sid],
    )


def transcripts(root):
    for dirpath, dirnames, filenames in os.walk(root):
        # Subagent transcripts are sidechains of their parent; memory is not a session.
        dirnames[:] = [d for d in dirnames if d not in ("subagents", "memory", ".git")]
        for fn in filenames:
            if fn.endswith(".jsonl"):
                yield os.path.join(dirpath, fn)


# --------------------------------------------------------------------- commands

def cmd_index(db, args):
    lock_path = args.db + ".lock"
    lock = open(lock_path, "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        if not args.quiet:
            print("Another indexer is running; skipping.")
        return
    host = socket.gethostname().split(".")[0]
    t0 = time.time()
    files = added = 0
    for root in args.path or [DEFAULT_SOURCE]:
        for p in transcripts(os.path.expanduser(root)):
            n = index_file(db, p, host, force=args.force)
            db.commit()
            files += 1
            added += n
    if not args.quiet:
        total = db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        print(f"Scanned {files} transcripts, added {added} messages in {time.time()-t0:.1f}s. "
              f"{total} sessions indexed.")


def fts_query(q, raw):
    if raw or re.search(r'["*()]|\b(AND|OR|NOT|NEAR)\b', q):
        return q
    words = re.findall(r"\w+", q)
    return " ".join(f'"{w}"' for w in words)


def since_ts(s):
    if not s:
        return None
    m = re.fullmatch(r"(\d+)([dwm])", s)
    if m:
        n, unit = int(m.group(1)), m.group(2)
        days = n * {"d": 1, "w": 7, "m": 30}[unit]
        return (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
    return s  # an ISO date like 2026-09-01


def cmd_search(db, args):
    q = fts_query(args.query, args.raw)
    where, params = ["messages_fts MATCH ?"], [q]
    if args.project:
        where.append("(s.project LIKE ? OR s.cwd LIKE ?)")
        params += [f"%{args.project}%"] * 2
    if args.session:
        sid = resolve(db, args.session)
        if not sid:
            return
        where.append("m.session_id = ?")
        params.append(sid)
    if args.role:
        where.append("m.role = ?")
        params.append(args.role)
    if args.since:
        where.append("m.ts >= ?")
        params.append(since_ts(args.since))
    sql = f"""
        SELECT m.id, m.ts, m.role, m.session_id, s.name, s.ai_title, s.project,
               snippet(messages_fts, 0, '[', ']', ' … ', 24) AS snip
        FROM messages_fts JOIN messages m ON m.id = messages_fts.rowid
        JOIN sessions s ON s.session_id = m.session_id
        WHERE {' AND '.join(where)}
        ORDER BY {'m.ts DESC' if args.recent else 'bm25(messages_fts)'}
        LIMIT ?"""
    try:
        rows = db.execute(sql, params + [args.limit]).fetchall()
    except sqlite3.OperationalError as e:
        sys.exit(f"Bad query {q!r}: {e}. Use --raw for FTS5 syntax, or plain words.")
    if not rows:
        print("No matches.")
        return
    if args.by_session:
        seen = {}
        for r in rows:
            seen.setdefault(r["session_id"], []).append(r)
        for sid, hits in seen.items():
            r = hits[0]
            print(f"{sid[:8]}  {label(r)}  [{r['project'] or '?'}]  {len(hits)} hit(s), latest {day(max(h['ts'] or '' for h in hits))}")
        return
    for r in rows:
        snip = " ".join(r["snip"].split())
        print(f"#{r['id']}  {day(r['ts'])}  {r['session_id'][:8]}  {label(r)}  [{r['project'] or '?'}]  {r['role']}")
        print(f"    {snip}")
    print(f"\nRead around a hit: sessiondb.py show <session> --around <#id>")


def cmd_sessions(db, args):
    where, params = [], []
    if args.project:
        where.append("(project LIKE ? OR cwd LIKE ?)")
        params += [f"%{args.project}%"] * 2
    if args.since:
        where.append("updated >= ?")
        params.append(since_ts(args.since))
    sql = "SELECT * FROM sessions"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY updated DESC LIMIT ?"
    for r in db.execute(sql, params + [args.limit]):
        n = (r["n_user"] or 0) + (r["n_assistant"] or 0)
        print(f"{r['session_id'][:8]}  {day(r['updated'])}  {label(r):40.40}  [{r['project'] or '?'}]  {n} msgs")


def cmd_show(db, args):
    sid = resolve(db, args.session)
    if not sid:
        return
    s = db.execute("SELECT * FROM sessions WHERE session_id=?", (sid,)).fetchone()
    print(f"== {label(s)}  ({sid})")
    print(f"   project: {s['cwd'] or '?'}  branch: {s['git_branch'] or '-'}  host: {s['host']}")
    print(f"   {day(s['started'])} → {day(s['updated'])}   user {s['n_user']} / assistant {s['n_assistant']}")
    print(f"   resume: {resume_cmd(s)}\n")
    if args.around:
        mid = int(str(args.around).lstrip("#"))
        rows = db.execute(
            """SELECT * FROM (SELECT * FROM messages WHERE session_id=? AND id<=? ORDER BY id DESC LIMIT ?)
               UNION SELECT * FROM (SELECT * FROM messages WHERE session_id=? AND id>? ORDER BY id LIMIT ?)
               ORDER BY id""",
            (sid, mid, args.context + 1, sid, mid, args.context),
        ).fetchall()
    elif args.head:
        rows = db.execute("SELECT * FROM messages WHERE session_id=? ORDER BY id LIMIT ?",
                          (sid, args.head)).fetchall()
    elif args.role == "user" and args.all:
        rows = db.execute("SELECT * FROM messages WHERE session_id=? AND role='user' ORDER BY id",
                          (sid,)).fetchall()
    elif args.all:
        rows = db.execute("SELECT * FROM messages WHERE session_id=? ORDER BY id", (sid,)).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM (SELECT * FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?) ORDER BY id",
            (sid, args.last),
        ).fetchall()
    for m in rows:
        if args.role and m["role"] != args.role:
            continue
        mark = " <<" if args.around and m["id"] == int(str(args.around).lstrip("#")) else ""
        text = m["text"] if args.full else trunc(m["text"], args.width)
        print(f"#{m['id']} [{(m['ts'] or '')[:16]}] {m['role'].upper()}{mark}:\n{text}\n")


def cmd_resume(db, args):
    sid = resolve(db, args.session)
    if sid:
        print(resume_cmd(db.execute("SELECT * FROM sessions WHERE session_id=?", (sid,)).fetchone()))


def cmd_stats(db, args):
    n_s = db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    n_m = db.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    first = db.execute("SELECT MIN(started) FROM sessions").fetchone()[0]
    gone = sum(1 for r in db.execute("SELECT path FROM files") if not os.path.exists(r[0]))
    print(f"{n_s} sessions, {n_m} messages, since {day(first)}")
    print(f"{gone} source transcripts no longer on disk (kept here)")
    print(f"db: {args.db} ({os.path.getsize(args.db) // 2**20} MB)")
    print("\nTop projects:")
    for r in db.execute("""SELECT project, COUNT(*) n, MAX(updated) u FROM sessions
                           GROUP BY project ORDER BY u DESC LIMIT 15"""):
        print(f"  {r['project'] or '?':32} {r['n']:4} sessions, last {day(r['u'])}")


# ---------------------------------------------------------------------- helpers

def resolve(db, key):
    """Session id from a full id, an id prefix, or a session name/title."""
    rows = db.execute(
        "SELECT session_id FROM sessions WHERE session_id LIKE ? ORDER BY updated DESC", (key + "%",)
    ).fetchall()
    if not rows:
        rows = db.execute(
            """SELECT session_id FROM sessions WHERE name = ? OR ai_title = ?
               UNION ALL SELECT session_id FROM sessions WHERE name LIKE ? OR ai_title LIKE ?""",
            (key, key, f"%{key}%", f"%{key}%"),
        ).fetchall()
        rows = list(dict.fromkeys(r[0] for r in rows))
    else:
        rows = [r[0] for r in rows]
    if not rows:
        print(f"No session matches {key!r}.")
        return None
    if len(rows) > 1 and not rows[0].startswith(key) and key not in rows[:1]:
        print(f"{key!r} matches {len(rows)} sessions; using the most recent. Others:", file=sys.stderr)
        for r in rows[1:6]:
            print(f"  {r}", file=sys.stderr)
    return rows[0]


def label(r):
    return r["name"] or r["ai_title"] or "(untitled)"


def resume_cmd(s):
    cwd = s["cwd"]
    cd = f"cd {cwd.replace(HOME, '~', 1)} && " if cwd else ""
    return f"{cd}claude --resume {s['session_id']}"


def day(ts):
    return (ts or "")[:10] or "?"


def trunc(t, n):
    t = t or ""
    return t if len(t) <= n else t[:n] + f" … [+{len(t)-n} chars]"


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="Search and resume Claude Code sessions.")
    ap.add_argument("--db", default=DEFAULT_DB, help=f"database path (default {DEFAULT_DB})")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("index", help="index new transcript lines (incremental)")
    p.add_argument("path", nargs="*", help=f"transcript roots (default {DEFAULT_SOURCE})")
    p.add_argument("--force", action="store_true", help="re-read files from the start")
    p.add_argument("-q", "--quiet", action="store_true")

    p = sub.add_parser("search", help="full-text search over messages")
    p.add_argument("query")
    p.add_argument("-n", "--limit", type=int, default=15)
    p.add_argument("-p", "--project", help="substring of project name or cwd")
    p.add_argument("-s", "--session", help="restrict to one session (id, prefix or name)")
    p.add_argument("--role", choices=["user", "assistant", "summary"])
    p.add_argument("--since", help="e.g. 7d, 4w, 3m or 2026-09-01")
    p.add_argument("--recent", action="store_true", help="newest first instead of best match")
    p.add_argument("--by-session", action="store_true", help="one line per matching session")
    p.add_argument("--raw", action="store_true", help="pass the query to FTS5 unchanged")

    p = sub.add_parser("sessions", help="list sessions, most recent first")
    p.add_argument("-n", "--limit", type=int, default=25)
    p.add_argument("-p", "--project")
    p.add_argument("--since")

    p = sub.add_parser("show", help="read a session's messages")
    p.add_argument("session", help="id, id prefix, or name")
    p.add_argument("--around", help="message #id from search; shows context around it")
    p.add_argument("-C", "--context", type=int, default=4)
    p.add_argument("--last", type=int, default=12)
    p.add_argument("--head", type=int)
    p.add_argument("--all", action="store_true")
    p.add_argument("--role", choices=["user", "assistant", "summary"])
    p.add_argument("--full", action="store_true", help="do not truncate messages")
    p.add_argument("-w", "--width", type=int, default=1500)

    p = sub.add_parser("resume", help="print the command to resume a session")
    p.add_argument("session")

    sub.add_parser("stats", help="database summary")

    args = ap.parse_args()
    db = connect(args.db)
    try:
        {"index": cmd_index, "search": cmd_search, "sessions": cmd_sessions, "show": cmd_show,
         "resume": cmd_resume, "stats": cmd_stats}[args.cmd](db, args)
    finally:
        db.close()


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
