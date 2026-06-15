#!/bin/bash
# Local LLM skill setup
#
# Configure these in your shell profile (~/.zshrc or ~/.bashrc):
#   export LOCAL_LLM_URL="http://your-llm-host:port"
#   export LOCAL_LLM_MODEL="your-model-name"
#
# Defaults (if not set):
#   LOCAL_LLM_URL=http://192.168.7.103:4000
#   LOCAL_LLM_MODEL=Qwen/Qwen3.6-35B-A3B-FP8

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Install skill
mkdir -p ~/.claude/skills/local-llm
cp "$SCRIPT_DIR/skills/local-llm/SKILL.md" ~/.claude/skills/local-llm/

# Add to allow list (optional - add to ~/.claude/settings.local.json)
echo "Skill installed to ~/.claude/skills/local-llm/"
echo ""
echo "To auto-approve, add to ~/.claude/settings.local.json permissions.allow:"
echo '  "Bash(curl*<YOUR_LLM_HOST>*)"'
