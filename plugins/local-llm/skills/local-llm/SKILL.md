---
name: local-llm
description: Call local LLM for code generation > 50 lines, boilerplate, tests, or docs. Saves tokens.
---

# /local-llm

Call local LLM for routine tasks. Saves Claude tokens.

## Config (env vars)

```bash
export LOCAL_LLM_URL="http://192.168.7.103:4000"
export LOCAL_LLM_MODEL="Qwen/Qwen3.6-35B-A3B-FP8"
```

## Execute

```bash
curl -s ${LOCAL_LLM_URL}/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{\"model\": \"${LOCAL_LLM_MODEL}\", \"messages\": [{\"role\": \"system\", \"content\": \"You are a coding assistant. Be concise. No thinking tags.\"}, {\"role\": \"user\", \"content\": \"PROMPT\"}]}" \
  | jq -r '.choices[0].message.content'
```

## When to Use
- Code generation > 50 lines
- Boilerplate / repetitive patterns
- Test writing with clear spec
- Documentation from code
