# Skill Vault

A Claude Code plugin containing reusable skills.

## Installation

### From GitHub (recommended)

```
/plugin marketplace add csabakecskemeti/skill-vault
/plugin install skill-vault
```

### Manual installation

Clone and link locally:

```bash
git clone https://github.com/csabakecskemeti/skill-vault.git
```

Then in Claude Code:
```
claude --plugin-dir /path/to/skill-vault
```

Or copy individual skills to your personal skills folder:
```bash
cp -r skills/projectz ~/.claude/skills/
```

## Available Skills

| Skill | Command | Description |
|-------|---------|-------------|
| [projectz](./skills/projectz/) | `/projectz` | Git-based markdown project tracker for managing projects across multiple computers |

## Creating Skills

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on creating and submitting skills.

## Skill Format

Each skill lives in `skills/<name>/` and must have a `SKILL.md` with YAML frontmatter:

```markdown
---
name: my-skill
description: What this skill does and when to use it
argument-hint: "[arg1] [arg2]"
---

# Skill instructions here...
```

## License

MIT
