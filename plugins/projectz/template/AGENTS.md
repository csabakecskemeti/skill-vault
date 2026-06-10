# AGENTS.md - Instructions for AI Agents

This repository is a **projectz** tracker - a Markdown-based personal project management and knowledge base system.

## Quick Reference

- **Projects** live in `projects/<slug>/`
- **README.md** = project description (what it is)
- **MAP.md** = project hub (status, role, metadata, links)
- **Tasks** in `projects/<slug>/tasks/<id>-<name>.md`
- **Notes** in `projects/<slug>/notes/<date>-<slug>.md` (private, not in project repo)
- **Computer configs** in `computers/<mac-id>.md`
- **All files use YAML frontmatter**

## File Purposes

| File | Purpose |
|------|---------|
| `README.md` | What the project is |
| `MAP.md` | Central hub: status, role, links |
| `tasks/` | Individual task files |
| `notes/` | Private notes (stored here, not in project repo) |

## Computer Identity

Computer ID is derived from MAC address:
- macOS: `ifconfig en0 | grep ether | awk '{print $2}' | tr -d ':'`
- Store in `~/.projectz.yaml` as `computer_id`
- Register in `computers/<mac-id>.md`

## Statuses

- `draft` - Just created
- `active` - Currently working on
- `backlog` - Paused, will resume
- `review` - In review/testing
- `done` - Completed
- `archived` - No longer maintained

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
