# AGENTS.md - Instructions for AI Agents

This repository is a **projectz** tracker - a Markdown-based personal project management system.

## Quick Reference

- **Projects** live in `projects/<slug>/`
- **README.md** = project description (what it is)
- **MAP.md** = project hub (status, links to tasks/notes/docs)
- **Tasks** are in `projects/<slug>/tasks/<id>-<name>.md`
- **Computer configs** are in `computers/<mac-id>.md`
- **All files use YAML frontmatter** for structured data

## File Purposes

| File | Purpose |
|------|---------|
| `README.md` | What the project is (description only) |
| `MAP.md` | Central hub: status, links to all project docs |
| `tasks/` | Individual task files |
| `notes/` | Date-prefixed notes (linked from MAP.md) |
| `docs/` | Documentation (linked from MAP.md) |
| `howto/` | How-to guides (linked from MAP.md) |

## Computer Identity

Computer ID is derived from MAC address:
- Get primary MAC: `ifconfig en0 | grep ether | awk '{print $2}' | tr -d ':'`
- Store in `~/.projectz.yaml` as `computer_id`
- Register in `computers/<mac-id>.md` with all local MACs
- Identity verified by matching at least one MAC

## Working with Projects

### Reading project status
1. Check `INDEX.md` for overview of all projects
2. Read `projects/<slug>/MAP.md` for project status and links
3. Follow links to tasks/, notes/, docs/ as needed

### Creating a project
1. Create `projects/<slug>/README.md` with description
2. Create `projects/<slug>/MAP.md` with frontmatter:
   ```yaml
   ---
   slug: project-name
   status: draft
   tags: []
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   ---
   ```
3. Create `projects/<slug>/tasks/` directory
4. Update `INDEX.md`

### Adding a task
1. Find next task number (scan existing files in tasks/)
2. Create `projects/<slug>/tasks/<NNN>-<task-slug>.md`

### Adding a note
1. Create `projects/<slug>/notes/<date>-<slug>.md`
2. Add link to MAP.md under "Recent Notes"

## Status Values

- **Projects**: `draft`, `active`, `review`, `done`, `archived`
- **Tasks**: `draft`, `active`, `blocked`, `done`
- **Priority**: `low`, `medium`, `high`, `critical`

## Syncing

Always use Git:
```bash
git add -A
git commit -m "projectz: description"
git pull --rebase
git push
```
