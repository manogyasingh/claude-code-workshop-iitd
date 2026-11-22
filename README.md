# Claude Code workshop demo: a research paper helper

This is the demo code from a Claude campus workshop at IIT Delhi on 12 November 2026.
The workshop covered how tools turn a language model into an agent, and the three ways
to extend Claude Code: MCP, skills and hooks.

The example is small on purpose. Claude searches arXiv, writes a paper brief in a fixed
format, and every action it takes is logged.

| Idea | File | What it shows |
| --- | --- | --- |
| MCP server | `arxiv_server.py` | Two Python functions become tools Claude can call |
| Skill | `.claude/skills/paper-brief/` | A procedure and a template, loaded only when needed |
| Hooks | `.claude/settings.json`, `.claude/hooks/` | Your code, run by Claude Code on every tool call |
| Agent loop | `mini_agent.py` | Optional: a model, one tool and a loop in 40 lines |

`arxiv_api.py` is ordinary HTTP and XML code with no AI in it. The server and the agent both call it.

## Requirements

- [Claude Code](https://code.claude.com/docs), installed and signed in
- [uv](https://docs.astral.sh/uv/)
- Python 3.10 or newer, available as `python3`
- Network access to arxiv.org

The three exercises need no API key. Only the optional `mini_agent.py` does.

This was written and tested on Linux. The hooks call `python3` and `reset.sh` is a shell
script, so on Windows use WSL.

## Setup

Read `.claude/settings.json` and the two scripts in `.claude/hooks/` before you start.
They are short, and they run on your machine whenever Claude Code uses a tool in this
folder. Do this for any project you download that ships hooks.

From this folder:

```sh
python3 arxiv_api.py topological insulators     # network check: prints five papers
claude mcp add arxiv -- uv run arxiv_server.py  # register the server for this folder
claude mcp list                                 # arxiv should show as connected
claude                                          # accept the folder trust prompt
```

The first `uv run` downloads the `mcp` package, so it takes a few seconds.

## Exercise 1: MCP

Inside Claude Code:

```
/mcp
Find the five most recent arXiv papers on topological insulators
```

Things to notice:

- Claude Code asks permission before it runs a tool it has not seen.
- The call is `search_papers` with `newest_first: true`. You did not type that flag.
  Claude read the tool's schema and chose it from the word "recent".
- The schema came from the type hints and docstring in `arxiv_server.py`.

## Exercise 2: Skills

Read `.claude/skills/paper-brief/SKILL.md`, then in the same session:

```
Brief me on the second one
```

Things to notice, in order:

1. The `paper-brief` skill loads now, not at startup. Until this point only its one-line description was in context.
2. `template.md` is read, because step 2 of the skill points to it.
3. `get_abstract` is called: the skill uses the MCP tool from exercise 1.
4. The brief is written to `notes/<arxiv-id>.md` with exactly the template's headings.

You can also run a skill by name: `/paper-brief 1310.0255`.

## Exercise 3: Hooks

In a second terminal, in this folder:

```sh
tail -F tool-log.jsonl
```

The log already holds every tool call from exercises 1 and 2. `log_tool.py` has been
running the whole time, and Claude was never told about it. Ask for another brief and
watch the lines arrive.

Then try the blocking hook:

```
Save a one-line summary of that as summary.md next to arxiv_server.py
```

`notes_only.py` exits with code 2, which blocks the write and hands its error message to
Claude. Claude tells you why, and usually offers to save the file inside `notes/` instead.

This hook also stops Claude from editing the code in this folder. To let Claude change
the files, delete the `PreToolUse` block from `.claude/settings.json` and restart `claude`.

## Optional: an agent loop in 40 lines

`mini_agent.py` is the loop that sits inside every agent: call the model, run the tools
it asks for, send the results back, repeat. It calls the Claude API directly, so it
needs an API key from the [Claude Console](https://platform.claude.com/) and is billed
to that key.

```sh
cp .env.example .env        # then put your key in .env
uv run --env-file .env mini_agent.py "Find recent papers on topological insulators"
```

`.env` is listed in `.gitignore`. Never commit it.

## Things to try next

- Add a third tool to `arxiv_server.py`, such as one that lists new papers in a category. Restart `claude` to pick it up.
- Change `template.md` and brief the same paper again.
- Make the description in `SKILL.md` vague and see whether the skill still triggers.
- Write a hook of your own. Start from `log_tool.py`: the event arrives as JSON on stdin, and the exit code decides what happens next.

## Reset

```sh
./reset.sh
```

This removes the arxiv server registration, the notes, the log and the cache.

## If something does not work

| Symptom | Fix |
| --- | --- |
| `/mcp` shows arxiv as failed | Run `uv run arxiv_server.py` in a shell to see the error. A healthy server starts and waits silently. |
| Tool error "arXiv is unreachable" | Check your network. Answers are cached in `.cache/`, so only a query you have run before works offline. |
| Tool error "arXiv rejected the request" | The query used search syntax the helper does not support. Claude normally retries with plain keywords. |
| The skill does not trigger | Invoke it by name: `/paper-brief 1310.0255`. |
| Nothing appears in `tool-log.jsonl` | Hooks load at startup. Restart `claude` from this folder. |
| Claude cannot edit a file here | That is `notes_only.py` doing its job. See exercise 3. |

## What not to share

`tool-log.jsonl` records every tool call, including file paths on your machine and what
you searched for. It is listed in `.gitignore` along with `.env`, `.cache/` and your notes.
Keep it that way if you publish your own copy.

## Learn more

- Claude Code: https://code.claude.com/docs
- Skills: https://code.claude.com/docs/en/skills
- Hooks: https://code.claude.com/docs/en/hooks
- Model Context Protocol: https://modelcontextprotocol.io

## Licence

MIT. See `LICENSE`. Use it, change it, and teach with it.
