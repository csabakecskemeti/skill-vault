---
name: projectz
description: Git-based project tracker and knowledge base. Use when user mentions "my projects", "project tracker", "projectz", or wants to track projects, add notes, manage tasks, or sync work across machines.
license: MIT
compatibility: Requires git and GitHub account
metadata:
  author: csabakecskemeti
  version: "0.7.0"
---

# /projectz - Git-based Project Tracker

A centralized knowledge base for tracking personal projects across multiple computers using Git and Markdown.

**Key features:**
- Track project status (active, backlog, done, etc.)
- Detect your role (owner, fork, contributor, user)
- Store private notes and internal docs (not in project repos)
- Rich project descriptions for context when switching machines/agents
- Cross-platform helper scripts for reliable scanning
- Sync everything via Git

---

## Commands

| Command | Description |
|---------|-------------|
| `/projectz` | Show summary of all projects (fast, read-only) |
| `/projectz init <repo-url> [path]` | First-time setup: clone repo, register this computer, install skill |
| `/projectz scan` | Discover local repos, update status/role for all projects |
| `/projectz note <project> <text>` | Add a private note about a project |
| `/projectz doc <project> <title>` | Create/edit internal documentation for a project |
| `/projectz task <project> <title>` | Add a task to a project |
| `/projectz done <project> <task-id>` | Mark a task as done |
| `/projectz sync` | Commit and push changes to tracker repo |

---

## Definitions

### Computer ID (MAC Address)

Each computer is identified by its primary network interface MAC address (lowercase, no separators).

Use the helper script (copied to tracker repo during init):
```bash
./scripts/get-computer-id.sh
```

Or manually:

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
├── AGENTS.md                # Instructions for AI agents
├── INDEX.md                 # Auto-generated project index
├── scripts/                 # Helper scripts (copied during init)
│   ├── get-computer-id.sh
│   ├── scan-repos.sh
│   └── analyze-repo.sh
├── computers/
│   └── <mac-id>.md
└── projects/
    └── <slug>/
        ├── README.md        # Rich project description
        ├── MAP.md           # Status, role, metadata
        ├── docs/            # Internal documentation (NOT in project repo)
        │   └── <topic>.md
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

### Project README.md (Rich Description)

**This is critical for context when another agent continues your work.**

```markdown
---
slug: my-project
created: 2024-01-15
---

# My Project

Brief one-line description of what this project is.

## Problem

What problem does this project solve? Why does it exist?
- Pain point 1
- Pain point 2

## Solution

How does this project solve the problem?
- Key approach
- Main features

## Tech Stack

- **Language:** Python 3.11
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **Deployment:** Docker, AWS ECS

## Current State

What's working, what's not, what's next.

- [x] Core API endpoints
- [x] Authentication
- [ ] Rate limiting
- [ ] Admin dashboard

## Getting Started

How to run this project locally:

\`\`\`bash
git clone <repo>
cd my-project
pip install -r requirements.txt
python main.py
\`\`\`

## Key Files

- `src/main.py` - Entry point
- `src/api/` - API routes
- `src/models/` - Database models
- `docs/` - Documentation

## Related

- [Architecture decisions](./docs/architecture.md)
- [API documentation](./docs/api.md)
```

### Project MAP.md (Metadata Hub)

```markdown
---
slug: my-project
status: active
role: owner
repo: https://github.com/user/my-project
has_git: true
tags: [python, web, api]
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
- [Internal Docs](./docs/)

## Repository

- Remote: https://github.com/user/my-project
- Branch: main
- Local: ~/code/my-project

## Recent Notes

- [2024-01-20 - Auth research](./notes/2024-01-20-auth-research.md)

## Internal Docs

- [Architecture](./docs/architecture.md)
- [Deployment Guide](./docs/deployment.md)
```

### Internal Docs: `docs/<topic>.md`

For documentation that should NOT go in the project's own repo:
- Private research and decisions
- Internal notes about third-party projects
- Credentials setup (without actual secrets)
- Personal workflow notes

