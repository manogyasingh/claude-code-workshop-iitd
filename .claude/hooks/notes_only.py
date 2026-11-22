#!/usr/bin/env python3
"""PreToolUse hook: file writes are allowed inside notes/ and nowhere else."""
import json
import os
import sys

event = json.load(sys.stdin)
target = os.path.abspath(event["tool_input"]["file_path"])
notes = os.path.join(os.environ["CLAUDE_PROJECT_DIR"], "notes")

if not target.startswith(notes + os.sep):
    print("Blocked by notes_only.py: this project only allows writes inside notes/.", file=sys.stderr)
    sys.exit(2)  # exit 2 = block the tool call; stderr is handed to Claude
