#!/bin/bash
# analyze-repo.sh - Analyze a single git repo and output info
# Usage: analyze-repo.sh /path/to/repo [--config ~/.projectz.yaml]
#
# Output: JSON with repo analysis

set -e

REPO_PATH="$1"
CONFIG_FILE="$HOME/.projectz.yaml"

# Parse additional arguments
shift || true
while [[ $# -gt 0 ]]; do
    case $1 in
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

if [ -z "$REPO_PATH" ] || [ ! -d "$REPO_PATH/.git" ]; then
    echo '{"error":"Not a git repository"}' >&2
    exit 1
fi

# Read config
if [ -f "$CONFIG_FILE" ]; then
    MY_USERNAME=$(grep github_username "$CONFIG_FILE" 2>/dev/null | cut -d: -f2 | tr -d ' ' || echo "")
    MY_EMAIL_CONFIG=$(grep git_email "$CONFIG_FILE" 2>/dev/null | cut -d: -f2 | tr -d ' ' || echo "")
fi

MY_EMAIL="${MY_EMAIL_CONFIG:-$(git config user.email 2>/dev/null || echo "")}"

cd "$REPO_PATH"

# Basic info
name=$(basename "$REPO_PATH")
slug=$(echo "$name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//')
remote=$(git remote get-url origin 2>/dev/null || echo "")
branch=$(git branch --show-current 2>/dev/null || echo "main")

# Commit info
last_commit=$(git log -1 --format=%Y-%m-%d 2>/dev/null || echo "")
last_commit_ts=$(git log -1 --format=%ct 2>/dev/null || echo "0")
now_ts=$(date +%s)
if [ "$last_commit_ts" != "0" ]; then
    days_ago=$(( (now_ts - last_commit_ts) / 86400 ))
else
    days_ago="null"
fi

# Commit counts
my_commits=$(git shortlog -sne --all 2>/dev/null | grep -i "$MY_EMAIL" | awk '{sum+=$1} END {print sum+0}' || echo "0")
total_commits=$(git rev-list --all --count 2>/dev/null || echo "0")

# Role detection
is_mine="no"
if [ -n "$MY_USERNAME" ] && echo "$remote" | grep -qi "$MY_USERNAME"; then
    is_mine="yes"
fi

has_upstream=$(git remote | grep -q upstream && echo "yes" || echo "no")
first_author=$(git log --reverse --format=%ae 2>/dev/null | head -1 || echo "")

if [ "$is_mine" = "yes" ]; then
    if [ "$has_upstream" = "yes" ] || { [ -n "$first_author" ] && [ "$first_author" != "$MY_EMAIL" ]; }; then
        role="fork"
        upstream_url=$(git remote get-url upstream 2>/dev/null || echo "")
    else
        role="owner"
        upstream_url=""
    fi
else
    if [ "$my_commits" -gt 0 ]; then
        role="contributor"
    else
        role="user"
    fi
    upstream_url=""
fi

# Status inference
if [ "$days_ago" = "null" ] || [ -z "$days_ago" ]; then
    status="draft"
elif [ "$days_ago" -lt 14 ]; then
    status="active"
elif [ "$days_ago" -lt 90 ]; then
    status="backlog"
else
    status="archived"
fi

# Check for README to extract description
description=""
for readme in README.md README.rst README.txt README; do
    if [ -f "$readme" ]; then
        # Get first non-empty, non-heading line as description
        description=$(grep -v '^#' "$readme" | grep -v '^$' | grep -v '^\[' | grep -v '^!' | head -1 | cut -c1-200 || echo "")
        break
    fi
done

# Detect primary language/tech
languages=""
if [ -f "package.json" ]; then languages="javascript"; fi
if [ -f "requirements.txt" ] || [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then languages="python"; fi
if [ -f "Cargo.toml" ]; then languages="rust"; fi
if [ -f "go.mod" ]; then languages="go"; fi
if [ -f "Gemfile" ]; then languages="ruby"; fi
if [ -f "pom.xml" ] || [ -f "build.gradle" ]; then languages="java"; fi

# Output JSON
cat <<EOF
{
  "path": "$REPO_PATH",
  "name": "$name",
  "slug": "$slug",
  "remote": "$remote",
  "branch": "$branch",
  "role": "$role",
  "status": "$status",
  "my_commits": $my_commits,
  "total_commits": $total_commits,
  "last_commit": "$last_commit",
  "days_ago": $days_ago,
  "has_upstream": "$has_upstream",
  "upstream_url": "$upstream_url",
  "description": "$(echo "$description" | sed 's/"/\\"/g')",
  "languages": "$languages"
}
EOF
