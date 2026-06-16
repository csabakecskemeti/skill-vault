#!/bin/bash
# Local LLM caller with metrics tracking

eval "$(grep '^export LOCAL_LLM' ~/.zshenv)"

PROMPT="$1"
METRICS="$HOME/.claude/local_llm_metrics.json"

response=$(curl -s "$LOCAL_LLM_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{"model": "'"$LOCAL_LLM_MODEL"'", "messages": [{"role": "system", "content": "You are a coding assistant. Output code only."}, {"role": "user", "content": "'"$PROMPT"'"}]}')

clean=$(echo "$response" | tr -d '\000-\037')
echo "$clean" | jq -r '.choices[0].message.content' | sed -n '/^```/,/^```/p'

# Update metrics
tokens=$(echo "$clean" | jq -r '.usage.total_tokens // 0')
[ -f "$METRICS" ] && prev=$(cat "$METRICS") || prev='{"total_calls":0,"total_tokens":0}'
tc=$(echo "$prev" | jq -r '.total_calls // 0')
tt=$(echo "$prev" | jq -r '.total_tokens // 0')
echo "{\"total_calls\":$((tc+1)),\"total_tokens\":$((tt+tokens)),\"date\":\"$(date +%F)\"}" > "$METRICS"
