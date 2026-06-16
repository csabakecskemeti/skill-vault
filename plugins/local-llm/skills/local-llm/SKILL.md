---
name: local-llm
description: Call local LLM for code generation > 50 lines, boilerplate, tests, or docs. Saves tokens.
allowed-tools:
  - Bash
---

# /local-llm

Call local LLM for routine tasks. Saves Claude tokens.

## Execute

!`${CLAUDE_SKILL_DIR}/scripts/local-llm.sh "PROMPT"`

## When to Use
- Code generation > 50 lines
- Boilerplate / repetitive patterns
- Test writing with clear spec
- Documentation from code
