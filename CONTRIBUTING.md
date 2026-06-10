# Contributing to Skill Vault

## Adding a New Skill

1. Create a directory under `skills/` with your skill name
2. Add the required files:
   - `<skillname>.md` - The skill definition (prompt that Claude follows)
   - `README.md` - Documentation for users

### Skill Definition Format

Your `<skillname>.md` should include:

```markdown
# /<skillname> - Short Description

Brief description of what the skill does.

## Usage

\`\`\`
/<skillname> [command] [args]
\`\`\`

## Commands

| Command | Description |
|---------|-------------|
| `/<skillname>` | Default action |
| `/<skillname> foo` | Does foo |

---

## Skill Instructions

(Instructions for Claude on how to implement each command)
```

### Guidelines

1. **Keep it focused** - One skill, one purpose
2. **Human-readable** - If your skill creates files, they should be readable without the skill
3. **Idempotent** - Commands should be safe to run multiple times
4. **Use existing tools** - Prefer `git`, standard file operations over custom solutions
5. **Document clearly** - Users should understand what the skill does without reading the implementation

## Pull Requests

1. Fork the repo
2. Create your skill in `skills/<name>/`
3. Test it works in Claude Code
4. Submit a PR with a description of what the skill does

## Questions?

Open an issue!
