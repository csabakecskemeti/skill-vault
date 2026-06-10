---
name: projectz
description: Git-based markdown project tracker for managing personal projects across multiple computers. Use when tracking projects, managing tasks, checking project status, adding tasks, syncing work across machines, or when user mentions "my projects", "project tracker", or "projectz".
license: MIT
compatibility: Requires git and a GitHub account for syncing
metadata:
  author: csabakecskemeti
  version: "0.4.0"
---

# /projectz - Git-based Project Tracker

Manage personal projects across multiple computers using Git and Markdown.

## Commands

| Command | Description |
|---------|-------------|
| `/projectz` | Show status of all projects |
| `/projectz init <repo-url>` | Clone projectz repo and register this computer |
| `/projectz new <name>` | Create a new project |
| `/projectz show <project>` | Show project details |
| `/projectz task <project> <title>` | Add a task to a project |
| `/projectz done <project> <task-id>` | Mark a task as done |
| `/projectz note <project> <text>` | Add a note to a project |
| `/projectz status <project> <status>` | Update project status |
| `/projectz link <project> <local-path>` | Link project to local checkout on this computer |
| `/projectz sync` | Pull latest, commit changes, push |
| `/projectz discover [path]` | Scan for local git repos, create/update projects |
| `/projectz scan` | Re-scan all projects and auto-infer status from activity |

## Project Statuses

| Status | Description | Auto-infer criteria |
|--------|-------------|---------------------|
| `draft` | Just created, not started | No commits yet or only initial commit |
| `active` | Currently being worked on | Commits within last 14 days |
| `backlog` | Paused, will resume later | No commits in 14-90 days |
| `review` | In review/testing phase | Manually set |
| `done` | Completed | Manually set |
| `archived` | No longer maintained | No commits in 90+ days, or manually set |

### Status Inference Rules

When running `/projectz scan` or `/projectz discover`, auto-infer status:

```
if last_commit < 14 days ago:
    status = "active"
elif last_commit < 90 days ago:
    status = "backlog"
else:
    status = "archived" (suggest, don't auto-set)
```

Never auto-change `done` or `review` - those are manually set.
Always report inferred changes and let user confirm before updating.

## Project Roles

Track your relationship with each project:

| Role | Description | Detection |
|------|-------------|-----------|
| `owner` | You created it, it's yours | Remote URL has your username + first commits are yours |
| `fork` | You forked someone else's repo | Your username in URL + has `upstream` remote or first commits aren't yours |
| `contributor` | You contribute to others' repo | Not your URL + you have commits in the repo |
| `user` | Just cloned to use it | Not your URL + no commits from you |

### Role Detection Logic

```bash
# Get configured git username/email
MY_EMAIL=$(git config user.email)
MY_USERNAME=$(cat ~/.projectz.yaml | grep github_username | cut -d: -f2 | tr -d ' ')

# Check if remote URL contains your username
ORIGIN=$(git remote get-url origin 2>/dev/null)
IS_MINE=$(echo "$ORIGIN" | grep -qi "$MY_USERNAME" && echo "yes" || echo "no")

# Check for upstream remote (indicates fork)
HAS_UPSTREAM=$(git remote | grep -q upstream && echo "yes" || echo "no")

# Get first commit author
FIRST_AUTHOR=$(git log --reverse --format="%ae" 2>/dev/null | head -1)

# Count commits by me vs total
MY_COMMITS=$(git shortlog -sne --all | grep -i "$MY_EMAIL" | awk '{sum+=$1} END {print sum+0}')
TOTAL_COMMITS=$(git rev-list --all --count 2>/dev/null || echo 0)

# Determine role
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

### Role-based Filtering

When showing projects, can filter by role:
- `/projectz` - show all
- `/projectz --mine` - show only `owner` + `fork`
- `/projectz --contributing` - show `contributor`
- `/projectz --using` - show `user`

---

## Configuration

### Local Config (`~/.projectz.yaml`)

```yaml
computer_id: a1b2c3d4e5f6    # MAC address (no colons)
computer_name: macbook-pro    # Friendly name
projectz_repo: ~/projectz     # Local clone path
github_username: csabakecskemeti  # For role detection
git_email: user@example.com       # For commit attribution detection
```

### Getting Computer ID (MAC Address)

The computer ID must be derived from a network interface MAC address for uniqueness:

**macOS:**
```bash
ifconfig en0 | grep ether | awk '{print $2}' | tr -d ':'
```

**Linux:**
```bash
cat /sys/class/net/eth0/address | tr -d ':'
```

**Windows (PowerShell):**
```powershell
(Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -First 1).MacAddress -replace '-',''
```

Store the result (lowercase, no separators) as `computer_id`. The same MAC must appear in the computer's registration file for identity verification.

---

## Repository Structure

```
projectz/
├── README.md              # Repo overview
├── AGENTS.md              # Instructions for AI agents
├── INDEX.md               # Auto-maintained project index
├── computers/             # Registered computers
│   └── <computer-id>.md   # Computer info + MAC addresses + local paths
└── projects/
    └── <project-slug>/
        ├── README.md      # Project description (what it is)
        ├── MAP.md         # Project hub: status, links to docs
        └── tasks/
            └── 001-<slug>.md
