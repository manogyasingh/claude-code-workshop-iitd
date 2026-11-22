#!/usr/bin/env python3
"""PostToolUse hook: append every tool call Claude makes to tool-log.jsonl."""
import json
import os
import sys
import time

event = json.load(sys.stdin)  # Claude Code pipes the event in as JSON

record = {
    "at": time.strftime("%H:%M:%S"),
    "tool": event["tool_name"],
    "input": event["tool_input"],
}
log = os.environ["CLAUDE_PROJECT_DIR"] + "/tool-log.jsonl"
with open(log, "a") as f:
    f.write(json.dumps(record) + "\n")
