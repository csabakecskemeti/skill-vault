#!/bin/bash
# Local LLM skill setup

# Add to your shell profile (.zshrc, .bashrc):
export LOCAL_LLM_URL="http://192.168.7.103:4000"
export LOCAL_LLM_MODEL="Qwen/Qwen3.6-35B-A3B-FP8"

# Install skill
mkdir -p ~/.claude/skills/local-llm
cp "$(dirname "$0")/skills/local-llm/SKILL.md" ~/.claude/skills/local-llm/

echo "local-llm skill installed"
