#!/bin/bash
# Local LLM caller with metrics tracking.
#
# Config resolution, first match wins:
#   1. LOCAL_LLM_URL / LOCAL_LLM_MODEL already in the environment
#   2. ~/.fleet-aliases.sh  (provides FLEET_LLM_HOST + fleet_llm_model)
#   3. ~/.zshenv            (legacy)
#
# The model is resolved from the server at call time unless explicitly pinned,
# so it follows whatever the cluster is currently serving. A pinned name goes
# stale the moment the cluster loads something else.
#
# Depends only on bash + python3 (no jq: it is absent on several fleet hosts
# and not on the non-interactive PATH on macOS).

set -o pipefail

PROMPT="$1"
METRICS="$HOME/.claude/local_llm_metrics.json"
MAX_TOKENS="${LOCAL_LLM_MAX_TOKENS:-2048}"

if [ -z "$PROMPT" ]; then
  echo "usage: local-llm.sh <prompt>" >&2
  exit 2
fi

# --- resolve config ---------------------------------------------------------
# shellcheck disable=SC1090
[ -f "$HOME/.fleet-aliases.sh" ] && . "$HOME/.fleet-aliases.sh"

if [ -z "$LOCAL_LLM_URL" ] && [ -f "$HOME/.zshenv" ]; then
  eval "$(grep '^export LOCAL_LLM' "$HOME/.zshenv")"
fi

if [ -z "$LOCAL_LLM_URL" ]; then
  echo "Error: LOCAL_LLM_URL is not set (no ~/.fleet-aliases.sh, no ~/.zshenv)" >&2
  exit 1
fi

if [ -z "$LOCAL_LLM_MODEL" ] && command -v fleet_llm_model >/dev/null 2>&1; then
  LOCAL_LLM_MODEL="$(fleet_llm_model)"
fi

# --- call -------------------------------------------------------------------
out=$(LOCAL_LLM_URL="$LOCAL_LLM_URL" \
      LOCAL_LLM_MODEL="$LOCAL_LLM_MODEL" \
      LOCAL_LLM_API_KEY="${LOCAL_LLM_API_KEY:-vllm}" \
      MAX_TOKENS="$MAX_TOKENS" \
      PROMPT="$PROMPT" python3 - <<'PY'
import json, os, sys, urllib.request, urllib.error

url    = os.environ["LOCAL_LLM_URL"].rstrip("/")
model  = os.environ.get("LOCAL_LLM_MODEL") or ""
key    = os.environ["LOCAL_LLM_API_KEY"]
maxtok = int(os.environ["MAX_TOKENS"])
prompt = os.environ["PROMPT"]


def get(path, timeout=10):
    req = urllib.request.Request(url + path,
                                 headers={"Authorization": "Bearer " + key})
    return json.load(urllib.request.urlopen(req, timeout=timeout))


# Resolve the served model if not pinned.
if not model:
    try:
        model = (get("/v1/models").get("data") or [{}])[0].get("id", "")
    except Exception as e:
        print(f"Error: cannot list models at {url}: {e}", file=sys.stderr)
        sys.exit(1)
if not model:
    print(f"Error: no model available at {url}", file=sys.stderr)
    sys.exit(1)

body = json.dumps({
    "model": model,
    "max_tokens": maxtok,
    "messages": [
        {"role": "system", "content": "You are a coding assistant. Output code only."},
        {"role": "user", "content": prompt},
    ],
}).encode()

req = urllib.request.Request(
    url + "/v1/chat/completions", data=body,
    headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})

try:
    d = json.load(urllib.request.urlopen(req, timeout=300))
except urllib.error.HTTPError as e:
    print(f"Error: HTTP {e.code} from {url}: {e.read()[:300].decode(errors='replace')}",
          file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error: request failed: {e}", file=sys.stderr)
    sys.exit(1)

choice  = (d.get("choices") or [{}])[0]
msg     = choice.get("message") or {}
content = msg.get("content")
finish  = choice.get("finish_reason")

# Reasoning models emit reasoning_content before content. If max_tokens runs out
# during the think phase, content is null and finish_reason is "length" - which
# looks like a failure but is really a truncated response.
if not content:
    if finish == "length":
        print(f"Error: truncated during reasoning (finish_reason=length, "
              f"max_tokens={maxtok}).", file=sys.stderr)
        print("       Raise LOCAL_LLM_MAX_TOKENS and retry.", file=sys.stderr)
    else:
        print(f"Error: empty response from {model} (finish_reason={finish})",
              file=sys.stderr)
    sys.exit(1)

print(content)
print("__TOKENS__:%d" % (d.get("usage", {}).get("total_tokens") or 0))
PY
) || exit 1

# --- output -----------------------------------------------------------------
tokens=$(printf '%s\n' "$out" | sed -n 's/^__TOKENS__:\([0-9]*\)$/\1/p' | tail -1)
content=$(printf '%s\n' "$out" | sed '/^__TOKENS__:[0-9]*$/d')

# Prefer a fenced code block; fall back to the whole answer if there is none.
block=$(printf '%s\n' "$content" | sed -n '/^```/,/^```/p')
if [ -n "$block" ]; then printf '%s\n' "$block"; else printf '%s\n' "$content"; fi

# --- metrics ----------------------------------------------------------------
mkdir -p "$(dirname "$METRICS")"
TOKENS="${tokens:-0}" METRICS="$METRICS" python3 - <<'PY'
import json, os, datetime
p = os.environ["METRICS"]
try:
    prev = json.load(open(p))
except Exception:
    prev = {"total_calls": 0, "total_tokens": 0}
json.dump({"total_calls": prev.get("total_calls", 0) + 1,
           "total_tokens": prev.get("total_tokens", 0) + int(os.environ["TOKENS"]),
           "date": datetime.date.today().isoformat()}, open(p, "w"))
PY
