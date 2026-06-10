---
name: projectz
description: Git-based project tracker and knowledge base. Use when user mentions "my projects", "project tracker", "projectz", or wants to track projects, add notes, manage tasks, or sync work across machines.
license: MIT
compatibility: Requires git and GitHub account
metadata:
  author: csabakecskemeti
  version: "0.6.1"
---

# /projectz - Git-based Project Tracker

A centralized knowledge base for tracking personal projects across multiple computers using Git and Markdown.

**Key features:**
- Track project status (active, backlog, done, etc.)
- Detect your role (owner, fork, contributor, user)
- Store private notes about any project (not committed to project repos)
- Sync everything via Git

---

## Commands

| Command | Description |
|---------|-------------|
| `/projectz` | Show summary of all projects (fast, read-only) |
| `/projectz init <repo-url>` | First-time setup: clone repo, register this computer |
| `/projectz scan` | Discover local repos, update status/role for all projects |
| `/projectz note <project> <text>` | Add a private note about a project |
| `/projectz task <project> <title>` | Add a task to a project |
| `/projectz done <project> <task-id>` | Mark a task as done |
| `/projectz sync` | Commit and push changes to tracker repo |

---

## Definitions

### Computer ID (MAC Address)

Each computer is identified by its primary network interface MAC address (lowercase, no separators).

**macOS:**
```bash
ifconfig en0 | grep ether | awk '{print $2}' | tr -d ':'
# Example output: a1b2c3d4e5f6
```

**Linux:**
```bash
cat /sys/class/net/eth0/address | tr -d ':'
```

**Windows (PowerShell):**
```powershell
(Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -First 1).MacAddress -replace '-',''
```

### Project Slug

URL-friendly identifier derived from project name: lowercase, hyphens instead of spaces.
- "My Cool Project" → `my-cool-project`
- "API_v2" → `api-v2`

### Statuses

