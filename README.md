# Skill Vault

A Claude Code plugin marketplace containing reusable skills.

## Installation

**Add the marketplace:**
```
/plugin marketplace add csabakecskemeti/skill-vault
```

**Install the plugin (choose one):**
```
# Option 1: Interactive - run /plugin, select projectz, press 'i' to install

# Option 2: Command line
/plugin install projectz@skill-vault
```

## Available Plugins

| Plugin | Command | Description |
|--------|---------|-------------|
| [projectz](./plugins/projectz/) | `/projectz` | Git-based markdown project tracker for managing projects across multiple computers |

## Structure

```
skill-vault/
├── .claude-plugin/
│   └── marketplace.json       # Marketplace catalog
└── plugins/
    └── projectz/
        ├── .claude-plugin/
        │   └── plugin.json    # Plugin manifest
        └── skills/
            └── projectz/
                └── SKILL.md   # Skill definition
```

## Creating Plugins

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

MIT