```markdown
---
title: Architecture Decisions
updated: 2024-01-20
---

# Architecture Decisions

## Why FastAPI over Flask?

After researching both options...

## Database Choice

PostgreSQL because...

## Deployment Strategy

Using ECS because...
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

## Helper Scripts

The following scripts are copied to your tracker repo during `/projectz init`. They provide reliable cross-platform scanning.

### `scripts/get-computer-id.sh`

Get the computer's MAC address (works on macOS and Linux):
```bash
./scripts/get-computer-id.sh
# Output: a1b2c3d4e5f6
```

### `scripts/scan-repos.sh`

Scan directories for git repos and output JSON:
```bash
./scripts/scan-repos.sh ~/Documents/workspace ~/code
# Output: one JSON object per line with repo info
```

### `scripts/analyze-repo.sh`

Analyze a single repo in detail:
```bash
./scripts/analyze-repo.sh /path/to/repo
# Output: JSON with full analysis
```

For Windows, use the `.ps1` PowerShell equivalents.

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
3. Get MAC address using helper script or manual method
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
7. Copy helper scripts to `<tracker_repo>/scripts/` if not present
8. Create `computers/<mac>.md` if not exists
9. **Install skill for simple `/projectz` command:**
   ```bash
   mkdir -p ~/.claude/skills/projectz
   # Copy this SKILL.md to ~/.claude/skills/projectz/SKILL.md
   ```
10. Commit and push
11. Print: "Setup complete. Run `/projectz scan` to discover local repos."
    Print: "Skill installed at ~/.claude/skills/projectz/ - use `/projectz` directly."

### `/projectz scan`

Discover local repos and update all project metadata. Use helper scripts for reliable scanning.

**Steps:**

1. **Load config**: Read `~/.projectz.yaml` for `tracker_repo`, `computer_id`, `github_username`, `git_email`

2. **Pull latest**: `cd <tracker_repo> && git pull --rebase`

3. **Scan for repos** using helper script:
   ```bash
   ./scripts/scan-repos.sh ~/Documents/workspace ~/code ~/projects
   ```
   Or manually search common directories for git repos.

4. **For each repo found:**
   - Parse JSON output from scan script
   - Or manually: get remote URL, detect role, infer status, count commits

5. **Match to existing projects or create new:**
   - If `projects/<slug>/MAP.md` exists: update it
   - If new repo: create `projects/<slug>/README.md` with rich template and `MAP.md`

6. **For new projects, generate rich README:**
   - Extract description from project's own README if exists
   - Detect tech stack from package.json, requirements.txt, etc.
   - Include "Problem", "Solution", "Tech Stack", "Current State" sections
   - Mark sections as TODO if info not available

7. **Update computer file:**
   - Add/update local paths in `computers/<mac>.md`

8. **Report changes:**
   ```
   Updated: my-project (active, owner, 47/52 commits)
   Updated: other-proj (backlog, fork, 12/89 commits)
   New: new-project (active, owner, 15/15 commits)
   Skipped: third-party-lib (role=user, not tracking)
   ```

9. **Ask before status changes:**
   - If status would change (e.g., active→backlog), ask user to confirm
   - Never auto-change `done` or `review`

10. **Commit and push:**
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

### `/projectz doc <project> <title>`

Create or edit internal documentation for a project. Docs are stored in tracker repo, NOT in the project's own repo.

**Steps:**
1. Generate slug from title
2. Create `projects/<project>/docs/` if not exists
3. If doc exists, open for editing
4. If new, create `<slug>.md`:
   ```markdown
   ---
   title: <title>
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   ---

   # <title>

   [Content here]
   ```
5. Update MAP.md "Internal Docs" section
6. Print: "Doc created/updated: <project>/docs/<slug>.md"

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

3. (Optional) Remove personal skill:
   ```bash
   rm -rf ~/.claude/skills/projectz
   ```

4. (Optional) Remove local clone if switching to a different repo:
   ```bash
   rm -rf <tracker_repo_path>
   ```

5. Re-initialize:
   ```
   /projectz init <repo-url>
   ```

This only affects this computer. Your tracker repo and other computers are unchanged.

---

## Important Notes

- **Rich READMEs are critical** - Write detailed project descriptions so another agent (or you on another machine) can continue work with full context.
- **Internal docs stay private** - The `docs/` folder in each project is for documentation that shouldn't go in the project's own repo.
- **Notes are private** - Stored in tracker repo, not in project repos. Use for internal thoughts, research, decisions.
- **Helper scripts** - Use the scripts in `scripts/` for reliable cross-platform scanning.
- **Tracker repo can be named anything** - `my-projects`, `tracker`, `work-log` - the path is stored in `~/.projectz.yaml`
- **Simple /projectz command** - After init, the skill is copied to `~/.claude/skills/projectz/` so you can use `/projectz` directly without namespace.
- **Git for sync** - Just `git pull`/`push`. No special sync logic.
- **Human-readable** - All files are markdown, viewable on GitHub.
- **Multi-computer** - Same tracker repo, different computers register themselves.
