#!/bin/bash
# Local LLM skill setup

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Install skill
mkdir -p ~/.claude/skills/local-llm
cp "$SCRIPT_DIR/skills/local-llm/SKILL.md" ~/.claude/skills/local-llm/

echo "Skill installed to ~/.claude/skills/local-llm/"
echo ""
echo "Add to ~/.zshenv (required for non-interactive shells):"
echo '  export LOCAL_LLM_URL="http://your-host:port"'
echo '  export LOCAL_LLM_MODEL="your-model-name"'
echo ""
echo "To auto-approve, add to ~/.claude/settings.local.json permissions.allow:"
echo '  "Bash(curl*your-host*)"'
