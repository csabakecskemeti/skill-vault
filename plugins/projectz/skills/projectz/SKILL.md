---
name: projectz
description: Git-based markdown project tracker for managing personal projects across multiple computers. Use when tracking projects, managing tasks, checking project status, adding tasks, syncing work across machines, or when user mentions "my projects", "project tracker", or "projectz".
license: MIT
compatibility: Requires git and a GitHub account for syncing
metadata:
  author: csabakecskemeti
  version: "0.2.0"
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
| `/projectz status <project> <status>` | Update project status (draft/active/review/done/archived) |
| `/projectz link <project> <local-path>` | Link project to local checkout on this computer |
| `/projectz sync` | Pull latest, commit changes, push |
| `/projectz discover` | Scan for local checkouts of known project repos |

---

## Configuration

### Local Config (`~/.projectz.yaml`)

```yaml
computer_id: a1b2c3d4e5f6    # MAC address (no colons)
computer_name: macbook-pro    # Friendly name
projectz_repo: ~/projectz     # Local clone path
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
| `status` | yes | draft, active, review, done, archived |
| `has_git` | no | true/false - is project under version control |
| `repo` | no | Remote repository URL |
| `tags` | no | List of tags for categorization |
| `created` | yes | Creation date (YYYY-MM-DD) |
| `updated` | yes | Last update date (YYYY-MM-DD) |

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
repo: https://github.com/user/my-project
has_git: true
tags: [python, web]
created: 2024-01-15
updated: 2024-01-20
---

# My Project - Map

## Status

Current: **active**

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
3. Create `~/.projectz.yaml` with computer_id (MAC), name, repo path
4. Create `computers/<mac-id>.md` with all local MAC addresses
5. Commit and push the computer registration
6. Confirm setup complete

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

### `/projectz discover`
1. Read all projects from `projects/`
2. For each with a `repo:` URL, search common locations (`~/`, `~/code/`, `~/projects/`, `~/Documents/`)
3. Match by checking if `.git/config` contains the repo URL
4. If found, update computer's local paths
5. Report findings

---

## Important Notes

- **MAC for identity** - Computer ID is MAC address; at least one registered MAC must match local interfaces
- **README = description** - Keep README.md focused on what the project is
- **MAP = hub** - MAP.md links to everything: status, tasks, notes, docs
- **Progressive linking** - MAP.md links to notes/, docs/, howto/ as needed
- **Git for sync** - Don't reinvent sync, just use `git pull`/`push`
- **Human-readable** - Files should make sense when viewed on GitHub
