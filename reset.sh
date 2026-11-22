#!/bin/sh
# Put the demo back to its starting state.
cd "$(dirname "$0")" || exit 1
rm -f tool-log.jsonl notes/*.md .claude/settings.local.json
rm -rf .cache
find . -name __pycache__ -type d -prune -exec rm -rf {} +
claude mcp remove arxiv >/dev/null 2>&1
echo "Demo reset: arxiv server unregistered; notes, log and cache cleared."
