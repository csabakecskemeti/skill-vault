---
name: projectz
description: Git-based project tracker and knowledge base. Use when user mentions "my projects", "project tracker", "projectz", or wants to track projects, add notes, manage tasks, brainstorm ideas, track goals, or sync work across machines.
license: MIT
compatibility: Requires git and GitHub account
metadata:
  author: csabakecskemeti
  version: "0.9.0"
---

# /projectz - Git-based Project Tracker

A centralized knowledge base for tracking personal projects across multiple computers using Git and Markdown.

**Key features:**
- Track project status (active, backlog, done, etc.)
- Detect your role (owner, fork, contributor, user)
- Store private notes and internal docs (not in project repos)
- Rich project descriptions for context when switching machines/agents
- **Dependencies** - Track hard (code) and soft (workflow) dependencies between projects
- **Goals** - Define high-level goals and link projects to them
- **Ideation** - Brainstorm and develop ideas before committing to projects
- Cross-platform helper scripts for reliable scanning
- Bidirectional sync via Git

---

## Commands

### Core Commands

| Command | Description |
|---------|-------------|
| `/projectz` | Show summary of all projects (fast, read-only) |
| `/projectz init <repo-url> [path]` | First-time setup: clone repo, register this computer, install skill |
| `/projectz scan` | Discover local repos, update status/role for all projects |
| `/projectz sync` | Bidirectional sync: pull remote changes, push local changes |
| `/projectz tree [projects\|goals]` | Show hierarchy tree (default: both) |

### Project Management

| Command | Description |
|---------|-------------|
| `/projectz note <project> <text>` | Add a private note about a project |
| `/projectz doc <project> <title>` | Create/edit internal documentation for a project |
| `/projectz task <project> <title>` | Add a task to a project |
| `/projectz done <project> <task-id>` | Mark a task as done |

### Dependencies

| Command | Description |
|---------|-------------|
| `/projectz depends <project> <dependency> [hard\|soft] <reason>` | Add a dependency |
| `/projectz deps <project>` | Show dependencies for a project |
| `/projectz blocked` | Show projects blocked by unfinished dependencies |
| `/projectz depgraph` | Show visual dependency graph |

### Goals

| Command | Description |
|---------|-------------|
| `/projectz goal <name>` | Create or view a goal |
| `/projectz goals` | List all goals with progress |
| `/projectz link <project> <goal> <contribution>` | Link a project to a goal |
| `/projectz unlink <project> <goal>` | Remove project-goal link |

### Ideation

| Command | Description |
|---------|-------------|
| `/projectz ideate [name]` | Start brainstorming a new idea (interactive if no name) |
| `/projectz ideas` | List all ideas by status |
| `/projectz idea <slug>` | View or continue developing an idea |
| `/projectz convert <idea-slug>` | Convert a ready idea into a project |

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
| `blocked` | Waiting on dependency | Has unmet hard dependency |

### Roles

| Role | Description | Detection |
|------|-------------|-----------|
| `owner` | You created it | Your username in remote URL + your first commit |
| `fork` | You forked it | Your username in URL + has `upstream` remote OR first commit not yours |
| `contributor` | You contribute | Not your URL + you have commits |
| `user` | Just using it | Not your URL + no commits from you |

### Dependency Types

| Type | Description | Example |
|------|-------------|---------|
| `hard` | Code/technical dependency | Project X imports a library from Project Y |
| `soft` | Workflow/capacity dependency | Need to finish framework before scaling up |

### Idea Statuses

| Status | Description |
|--------|-------------|
| `brainstorming` | Initial exploration, collecting thoughts |
| `researching` | Actively investigating feasibility |
| `ready` | Validated and ready to become a project |
| `rejected` | Decided not to pursue |
| `converted` | Turned into a project |

### Goal Statuses

| Status | Description |
|--------|-------------|
| `active` | Currently pursuing |
| `achieved` | Goal completed |
| `paused` | Temporarily on hold |
| `abandoned` | No longer pursuing |

### Hierarchy

Both projects and goals support parent-child relationships with **multiple parents**:

- **Project hierarchy**: A project can have multiple `parents` (e.g., a shared library used by several projects)
- **Goal hierarchy**: A goal can serve multiple parent goals (e.g., `local-llm-self-sufficiency` supports both `ai-powered-income` AND `unified-multi-machine-workflow`)

Use `parents` as a list in frontmatter. This creates a DAG (directed acyclic graph), not a strict tree.

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
├── goals/                   # High-level objectives
│   └── <goal-slug>.md
├── ideas/                   # Ideas being developed
│   └── <idea-slug>.md
└── projects/
    └── <slug>/
        ├── README.md        # Rich project description
        ├── MAP.md           # Status, role, metadata, dependencies, goals
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
parents: []  # optional: list of parent project slugs (for subprojects)