```

---

## File Formats

### MAP.md Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `slug` | yes | URL-friendly project identifier |
| `status` | yes | draft, active, backlog, review, done, archived |
| `role` | no | owner, fork, contributor, user (auto-detected) |
| `has_git` | no | true/false - is project under version control |
| `repo` | no | Remote repository URL |
| `upstream` | no | Original repo URL if this is a fork |
| `tags` | no | List of tags for categorization |
| `created` | yes | Creation date (YYYY-MM-DD) |
| `updated` | yes | Last update date (YYYY-MM-DD) |
| `last_commit` | no | Date of last git commit (auto-updated by scan) |
| `last_activity` | no | Date of last file modification (auto-updated by scan) |
| `my_commits` | no | Number of commits by you (auto-updated by scan) |
| `total_commits` | no | Total commits in repo (auto-updated by scan) |

### MAP.md Sections

| Section | Purpose |
|---------|---------|
| **Repository** | Git status, remote URL, branch info |
| **Files > Temporary** | Safe to delete: builds, caches, logs |
| **Files > Private** | Don't share: .env, secrets, local configs |
| **Files > Core** | Important: source, docs, tests |
| **Quick Links** | Links to tasks/, notes/, howto/ |
| **Recent Notes** | Latest notes with links |
| **Related Documents** | Links to docs, guides, decisions |

### Project README.md (description only)

```markdown
# My Project

Brief description of what this project is.

## Overview

More details about the project goals and scope.

See [MAP.md](./MAP.md) for status, tasks, and related documents.
```

### Project MAP.md (central hub)

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

# My Project - Map

## Status

Current: **active** | Role: **owner**

## Quick Links

- [Tasks](./tasks/)
- [Notes](./notes/)
- [How-To Guides](./howto/)

## Repository

- **Git**: yes, initialized
- **Remote**: https://github.com/user/my-project
- **Default branch**: main

## Files

### Temporary (safe to delete)
- `build/`, `dist/` - build outputs
- `*.log` - log files
- `.cache/`, `__pycache__/` - caches
- `node_modules/` - dependencies (reinstallable)

### Private (don't share publicly)
- `.env`, `.env.local` - environment secrets
- `config.local.yaml` - local overrides
- `secrets/` - API keys, credentials
- `*.pem`, `*.key` - certificates/keys

### Core (important, back up)
- `src/` - source code
- `docs/` - documentation
- `tests/` - test files

## Recent Notes

- [2024-01-20 - Auth Research](./notes/2024-01-20-auth-research.md)
- [2024-01-15 - Initial Setup](./notes/2024-01-15-initial-setup.md)

## Related Documents

- [Architecture Decision](./docs/architecture.md)
- [Deployment Guide](./howto/deploy.md)
```

### Task file (tasks/001-setup.md)

```markdown
---
id: "001"
title: Set up project structure
status: active
priority: high
created: 2024-01-15
---

# Set up project structure

Create the initial directory structure and configuration files.

## Acceptance Criteria

- [ ] Directory structure created
- [ ] Config files in place
```

### Computer file (computers/<mac-id>.md)

```markdown
---
id: a1b2c3d4e5f6
name: macbook-pro
mac_addresses:
  - a1b2c3d4e5f6
  - f6e5d4c3b2a1
registered: 2024-01-15
---

# macbook-pro

## Local Project Paths

| Project | Local Path | Last Commit |
|---------|------------|-------------|
| my-project | ~/code/my-project | abc1234 |
```

