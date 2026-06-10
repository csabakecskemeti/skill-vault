# AGENTS.md - Instructions for AI Agents

This repository is a **projectz** tracker - a Markdown-based personal project management system.

## Quick Reference

- **Projects** are in `projects/<slug>/README.md`
- **Tasks** are in `projects/<slug>/tasks/<id>-<name>.md`
- **Computer configs** are in `computers/<computer-id>.md`
- **All files use YAML frontmatter** for structured data

## Working with Projects

### Reading project status
1. Check `INDEX.md` for an overview
2. Read `projects/<slug>/README.md` for details
3. Scan `projects/<slug>/tasks/` for tasks

### Creating a project
1. Create `projects/<slug>/README.md` with frontmatter:
   ```yaml
   ---
   name: Project Name
   slug: project-name
   status: draft
   tags: []
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   ---
   ```
2. Create `projects/<slug>/tasks/` directory
3. Update `INDEX.md`

### Adding a task
1. Find next task number (scan existing files)
2. Create `projects/<slug>/tasks/<NNN>-<task-slug>.md`:
   ```yaml
   ---
   id: "NNN"
   title: Task Title
   status: active
   priority: medium
   created: YYYY-MM-DD
   ---
   ```

### Completing a task
1. Update frontmatter: `status: done`
2. Add `completed: YYYY-MM-DD`

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

## Computer Tracking

Each computer has a file in `computers/` tracking local project paths. This enables knowing where a project is checked out on each machine.