# Dependencies
dependencies:
  hard:
    - project: shared-lib
      reason: "Uses utility functions from shared-lib"
  soft:
    - project: agent-framework
      reason: "Need this to automate testing"

# Goals this project contributes to
goals:
  - goal: build-ai-platform
    contribution: "Provides the API layer for AI services"
  - goal: learn-rust
    contribution: "Performance-critical modules written in Rust"
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

## Dependencies

### Hard (Code)
- **shared-lib**: Uses utility functions from shared-lib

### Soft (Workflow)
- **agent-framework**: Need this to automate testing

## Goals

- **build-ai-platform**: Provides the API layer for AI services
- **learn-rust**: Performance-critical modules written in Rust

## Recent Notes

- [2024-01-20 - Auth research](./notes/2024-01-20-auth-research.md)

## Internal Docs

- [Architecture](./docs/architecture.md)
- [Deployment Guide](./docs/deployment.md)
```

### Goal File: `goals/<goal-slug>.md`

```markdown
---
slug: build-ai-platform
status: active
priority: high
created: 2024-01-15
target_date: 2024-12-31
parents: []  # optional: list of parent goal slugs (can serve multiple goals)
---

# Build AI Platform

## Description

Create a comprehensive AI platform that can run multiple models, handle inference requests, and provide a unified API.

## Why It Matters

- Consolidate AI experiments into production-ready infrastructure
- Enable rapid prototyping of new AI applications
- Reduce dependency on external AI services

## Success Criteria

- [ ] Unified API for multiple model backends
- [ ] Auto-scaling based on load
- [ ] Cost tracking per model/request
- [ ] Self-hosted on own hardware

## Contributing Projects

| Project | Status | Contribution |
|---------|--------|--------------|
| llmaas | active | Core inference server |
| agent-hub | active | Inter-agent communication |
| quasar-deck | active | Monitoring dashboard |

## Progress Notes

- 2024-01-15: Started with llmaas as foundation
- 2024-01-20: Added agent-hub for multi-agent coordination
```

### Idea File: `ideas/<idea-slug>.md`

```markdown
---
slug: voice-controlled-home-automation
status: brainstorming
created: 2024-01-15
updated: 2024-01-20
tags: [iot, voice, automation]
converted_to:  # filled when converted to project
---

# Voice-Controlled Home Automation

## The Idea

A fully local (no cloud) voice assistant that controls home automation without sending any data to external services.

## Problem It Solves

- Privacy concerns with Alexa/Google Home
- Latency with cloud-based voice processing
- Dependency on internet connectivity
- Limited customization of commercial solutions

## Brainstorm Notes

- Could use Whisper for local speech-to-text
- Home Assistant for device control
- Need to research wake word detection (Porcupine? OpenWakeWord?)
- Hardware: Raspberry Pi with ReSpeaker mic array?

## Research

