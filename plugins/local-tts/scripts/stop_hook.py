#!/usr/bin/env python3
"""Stop-hook worker: read the last assistant reply from the transcript and
hand it to the TTS daemon.

Runs detached from the hook itself, so a cold daemon start never blocks the
end of a turn.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import speak  # noqa: E402
import ttslib  # noqa: E402


def last_assistant_text(transcript_path: str):
    """Return (uuid, text) of the final assistant message in the transcript."""
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None, ""

    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if entry.get("type") != "assistant":
            continue
        message = entry.get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            blocks = [content]
        elif isinstance(content, list):
            blocks = [b.get("text", "") for b in content
                      if isinstance(b, dict) and b.get("type") == "text"]
        else:
            continue
        text = "\n".join(b for b in blocks if b.strip())
        if text.strip():
            return entry.get("uuid") or entry.get("requestId"), text
    return None, ""


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0

    cfg = ttslib.load_config()
    if not cfg.get("enabled", True):
        return 0

    session_id = payload.get("session_id", "")
    uid, text = last_assistant_text(payload.get("transcript_path", ""))
    if not text.strip():
        return 0

    # Stop can fire more than once for the same reply; speak it only once.
    state = ttslib.load_state()
    spoken = state.setdefault("spoken", {})
    if uid and spoken.get(session_id) == uid:
        return 0
    if uid:
        spoken[session_id] = uid
        # Keep the dedup table from growing without bound across sessions.
        if len(spoken) > 50:
            for key in list(spoken)[:-50]:
                spoken.pop(key, None)
        ttslib.save_state(state)

    cleaned = ttslib.clean_for_tts(text, cfg["max_chars"])
    if not cleaned:
        return 0

    speak.request({"cmd": "speak", "text": cleaned,
                   "voice": cfg["voice"], "speed": cfg["speed"]})
    return 0


if __name__ == "__main__":
    sys.exit(main())
