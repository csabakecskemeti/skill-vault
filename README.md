# Skill Vault

A collection of reusable Claude Code skills.

## What is a Skill?

A skill is a reusable prompt that teaches Claude Code how to perform a specific task. Skills are invoked with `/skillname` in Claude Code.

## Available Skills

| Skill | Description |
|-------|-------------|
| [projectz](./skills/projectz/) | Git-based markdown project tracker for managing projects across multiple computers |

## Installation

### Per-project installation
Copy the skill's `.md` file to your project's `.claude/commands/` directory:

```bash
mkdir -p .claude/commands
cp skills/projectz/projectz.md .claude/commands/
```

### Global installation
Copy to your user-level Claude config:

```bash
mkdir -p ~/.claude/commands
cp skills/projectz/projectz.md ~/.claude/commands/
```

## Creating Skills

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on creating and submitting skills.

## License

MIT