| Status | Description | Auto-infer rule |
|--------|-------------|-----------------|
| `draft` | Just created | No commits or only initial commit |
| `active` | Currently working on | Last commit < 14 days ago |
| `backlog` | Paused, will resume | Last commit 14-90 days ago |
| `review` | In review/testing | Manual only |
| `done` | Completed | Manual only |
| `archived` | No longer maintained | Last commit > 90 days (suggest, don't auto-set) |

### Roles

| Role | Description | Detection |
|------|-------------|-----------|
| `owner` | You created it | Your username in remote URL + your first commit |
| `fork` | You forked it | Your username in URL + has `upstream` remote OR first commit not yours |
| `contributor` | You contribute | Not your URL + you have commits |
| `user` | Just using it | Not your URL + no commits from you |

---

## Data Formats

### Local Config: `~/.projectz.yaml`

```yaml
computer_id: a1b2c3d4e5f6
computer_name: macbook-pro
tracker_repo: ~/my-projects    # Path to your tracker repo (any name)
github_username: yourname
git_email: you@example.com
```

**Important:** `tracker_repo` is the path where you cloned your tracker repository. It can be any name (e.g., `~/my-projects`, `~/tracker`, `~/work-tracker`). All commands read this path from config.

### Repository Structure

```
<tracker_repo>/              # e.g., ~/my-projects/
├── README.md
├── AGENTS.md
├── INDEX.md
├── computers/
│   └── <mac-id>.md
└── projects/
    └── <slug>/
        ├── README.md      # What the project is
        ├── MAP.md         # Status, role, metadata
        ├── tasks/
        │   └── 001-<slug>.md
        └── notes/
            └── <date>-<slug>.md
```

### Computer File: `computers/<mac-id>.md`

```markdown
---
id: a1b2c3d4e5f6
name: macbook-pro
registered: 2024-01-15
---

# macbook-pro

## Local Paths

| Project | Path | Last Commit |
|---------|------|-------------|
| my-project | ~/code/my-project | abc1234 |
```

### Project MAP.md

```markdown
---
slug: my-project
status: active
role: owner
repo: https://github.com/user/my-project
has_git: true
tags: [python, web]
created: 2024-01-15
updated: 2024-01-20
last_commit: 2024-01-20
my_commits: 47
total_commits: 52
---

# my-project

**Status:** active | **Role:** owner | **Commits:** 47/52

## Quick Links

- [Tasks](./tasks/)
- [Notes](./notes/)

## Repository

- Remote: https://github.com/user/my-project
- Branch: main

## Recent Notes

- [2024-01-20 - Auth research](./notes/2024-01-20-auth-research.md)
```

### Task File: `tasks/001-setup.md`

```markdown
---
id: "001"
title: Set up project
status: active
priority: high
created: 2024-01-15
---

# Set up project

Description here.

## Acceptance Criteria

- [ ] Directory structure
- [ ] Config files
```

### Note File: `notes/<date>-<slug>.md`

```markdown
---
date: 2024-01-20
tags: [research, auth]
---

# Auth Research

Private notes about authentication approach...
```

---

## Utilities

### Get Tracker Repo Path
```bash
TRACKER_REPO=$(grep tracker_repo ~/.projectz.yaml | cut -d: -f2 | tr -d ' ' | sed "s|~|$HOME|")
```

### Get MAC Address (macOS)
```bash
MAC_ID=$(ifconfig en0 | grep ether | awk '{print $2}' | tr -d ':')
```

### Get Last Commit Date
```bash
LAST_COMMIT=$(git log -1 --format=%Y-%m-%d 2>/dev/null || echo "")
```

### Get Days Since Last Commit
```bash
DAYS_AGO=$(git log -1 --format=%ct 2>/dev/null | xargs -I {} bash -c 'echo $(( ($(date +%s) - {}) / 86400 ))')
```

### Detect Role
```bash
MY_USERNAME=$(grep github_username ~/.projectz.yaml | cut -d: -f2 | tr -d ' ')
MY_EMAIL=$(git config user.email)
ORIGIN=$(git remote get-url origin 2>/dev/null)
IS_MINE=$(echo "$ORIGIN" | grep -qi "$MY_USERNAME" && echo "yes" || echo "no")
HAS_UPSTREAM=$(git remote | grep -q upstream && echo "yes" || echo "no")
FIRST_AUTHOR=$(git log --reverse --format=%ae 2>/dev/null | head -1)
MY_COMMITS=$(git shortlog -sne --all 2>/dev/null | grep -i "$MY_EMAIL" | awk '{sum+=$1} END {print sum+0}')
TOTAL_COMMITS=$(git rev-list --all --count 2>/dev/null || echo 0)

if [ "$IS_MINE" = "yes" ]; then
    if [ "$HAS_UPSTREAM" = "yes" ] || [ "$FIRST_AUTHOR" != "$MY_EMAIL" ]; then
        ROLE="fork"
    else
        ROLE="owner"
    fi
else
    if [ "$MY_COMMITS" -gt 0 ]; then
        ROLE="contributor"
    else
        ROLE="user"
    fi
fi
```

### Infer Status from Days
```bash
if [ "$DAYS_AGO" -lt 14 ]; then
    STATUS="active"
elif [ "$DAYS_AGO" -lt 90 ]; then
    STATUS="backlog"
else
    STATUS="archived"  # suggest only, don't auto-set
fi
```

---

## Command Details

### `/projectz` (no args)

Show summary of all projects. Fast, read-only.

**Logic:**
1. If no `~/.projectz.yaml` exists:
   - Print: "No projectz config. Run `/projectz init <repo-url>` to get started."
   - Stop.

2. Read `tracker_repo` from config, then read `<tracker_repo>/projects/*/MAP.md`

3. For this computer, check `<tracker_repo>/computers/<mac-id>.md` for local paths

4. Display table:
   ```
   | Project    | Status  | Role   | Last Commit | Local |
   |------------|---------|--------|-------------|-------|
   | my-project | active  | owner  | 2 days ago  | yes   |
   | other-proj | backlog | fork   | 45 days     | yes   |
   | team-proj  | active  | contrib| 1 day ago   | no    |
   ```

5. If no projects linked to this computer:
   - Print: "No local projects found. Run `/projectz scan` to discover repos."

### `/projectz init <repo-url> [path]`

First-time setup on a new computer.

**Steps:**
1. Determine clone path:
   - If `[path]` provided, use it
   - Otherwise, derive from repo URL (e.g., `my-projects.git` → `~/my-projects`)
2. Clone repo: `git clone <repo-url> <path>`
3. Get MAC address (see Utilities)
4. Extract username from repo URL
5. Get email: `git config user.email`
6. Create `~/.projectz.yaml`:
   ```yaml
   computer_id: <mac>
   computer_name: <hostname>
   tracker_repo: <path>
   github_username: <extracted>
   git_email: <email>
   ```
7. Create `computers/<mac>.md` if not exists
8. Commit and push
9. Print: "Setup complete. Run `/projectz scan` to discover local repos."

### `/projectz scan`

Discover local repos and update all project metadata. This is the main "sync" operation.

**Steps:**

1. **Load config**: Read `~/.projectz.yaml` for `tracker_repo`, `computer_id`, `github_username`, `git_email`

2. **Pull latest**: `cd <tracker_repo> && git pull --rebase`

3. **Scan for repos**: Search common directories for git repos:
   ```bash
   find ~/Documents/workspace ~/code ~/projects ~/ -maxdepth 3 -name ".git" -type d 2>/dev/null
   ```

4. **For each repo found:**
   - Get remote URL: `git remote get-url origin`
   - Get project name from URL or folder name
   - Generate slug
   - Run role detection (see Utilities)
   - Run status inference (see Utilities)
   - Get commit counts

5. **Match to existing projects or create new:**
   - If `projects/<slug>/MAP.md` exists: update it
   - If new repo: create `projects/<slug>/README.md` and `MAP.md`

6. **Update computer file:**
   - Add/update local paths in `computers/<mac>.md`

7. **Report changes:**
   ```
   Updated: my-project (active, owner, 47/52 commits)
   Updated: other-proj (backlog, fork, 12/89 commits)
   New: new-project (active, owner, 15/15 commits)
   Skipped: third-party-lib (role=user, not tracking)
   ```

8. **Ask before status changes:**
   - If status would change (e.g., active→backlog), ask user to confirm
   - Never auto-change `done` or `review`

9. **Commit and push:**
   ```bash
   git add -A
   git commit -m "projectz: scan from <computer-name>"
   git push
   ```

### `/projectz note <project> <text>`

Add a private note about a project. Notes are stored in your tracker repo, NOT the project's own repo.

**Steps:**
1. Generate slug from first few words of text
2. Create `projects/<project>/notes/` if not exists
3. Create `<date>-<slug>.md`:
   ```markdown
   ---
   date: YYYY-MM-DD
   ---

   # <title from text>

   <text>
   ```
4. Update MAP.md "Recent Notes" section
5. Print: "Note added to <project>"

### `/projectz task <project> <title>`

Add a task to a project.

**Steps:**
1. Find next task number (scan `tasks/` directory)
2. Generate slug from title
3. Create `tasks/<num>-<slug>.md`:
   ```markdown
   ---
   id: "<num>"
   title: <title>
   status: active
   created: YYYY-MM-DD
   ---

   # <title>
   ```
4. Print: "Task <num> added to <project>"

### `/projectz done <project> <task-id>`

Mark a task as done.

**Steps:**
1. Find task file matching ID (e.g., `001-*.md`)
2. Update frontmatter: `status: done`, add `completed: YYYY-MM-DD`
3. Print: "Task <id> marked done"

### `/projectz sync`

Commit and push any pending changes.

**Steps:**
1. Read `tracker_repo` from `~/.projectz.yaml`
2. `cd <tracker_repo>`
3. `git add -A`
4. `git diff --cached --quiet || git commit -m "projectz: sync"`
5. `git pull --rebase`
6. `git push`
7. Print: "Synced"

---

## How to Reset / Start Over

If you need to reinitialize on this computer:

1. Check your current tracker path:
   ```bash
   grep tracker_repo ~/.projectz.yaml
   ```

2. Delete local config:
   ```bash
   rm ~/.projectz.yaml
   ```

3. (Optional) Remove local clone if switching to a different repo:
   ```bash
   rm -rf <tracker_repo_path>
   ```

4. Re-initialize:
   ```
   /projectz init <repo-url>
   ```

This only affects this computer. Your tracker repo and other computers are unchanged.

---

## Important Notes

- **Notes are private** - Stored in tracker repo, not in project repos. Use for internal thoughts, research, decisions.
- **Tracker repo can be named anything** - `my-projects`, `tracker`, `work-log` - the path is stored in `~/.projectz.yaml`
- **Git for sync** - Just `git pull`/`push`. No special sync logic.
- **Human-readable** - All files are markdown, viewable on GitHub.
- **Multi-computer** - Same tracker repo, different computers register themselves.
- **Role detection** - Automatically determines your relationship to each project.
- **Status inference** - Suggests status based on commit activity, but asks before changing.
