# AGENTS.md - Instructions for AI Agents

This repository is a **projectz** tracker - a Markdown-based personal project management and knowledge base system.

## Quick Reference

- **Projects** live in `projects/<slug>/`
- **README.md** = Rich project description (what it is, problem, solution, tech stack)
- **MAP.md** = Project hub (status, role, metadata, links)
- **docs/** = Internal documentation (NOT in project's own repo)
- **Tasks** in `projects/<slug>/tasks/<id>-<name>.md`
- **Notes** in `projects/<slug>/notes/<date>-<slug>.md` (private, not in project repo)
- **Computer configs** in `computers/<mac-id>.md`
- **Helper scripts** in `scripts/`
- **All files use YAML frontmatter**

## File Purposes

| File | Purpose |
|------|---------|
| `README.md` | Rich description: problem, solution, tech stack, current state |
| `MAP.md` | Central hub: status, role, links |
| `docs/` | Internal documentation (private, not in project repo) |
| `tasks/` | Individual task files |
| `notes/` | Private notes (stored here, not in project repo) |

## Why Rich READMEs Matter

When you (or another agent) come back to a project on a different computer, you need context:
- What does this project do?
- What problem does it solve?
- What's the tech stack?
- What's the current state?
- How do I run it?

**Always write detailed project READMEs with these sections:**
- Problem
- Solution
- Tech Stack
- Current State
- Getting Started
- Key Files

## Internal Documentation

The `docs/` folder is for documentation that should NOT go in the project's own repo:
- Private research and decisions
- Notes about third-party projects you use
- Credentials setup (without actual secrets)
- Personal workflow notes

## Helper Scripts

Use scripts in `scripts/` for reliable operations:
- `get-computer-id.sh` - Get MAC address
- `scan-repos.sh` - Scan for git repos
- `analyze-repo.sh` - Analyze single repo

## Computer Identity

Computer ID is derived from MAC address:
- Use: `./scripts/get-computer-id.sh`
- Or macOS: `ifconfig en0 | grep ether | awk '{print $2}' | tr -d ':'`
- Store in `~/.projectz.yaml` as `computer_id`
- Register in `computers/<mac-id>.md`

## Statuses

- `draft` - Just created
- `active` - Currently working on (commit < 14 days)
- `backlog` - Paused, will resume (14-90 days)
- `review` - In review/testing (manual)
- `done` - Completed (manual)
- `archived` - No longer maintained (> 90 days)

## Roles

- `owner` - You created it
- `fork` - You forked someone else's repo
- `contributor` - You contribute to others' repo
- `user` - Just cloned to use it

## Syncing

Always use Git:
```bash
git add -A
git commit -m "projectz: description"
git pull --rebase
git push
```
