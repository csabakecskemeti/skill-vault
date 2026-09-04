---
description: Control local Kokoro text-to-speech (on/off/voice/speed/backend/server/status)
argument-hint: "[on|off|stop|status|voice NAME|speed N|backend embedded|http|server up|down|restart|log]"
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/tts-ctl.sh:*)
---

Run `${CLAUDE_PLUGIN_ROOT}/scripts/tts-ctl.sh $ARGUMENTS` (use `status` when no
arguments were given) and report its output verbatim in a couple of lines.

`server up` may print a first-time-setup notice and take several minutes while
it pulls a multi-GB image; that is expected, so report it rather than treating
it as an error.

Do not explain the plugin, do not suggest follow-up commands, and do not run
anything else.