---

## Command Implementations

### `/projectz init <repo-url>`
1. Clone the repo to `~/projectz` (or ask user for location)
2. Get MAC address from primary network interface
3. Extract GitHub username from repo URL (e.g., `csabakecskemeti` from `github.com/csabakecskemeti/projectz`)
4. Get git email from `git config user.email`
5. Create `~/.projectz.yaml` with:
   - `computer_id`: MAC address
   - `computer_name`: hostname
   - `projectz_repo`: local path
   - `github_username`: extracted from repo URL
   - `git_email`: from git config
6. Create `computers/<mac-id>.md` with all local MAC addresses
7. Commit and push the computer registration
8. Confirm setup complete

### `/projectz new <name>`
1. Generate slug from name (lowercase, hyphens)
2. Create `projects/<slug>/README.md` with description template
3. Create `projects/<slug>/MAP.md` with status and links
4. Create `projects/<slug>/tasks/` directory
5. Update `INDEX.md`
6. Report success

### `/projectz task <project> <title>`
1. Find next task number (scan existing task files)
2. Generate task slug from title
3. Create `projects/<project>/tasks/<num>-<slug>.md`
4. Report success with task ID

### `/projectz done <project> <task-id>`
1. Find task file matching ID (e.g., `001-*.md`)
2. Update frontmatter: `status: done`
3. Add `completed: <date>` to frontmatter
4. Report success

### `/projectz note <project> <text>`
1. Create `projects/<project>/notes/` if not exists
2. Create `<date>-<slug>.md` with the note content
3. Add link to MAP.md under "Recent Notes"
4. Report success

### `/projectz sync`
1. `git add -A`
2. `git commit -m "projectz: <summary of changes>"` (skip if nothing to commit)
3. `git pull --rebase`
4. `git push`
5. Report sync status

### `/projectz link <project> <local-path>`
1. Read computer file for current computer (match by MAC)
2. Add/update entry in "Local Project Paths" table
3. Run `git -C <local-path> rev-parse --short HEAD` to record commit
4. Report success

### `/projectz discover [path]`
1. If path provided, scan that directory for git repos
2. If no path, search common locations (`~/`, `~/code/`, `~/projects/`, `~/Documents/workspace/`)
3. For each git repo found:
   - Get remote URL from `.git/config`
   - Get last commit date: `git log -1 --format=%ci`
   - Check if project exists in projectz
   - If exists: update local path in computer file
   - If new: offer to create project entry with inferred status
4. Infer status based on last commit date (see Status Inference Rules)
5. Update computer's local paths table
6. Report findings with suggested actions

### `/projectz scan`
1. Read all projects from `projects/`
2. For each project with a local path on this computer:
   - `cd` to local path
   - Get last commit: `git log -1 --format=%ci`
   - Get last file change: `find . -type f -not -path "./.git/*" -exec stat -f "%m" {} \; | sort -rn | head -1`
   - Compare with current status
3. Generate status change suggestions:
   - "project-x: active → backlog (no commits in 45 days)"
   - "project-y: backlog → active (commit 2 days ago)"
4. Update `last_commit` and `last_activity` in MAP.md frontmatter
5. Ask user to confirm status changes before applying
6. Report summary

### Activity detection commands

**Get last commit date (cross-platform):**
```bash
git log -1 --format=%ci 2>/dev/null || echo "no commits"
```

**Get days since last commit:**
```bash
git log -1 --format=%ct | xargs -I {} bash -c 'echo $(( ($(date +%s) - {}) / 86400 )) days'
```

**Check if repo has uncommitted changes:**
```bash
git status --porcelain | head -1
```

---

## Important Notes

- **MAC for identity** - Computer ID is MAC address; at least one registered MAC must match local interfaces
- **README = description** - Keep README.md focused on what the project is
- **MAP = hub** - MAP.md links to everything: status, tasks, notes, docs
- **Progressive linking** - MAP.md links to notes/, docs/, howto/ as needed
- **Git for sync** - Don't reinvent sync, just use `git pull`/`push`
- **Human-readable** - Files should make sense when viewed on GitHub
