---
name: local-llm
description: Call local LLM for code generation > 50 lines, boilerplate, tests, or docs. Saves tokens.
---

# /local-llm

Call local LLM for routine tasks. Saves Claude tokens.

## Required Env Vars

Set in `~/.zshenv`:
```bash
export LOCAL_LLM_URL="http://your-host:port"
export LOCAL_LLM_MODEL="your-model-name"
```

## Execute

```bash
source ~/.zshenv && curl -s "$LOCAL_LLM_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d "{\"model\": \"$LOCAL_LLM_MODEL\", \"messages\": [{\"role\": \"system\", \"content\": \"You are a coding assistant. Output code only.\"}, {\"role\": \"user\", \"content\": \"PROMPT\"}]}" \
  | jq -r '.choices[0].message.content'
```

## When to Use
- Code generation > 50 lines
- Boilerplate / repetitive patterns
- Test writing with clear spec
- Documentation from code
