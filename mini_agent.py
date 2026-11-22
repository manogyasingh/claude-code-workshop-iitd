# /// script
# requires-python = ">=3.10"
# dependencies = ["anthropic"]
# ///
"""An agent in about 40 lines: a model, one tool, and a loop.

Unlike the rest of the demo this calls the Claude API directly, so it needs an
API key, and usage is billed to that key:

    cp .env.example .env        # then put your key in .env
    uv run --env-file .env mini_agent.py "Find recent papers on topological insulators"
"""
import json
import sys

import anthropic

import arxiv_api

TOOLS = [{
    "name": "search_papers",
    "description": "Search arXiv by plain keywords. Returns id, title, authors and date.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "max_results": {"type": "integer"},
            "newest_first": {"type": "boolean"},
        },
        "required": ["query"],
    },
}]

client = anthropic.Anthropic()
question = " ".join(sys.argv[1:]) or "Find recent papers on topological insulators"
messages = [{"role": "user", "content": question}]

while True:
    response = client.beta.messages.create(
        model="claude-opus-5-5", max_tokens=16000, tools=TOOLS, messages=messages,
        # If a request is declined by a safety filter, let the API retry it on a fallback model.
        betas=["server-side-fallback-2026-07-01"], fallbacks="default",
    )
    messages.append({"role": "assistant", "content": response.content})
    if response.stop_reason != "tool_use":
        break  # the model answered in text, so we are done

    results = []
    for block in response.content:
        if block.type == "tool_use":  # the model ASKED for a call...
            print(f"-> {block.name}({json.dumps(block.input)})")
            try:
                output = json.dumps(arxiv_api.search(**block.input))  # ...and this program makes it
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
            except Exception as error:
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(error), "is_error": True})
    messages.append({"role": "user", "content": results})

print("".join(block.text for block in response.content if block.type == "text"))