- [Whisper local deployment](https://...)
- [Home Assistant REST API](https://...)
- [OpenWakeWord project](https://...)

## Viability Assessment

### Pros
- Full privacy
- No subscription costs
- Highly customizable

### Cons
- Significant setup effort
- May need dedicated hardware
- Voice recognition quality vs cloud

### Effort Estimate
- Initial prototype: 2-3 weekends
- Production-ready: 1-2 months part-time

## Decision

**Status: researching**

Next steps:
1. Test Whisper latency on Raspberry Pi
2. Evaluate wake word detection options
3. Prototype with simple commands
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
blocked_by:  # optional: task ID or project slug
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
   | Project    | Status  | Role   | Last Commit | Local | Blocked |
   |------------|---------|--------|-------------|-------|---------|
   | my-project | active  | owner  | 2 days ago  | yes   |         |
   | other-proj | blocked | owner  | 5 days      | yes   | shared-lib |
   | team-proj  | active  | contrib| 1 day ago   | no    |         |
   ```

5. Show goal progress summary if goals exist:
   ```
   Goals: build-ai-platform (3/5 projects active) | learn-rust (1/2 done)
   ```

6. If no projects linked to this computer:
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
9. Create `goals/` and `ideas/` directories if not present
10. **Install skill for simple `/projectz` command:**
    ```bash
    mkdir -p ~/.claude/skills/projectz
    # Copy this SKILL.md to ~/.claude/skills/projectz/SKILL.md
    ```
11. Commit and push
12. Print: "Setup complete. Run `/projectz scan` to discover local repos."
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

8. **Check dependencies:**
   - For each project with hard dependencies, check if dependency is `done`
   - If not, mark project as `blocked` (or warn)

9. **Report changes:**
   ```
   Updated: my-project (active, owner, 47/52 commits)
   Updated: other-proj (backlog, fork, 12/89 commits)
   New: new-project (active, owner, 15/15 commits)
   Blocked: api-service (waiting on: shared-lib)
   Skipped: third-party-lib (role=user, not tracking)
   ```

10. **Ask before status changes:**
    - If status would change (e.g., active→backlog), ask user to confirm
    - Never auto-change `done` or `review`

11. **Commit and push:**
    ```bash
    git add -A
    git commit -m "projectz: scan from <computer-name>"
    git push
    ```

### `/projectz sync`

Bidirectional sync: pull remote changes, then push local changes.

**Steps:**
1. Read `tracker_repo` from `~/.projectz.yaml`
2. `cd <tracker_repo>`
3. **Pull first** (get updates from other computers):
   ```bash
   git fetch origin
   git pull --rebase
   ```
4. **Report incoming changes:**
   - Show which files were updated
   - Highlight new projects, updated tasks, new notes from other computers
5. **Push local changes:**
   ```bash
   git add -A
   git diff --cached --quiet || git commit -m "projectz: sync from <computer-name>"
   git push
   ```
6. **Report outgoing changes:**
   - Show what was pushed
7. Print: "Synced. Pulled X changes, pushed Y changes."

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

---

## Dependency Commands

### `/projectz depends <project> <dependency> [hard|soft] <reason>`

Add a dependency between projects.

**Steps:**
1. Validate both projects exist
2. Default to `soft` if type not specified
3. Update `<project>/MAP.md` frontmatter:
   ```yaml
   dependencies:
     hard:
       - project: <dependency>
         reason: "<reason>"
   ```
4. Update the Dependencies section in MAP.md body
5. If hard dependency and `<dependency>` is not `done`, set project status to `blocked`
6. Print: "Added <type> dependency: <project> → <dependency>"

### `/projectz deps <project>`

Show dependencies for a project.

**Output:**
```
Dependencies for my-project:

HARD (code dependencies):
  → shared-lib (status: active) - Uses utility functions
  → auth-service (status: done) ✓ - Authentication module

SOFT (workflow dependencies):
  → agent-framework (status: backlog) - Need this to automate testing

Depended on by:
  ← api-gateway (hard) - Imports API client
  ← frontend (soft) - Shares types
```

### `/projectz blocked`

Show all projects blocked by unfinished dependencies.

**Output:**
```
Blocked Projects:

my-project
  Waiting on: shared-lib (active, 60% done)
  Reason: Uses utility functions from shared-lib

api-gateway
  Waiting on: my-project (blocked)
  Reason: Imports API client
  Note: Cascading block - my-project is also blocked

Soft blocks (not critical):
  frontend → design-system (backlog) - Waiting for component library
```

### `/projectz depgraph`

Show visual dependency graph.

**Output:**
```
Dependency Graph:

  auth-service [done] ✓
       │
       ▼
  shared-lib [active]
       │
       ├──────────────┐
       ▼              ▼
  my-project      data-pipeline
  [blocked]         [active]
       │
       ▼
  api-gateway [blocked]

Legend: [done]✓  [active]  [blocked]⚠  [backlog]○
```

---

## Goal Commands

### `/projectz goal <name>`

Create or view a goal.

**If goal exists:** Display goal details with contributing projects and progress.

**If new goal:**
1. Generate slug from name
2. Create `goals/<slug>.md`:
   ```markdown
   ---
   slug: <slug>
   status: active
   priority: medium
   created: YYYY-MM-DD
   target_date:
   ---

   # <name>

   ## Description

   [What does achieving this goal mean?]

   ## Why It Matters

   [Motivation and impact]

   ## Success Criteria

   - [ ] Criterion 1
   - [ ] Criterion 2

   ## Contributing Projects

   | Project | Status | Contribution |
   |---------|--------|--------------|
   ```
3. Open for editing
4. Print: "Goal created: <name>"

### `/projectz goals`

List all goals with progress.

**Output:**
```
Goals:

HIGH PRIORITY:
  build-ai-platform [active]
    Progress: 3/5 projects active, 1 done
    Target: 2024-12-31 (6 months remaining)
    Next: Complete llmaas inference endpoints

  financial-independence [active]
    Progress: 2/4 projects active
    No target date

MEDIUM PRIORITY:
  learn-rust [active]
    Progress: 1/2 projects done

ACHIEVED:
  ✓ setup-home-lab (completed 2024-01-15)
```

### `/projectz link <project> <goal> <contribution>`

Link a project to a goal with explanation of how it contributes.

**Steps:**
1. Validate project and goal exist
2. Update project's MAP.md:
   ```yaml
   goals:
     - goal: <goal>
       contribution: "<contribution>"
   ```
3. Update goal file's "Contributing Projects" table
4. Print: "Linked <project> to goal <goal>"

### `/projectz unlink <project> <goal>`

Remove a project-goal link.

---

## Ideation Commands

### `/projectz ideate [name]`

Start brainstorming a new idea.

**Interactive mode (no name):**
1. Ask: "What's the idea about? (one sentence)"
2. Ask: "What problem does it solve?"
3. Generate slug from response
4. Create idea file with responses
5. Ask: "Want to add more details now?"

**Direct mode (with name):**
1. Generate slug from name
2. Create `ideas/<slug>.md`:
   ```markdown
   ---
   slug: <slug>
   status: brainstorming
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   tags: []
   converted_to:
   ---

   # <name>

   ## The Idea

   [Core concept]

   ## Problem It Solves

   [Why this matters]

   ## Brainstorm Notes

   -

   ## Research

   -

   ## Viability Assessment

   ### Pros
   -

   ### Cons
   -

   ### Effort Estimate

   [Time/resources needed]

   ## Decision

   **Status: brainstorming**

   Next steps:
   1.
   ```
3. Open for editing
4. Print: "Idea created: <name>. Use `/projectz idea <slug>` to continue developing it."

### `/projectz ideas`

List all ideas by status.

**Output:**
```
Ideas:

READY TO CONVERT:
  voice-home-automation - Voice-controlled home automation
    Last updated: 2024-01-20
    Tags: iot, voice

RESEARCHING:
  distributed-backup - P2P backup system
    Last updated: 2024-01-18

BRAINSTORMING:
  ai-art-generator - Generate art from descriptions
    Created: 2024-01-15

REJECTED:
  crypto-trading-bot - Automated trading (rejected: too risky)

To convert a ready idea: /projectz convert <slug>
```

### `/projectz idea <slug>`

View or continue developing an idea.

**Output:** Display full idea content, then ask:
- "Add a brainstorm note?"
- "Add research link?"
- "Update status?"
- "Ready to convert to project?"

### `/projectz convert <idea-slug>`

Convert a ready idea into a full project.

**Steps:**
1. Read idea file
2. Ask for confirmation: "Convert '<name>' to a project?"
3. Create project directory and files:
   - `README.md` - populated from idea content
   - `MAP.md` - status: draft, populated from idea
4. Update idea file:
   ```yaml
   status: converted
   converted_to: <project-slug>
   ```
5. Optionally link to goals if idea mentioned them
6. Print: "Converted idea to project: <project-slug>"

---

## Hierarchy Commands

### `/projectz tree [projects|goals]`

Show hierarchy tree for projects, goals, or both.

**Output (default - both):**
```
Project Hierarchy:

quasar-deck [active]
├── spark-monitor-gui [active]
└── dgx-dashboard [backlog]

agent-hub [active]
└── agent-hub-web [draft]

(standalone projects not shown - use /projectz for full list)

Goal Hierarchy:

build-ai-platform [active] ★ HIGH
├── build-llm-infrastructure [active]
│   └── optimize-inference [backlog]
└── create-agent-framework [active]

financial-independence [active]
└── passive-income-streams [active]

(standalone goals not shown - use /projectz goals for full list)
```

### Setting Parent Relationships

**For projects:** Edit the project's MAP.md frontmatter:
```yaml
parents:
  - quasar-deck      # this project is a child of quasar-deck
  - monitoring-suite # and also part of the monitoring suite
```

**For goals:** Edit the goal file frontmatter:
```yaml
parents:
  - ai-powered-income              # serves the income goal
  - unified-multi-machine-workflow # AND the multi-machine goal
```

Or use natural language:
- "Make spark-monitor-gui a subproject of quasar-deck"
- "Add local-llm-self-sufficiency as a sub-goal of both ai-powered-income and unified-multi-machine-workflow"

The agent will update the appropriate frontmatter. Multiple parents create a DAG structure - one item can serve multiple purposes.

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
- **Dependencies track blockers** - Hard dependencies can block projects; soft dependencies are informational.
- **Goals provide direction** - Link projects to higher-level goals to see the bigger picture.
- **Ideate before committing** - Use ideas to brainstorm without creating full project overhead.
- **Helper scripts** - Use the scripts in `scripts/` for reliable cross-platform scanning.
- **Tracker repo can be named anything** - `my-projects`, `tracker`, `work-log` - the path is stored in `~/.projectz.yaml`
- **Simple /projectz command** - After init, the skill is copied to `~/.claude/skills/projectz/` so you can use `/projectz` directly without namespace.
- **Git for sync** - Bidirectional: pull to get updates, push to share changes.
- **Human-readable** - All files are markdown, viewable on GitHub.
- **Multi-computer** - Same tracker repo, different computers register themselves.
