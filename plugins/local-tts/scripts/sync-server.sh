#!/bin/sh
# Re-vendor server/ from a kokoro-tts-server checkout, so the bundled build
# context does not silently drift from upstream.
set -e
SRC=${1:-../kokoro-tts-server}
DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

[ -f "$SRC/Dockerfile" ] || { echo "not a kokoro-tts-server checkout: $SRC" >&2; exit 1; }

rsync -a --delete --exclude '__pycache__' \
  "$SRC/Dockerfile" "$SRC/requirements.txt" "$SRC/docker-compose.yml" \
  "$SRC/kokoro_server" "$DIR/server/"

SHA=$(git -C "$SRC" rev-parse --short HEAD 2>/dev/null || echo unknown)
sed -i '' "s/^- Upstream commit: .*/- Upstream commit: \`$SHA\`/" "$DIR/server/VENDORED.md" 2>/dev/null \
  || sed -i "s/^- Upstream commit: .*/- Upstream commit: \`$SHA\`/" "$DIR/server/VENDORED.md"
echo "synced server/ from $SRC at $SHA"
