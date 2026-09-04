#!/usr/bin/env python3
"""Read/write plugin config and report daemon status. Stdlib only."""
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import speak  # noqa: E402
import ttslib  # noqa: E402

# Kokoro's bundled voices. 'a' = American English, 'b' = British.
VOICES = {
    "a": ["af_heart", "af_bella", "af_nicole", "af_aoede", "af_kore", "af_sarah",
          "af_nova", "af_sky", "af_alloy", "af_jessica", "af_river",
          "am_michael", "am_fenrir", "am_puck", "am_echo", "am_eric",
          "am_liam", "am_onyx", "am_santa", "am_adam"],
    "b": ["bf_emma", "bf_isabella", "bf_alice", "bf_lily",
          "bm_george", "bm_fable", "bm_lewis", "bm_daniel"],
}

BOOL = {"true": True, "1": True, "yes": True, "on": True,
        "false": False, "0": False, "no": False, "off": False}


def coerce(key, raw):
    if key == "backend":
        if raw not in ("embedded", "http"):
            raise SystemExit(f"backend must be 'embedded' or 'http', got {raw!r}")
        return raw
    if key in ("enabled",):
        if raw.lower() not in BOOL:
            raise SystemExit(f"{key} must be true/false, got {raw!r}")
        return BOOL[raw.lower()]
    if key in ("speed",):
        return float(raw)
    if key in ("max_chars", "idle_unload_seconds"):
        return int(raw)
    return raw


def main():
    args = sys.argv[1:] or ["status"]
    cmd = args[0]

    if cmd == "set":
        if len(args) < 3:
            raise SystemExit("usage: config.py set KEY VALUE")
        key, raw = args[1], args[2]
        if key not in ttslib.DEFAULTS:
            raise SystemExit(f"unknown key {key!r}; known: {', '.join(ttslib.DEFAULTS)}")
        cfg = ttslib.load_config()
        cfg[key] = coerce(key, raw)
        if key == "voice":
            known = VOICES["a"] + VOICES["b"]
            if raw not in known:
                print(f"warning: {raw!r} is not a known Kokoro voice", file=sys.stderr)
            cfg["lang_code"] = "b" if raw.startswith(("bf_", "bm_")) else "a"
        ttslib.save_config(cfg)
        if key in ("voice", "lang_code", "backend", "server_url"):
            # lang_code is baked into the loaded pipeline; restart to apply.
            speak.request({"cmd": "shutdown"}, autostart=False)
        return

    if cmd == "voices":
        for lang, names in VOICES.items():
            label = "American English" if lang == "a" else "British English"
            print(f"{label} (lang_code={lang}):")
            for name in names:
                print(f"  {name}")
        return

    if cmd == "get":
        print(json.dumps(ttslib.load_config(), indent=2))
        return

    cfg = ttslib.load_config()
    ping = speak.request({"cmd": "ping"}, autostart=False)
    print(f"  speaking : {'on' if cfg['enabled'] else 'off'}")
    print(f"  voice    : {cfg['voice']} (lang {cfg['lang_code']}, speed {cfg['speed']}x)")
    print(f"  max chars: {cfg['max_chars']}")
    if ping.get("ok"):
        print(f"  daemon   : running (pid {ping['pid']}), "
              f"model {'loaded' if ping['loaded'] else 'not loaded yet'}, "
              f"{ping['queued']} queued")
    else:
        print("  daemon   : not running (starts on the next reply)")
    print(f"  backend  : {cfg['backend']}")
    if cfg["backend"] == "http":
        print(f"  server   : {cfg['server_url']}", end="")
        try:
            with urllib.request.urlopen(f"{cfg['server_url'].rstrip('/')}/health", timeout=4) as r:
                info = json.loads(r.read().decode())
            svc, api = info.get("service"), info.get("api_version")
            if svc != "kokoro-tts-server":
                print(f"  reachable, but not a kokoro-tts-server (assuming OpenAI-compatible)")
            elif api != 1:
                print(f"  INCOMPATIBLE - server API v{api}, plugin speaks v1")
            else:
                print(f"  ok (v{info.get('version')}, API v{api}, "
                      f"loaded: {info.get('loaded_pipelines') or 'none yet'})")
        except Exception as exc:
            print(f"  UNREACHABLE ({exc})")
            print("             start it with: docker compose up -d")
    elif not ttslib.VENV_PYTHON.exists():
        print(f"  venv     : {ttslib.VENV}  MISSING - run setup.sh")
    else:
        probe = subprocess.run([str(ttslib.VENV_PYTHON), "-c", "import numpy, soundfile, kokoro"],
                               capture_output=True)
        if probe.returncode == 0:
            print(f"  venv     : {ttslib.VENV}  ok")
        else:
            reason = probe.stderr.decode(errors="replace").strip().splitlines()[-1:] or ["unknown"]
            print(f"  venv     : {ttslib.VENV}  INCOMPLETE - {reason[0]}")
            print("             run setup.sh (or wait for it to finish)")
    print(f"  log      : {ttslib.LOGFILE}")


if __name__ == "__main__":
    main()
