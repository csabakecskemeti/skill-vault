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
eval "$(grep '^export LOCAL_LLM' ~/.zshenv)" && response=$(curl -s "$LOCAL_LLM_URL/v1/chat/completions" -H "Content-Type: application/json" -d '{"model": "'"$LOCAL_LLM_MODEL"'", "messages": [{"role": "system", "content": "You are a coding assistant. Output code only."}, {"role": "user", "content": "PROMPT"}]}') && echo "$response" | jq -r '.choices[0].message.content' | sed -n '/^```/,/^```/p' && tokens=$(echo "$response" | jq -r '.usage.total_tokens // 0' 2>/dev/null || echo 0) && metrics="$HOME/.claude/local_llm_metrics.json" && [ -f "$metrics" ] && prev=$(cat "$metrics") || prev='{"total_calls":0,"total_tokens":0}' && tc=$(echo "$prev" | jq -r '.total_calls // 0') && tt=$(echo "$prev" | jq -r '.total_tokens // 0') && echo "{\"total_calls\":$((tc+1)),\"total_tokens\":$((tt+tokens)),\"date\":\"$(date +%F)\"}" > "$metrics"
```

## When to Use
- Code generation > 50 lines
- Boilerplate / repetitive patterns
- Test writing with clear spec
- Documentation from code
