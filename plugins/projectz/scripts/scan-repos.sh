#!/bin/bash
# scan-repos.sh - Scan directories for git repos and output info
# Usage: scan-repos.sh [search_paths...] [--config ~/.projectz.yaml]
#
# Output format (one JSON object per line):
# {"path":"/path/to/repo","name":"repo-name","slug":"repo-name","remote":"git@...","role":"owner","status":"active","my_commits":10,"total_commits":15,"last_commit":"2024-01-20","days_ago":5}

set -e

# Default search paths
DEFAULT_PATHS="$HOME/Documents/workspace $HOME/code $HOME/projects $HOME/dev $HOME/src"

# Parse arguments
SEARCH_PATHS=""
CONFIG_FILE="$HOME/.projectz.yaml"

while [[ $# -gt 0 ]]; do
    case $1 in
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        *)
            SEARCH_PATHS="$SEARCH_PATHS $1"
            shift
            ;;
    esac
done

# Use default paths if none provided
if [ -z "$SEARCH_PATHS" ]; then
    SEARCH_PATHS="$DEFAULT_PATHS"
fi

# Read config
if [ -f "$CONFIG_FILE" ]; then
    MY_USERNAME=$(grep github_username "$CONFIG_FILE" 2>/dev/null | cut -d: -f2 | tr -d ' ' || echo "")
    MY_EMAIL_CONFIG=$(grep git_email "$CONFIG_FILE" 2>/dev/null | cut -d: -f2 | tr -d ' ' || echo "")
fi

# Fallback to git config
MY_EMAIL="${MY_EMAIL_CONFIG:-$(git config user.email 2>/dev/null || echo "")}"

# Function to detect role
detect_role() {
    local repo_path="$1"
    cd "$repo_path" 2>/dev/null || return

    local origin=$(git remote get-url origin 2>/dev/null || echo "")
    local has_upstream=$(git remote | grep -q upstream && echo "yes" || echo "no")
    local first_author=$(git log --reverse --format=%ae 2>/dev/null | head -1 || echo "")
    local my_commits=$(git shortlog -sne --all 2>/dev/null | grep -i "$MY_EMAIL" | awk '{sum+=$1} END {print sum+0}' || echo "0")
    local total_commits=$(git rev-list --all --count 2>/dev/null || echo "0")

    local is_mine="no"
    if [ -n "$MY_USERNAME" ] && echo "$origin" | grep -qi "$MY_USERNAME"; then
        is_mine="yes"
    fi

    local role="user"
    if [ "$is_mine" = "yes" ]; then
        if [ "$has_upstream" = "yes" ] || { [ -n "$first_author" ] && [ "$first_author" != "$MY_EMAIL" ]; }; then
            role="fork"
        else
            role="owner"
        fi
    else
        if [ "$my_commits" -gt 0 ]; then
            role="contributor"
        else
            role="user"
        fi
    fi

    echo "$role|$my_commits|$total_commits"
}

# Function to infer status
infer_status() {
    local days_ago="$1"
    if [ -z "$days_ago" ] || [ "$days_ago" = "" ]; then
        echo "draft"
    elif [ "$days_ago" -lt 14 ]; then
        echo "active"
    elif [ "$days_ago" -lt 90 ]; then
        echo "backlog"
    else
        echo "archived"
    fi
}

# Function to generate slug
slugify() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//'
}

# Find and process repos
for search_path in $SEARCH_PATHS; do
    # Expand ~ if present
    search_path="${search_path/#\~/$HOME}"

    if [ ! -d "$search_path" ]; then
        continue
    fi

    # Find git repos (max depth 4 to catch nested repos)
    find "$search_path" -maxdepth 4 -name ".git" -type d 2>/dev/null | while read git_dir; do
        repo_path=$(dirname "$git_dir")

        # Skip if in common ignore directories
        case "$repo_path" in
            */node_modules/*|*/.cache/*|*/vendor/*|*/.venv/*|*/venv/*)
                continue
                ;;
        esac

        cd "$repo_path" 2>/dev/null || continue

        # Get repo info
        name=$(basename "$repo_path")
        slug=$(slugify "$name")
        remote=$(git remote get-url origin 2>/dev/null || echo "")

        # Get last commit info
        last_commit=$(git log -1 --format=%Y-%m-%d 2>/dev/null || echo "")
        if [ -n "$last_commit" ]; then
            last_commit_ts=$(git log -1 --format=%ct 2>/dev/null || echo "0")
            now_ts=$(date +%s)
            days_ago=$(( (now_ts - last_commit_ts) / 86400 ))
        else
            days_ago=""
        fi

        # Detect role and get commit counts
        role_info=$(detect_role "$repo_path")
        role=$(echo "$role_info" | cut -d'|' -f1)
        my_commits=$(echo "$role_info" | cut -d'|' -f2)
        total_commits=$(echo "$role_info" | cut -d'|' -f3)

        # Infer status
        status=$(infer_status "$days_ago")

        # Output JSON (escaped for safety)
        printf '{"path":"%s","name":"%s","slug":"%s","remote":"%s","role":"%s","status":"%s","my_commits":%s,"total_commits":%s,"last_commit":"%s","days_ago":%s}\n' \
            "$repo_path" \
            "$name" \
            "$slug" \
            "$remote" \
            "$role" \
            "$status" \
            "${my_commits:-0}" \
            "${total_commits:-0}" \
            "$last_commit" \
            "${days_ago:-null}"
    done
done
