---
name: projectz
description: Git-based markdown project tracker for managing personal projects across multiple computers. Use when tracking projects, managing tasks, checking project status, adding tasks, syncing work across machines, or when user mentions "my projects", "project tracker", or "projectz".
license: MIT
compatibility: Requires git and a GitHub account for syncing
metadata:
  author: csabakecskemeti
  version: "0.1.0"
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

The projectz system uses two locations:

1. **Projectz repo** - A Git repository containing all project data as Markdown files
2. **Local config** - `~/.projectz.yaml` storing computer-specific settings:

```yaml
computer_id: comp-abc123
computer_name: macbook-pro
projectz_repo: ~/projectz  # local clone path
```

## Repository Structure

```
projectz/
├── README.md              # Overview and links
├── AGENTS.md              # Instructions for AI agents
├── INDEX.md               # Auto-maintained project index
├── computers/             # Registered computers
│   └── <computer-id>.md   # Computer info and its project paths
└── projects/
    └── <project-slug>/
        ├── README.md      # Project overview, status, notes
        └── tasks/
            ├── 001-<slug>.md
            └── 002-<slug>.md
```

## File Formats

### Project README.md
```markdown
---
name: My Project
slug: my-project
status: active
repo: https://github.com/user/my-project
tags: [python, web]
created: 2024-01-15
updated: 2024-01-20
---

# My Project

Description of the project.

## Notes

- 2024-01-20: Started working on auth
- 2024-01-15: Initial setup
```

### Task file (tasks/001-setup.md)
```markdown
---
id: "001"
title: Set up project structure
status: active
priority: high
created: 2024-01-15
updated: 2024-01-15
---

# Set up project structure

Create the initial directory structure and configuration files.

## Acceptance Criteria

- [ ] Directory structure created
- [ ] Config files in place
```

### Computer file (computers/comp-abc123.md)
```markdown
---
id: comp-abc123
name: macbook-pro
registered: 2024-01-15
---

# macbook-pro

## Local Project Paths

| Project | Local Path | Last Synced |
|---------|------------|-------------|
| my-project | ~/code/my-project | 2024-01-20 |
```

## Command Implementations

### `/projectz` (no args) - Show Status
1. Read `~/.projectz.yaml` to find repo location
2. Read `INDEX.md` or scan `projects/` directory
3. Display summary: project names, statuses, active task counts

### `/projectz init <repo-url>`
1. Clone the repo to `~/projectz` (or ask user for location)
2. Generate computer ID from hostname hash
3. Create `~/.projectz.yaml` with config
4. Create `computers/<computer-id>.md` if not exists
5. Commit and push the computer registration
6. Confirm setup complete

### `/projectz new <name>`
1. Generate slug from name (lowercase, hyphens)
2. Create `projects/<slug>/README.md` with template
3. Create `projects/<slug>/tasks/` directory
4. Update `INDEX.md`
5. Report success (don't auto-commit, let user review or use sync)

### `/projectz task <project> <title>`
1. Find next task number (scan existing task files)
2. Generate task slug from title
3. Create `projects/<project>/tasks/<num>-<slug>.md`
4. Report success with task ID

### `/projectz done <project> <task-id>`
1. Find task file matching ID (e.g., `001-*.md`)
2. Update frontmatter: `status: done`
3. Add completion timestamp
4. Report success

### `/projectz sync`
1. `git add -A`
2. `git commit -m "projectz sync: <timestamp>"` (skip if nothing to commit)
3. `git pull --rebase`
4. `git push`
5. Report sync status

### `/projectz link <project> <local-path>`
1. Read computer file for current computer
2. Add/update entry in "Local Project Paths" table
3. Optionally run `git -C <local-path> rev-parse HEAD` to record commit

### `/projectz discover`
1. Read all projects from `projects/`
2. For each with a `repo:` URL, search common locations (`~/`, `~/code/`, `~/projects/`, etc.)
3. If found, update computer's local paths
4. Report findings

## Important Notes

- **Always use git for sync** - don't reinvent sync, just use `git pull`/`push`
- **Human-readable first** - files should make sense when viewed on GitHub
- **Minimal structure** - don't over-engineer, add complexity only when needed
- **Idempotent operations** - running a command twice shouldn't break things
- **Report clearly** - tell the user what was done and what files were changed
