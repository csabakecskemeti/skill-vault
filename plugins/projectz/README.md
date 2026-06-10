# projectz

A Claude Code skill for managing personal projects across multiple computers using Git and Markdown.

## Why?

You run multiple projects across multiple machines. You need a simple way to:
- Track what projects you're working on
- Know where each project lives on each computer
- Manage tasks and notes
- Sync everything via Git

**No database. No SaaS. Just Markdown + Git.**

## Installation

### Via skill-vault plugin

```
/plugin marketplace add csabakecskemeti/skill-vault
/plugin install skill-vault
```

The skill will be available as `/skill-vault:projectz` or just `/projectz`.

### Manual (single skill)

```bash
mkdir -p ~/.claude/skills
cp -r projectz ~/.claude/skills/
```

## Setup

1. Create your own projectz repo on GitHub (e.g., `yourname/projectz`)
2. Initialize it with the template from `template/` folder
3. Run `/projectz init git@github.com:yourname/projectz.git`

## Usage

```
/projectz                              # Show all projects
/projectz new "My Web App"             # Create project
/projectz task my-web-app "Add auth"   # Add task
/projectz done my-web-app 001          # Complete task
/projectz sync                         # Commit and push
```

## Commands

| Command | Description |
|---------|-------------|
| `/projectz` | Show status overview |
| `/projectz init <repo>` | Set up projectz on this computer |
| `/projectz new <name>` | Create a new project |
| `/projectz show <project>` | Show project details |
| `/projectz task <project> <title>` | Add a task |
| `/projectz done <project> <id>` | Mark task done |
| `/projectz note <project> <text>` | Add a note |
| `/projectz status <project> <status>` | Change project status |
| `/projectz link <project> <path>` | Link to local checkout |
| `/projectz sync` | Git add, commit, pull, push |
| `/projectz discover` | Find local project checkouts |

## How It Works

```
┌─────────────────────────────────────┐
│  Your projectz repo (GitHub)        │
│  └── Markdown files                 │
└──────────────────┬──────────────────┘
                   │ git clone/pull/push
                   ▼
┌─────────────────────────────────────┐
│  /projectz skill (Claude Code)      │
│  └── Reads/writes the markdown      │
└─────────────────────────────────────┘
```

## Repository Structure

```
projectz/
├── README.md
├── INDEX.md               # Project overview
├── computers/
│   └── comp-abc123.md     # Per-computer local paths
└── projects/
    └── my-project/
        ├── README.md      # Project info + notes
        └── tasks/
            └── 001-setup.md
```

## License

MIT
