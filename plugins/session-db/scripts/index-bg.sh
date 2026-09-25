#!/bin/bash
# Hook entry point: index new transcript lines in the background so the
# session never waits on it. Overlapping runs are skipped by the indexer's lock.
nohup python3 "$(dirname "$0")/sessiondb.py" index -q >/dev/null 2>&1 &
exit 0
