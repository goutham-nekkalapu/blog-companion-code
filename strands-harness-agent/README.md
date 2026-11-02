# strands-harness-agent

A tiny, runnable coding agent built on a real agent harness ([Strands](https://strandsagents.com/),
published as the `strands-agents/harness-sdk`). It wraps a bare Claude model in an
agent loop with file and shell tools so it can write code, run its own tests, read
the failures, and fix itself, all autonomously.

This is the companion code for the blog post
**"Building a Harness-Backed Agent: A Hands-On Walkthrough with Strands."**
The post walks through each piece; this folder is the complete, working version.
Post: <https://gouthamnekkalapu.com/posts/agent-harness-hands-on-strands>

## What's in here

| File | Purpose |
| --- | --- |
| `agent.py` | Builds the model + agent, registers tools and hooks, runs a task. |
| `hooks.py` | A loop-tracing hook that prints each tool call so you can watch the agent work. |
| `requirements.txt` | The harness (`strands-agents[anthropic]`) + community tools. |
| `setup.sh` | Creates a virtualenv and installs everything (plus `pytest`). |
| `.env.example` | Template for your `ANTHROPIC_API_KEY`. |

## How the harness maps to the primitives

| What the code does | Harness primitive |
| --- | --- |
| `Agent(...)` running until done | the agent loop |
| `file_read` / `file_write` | durable storage / workspace |
| `shell` | code execution + verification |
| `system_prompt` | feedforward: durable, project-wide context |
| `add_hook(...)` | feedback: observation and self-correction |

## Prerequisites

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)

## Setup

```bash
./setup.sh
source .venv/bin/activate
export ANTHROPIC_API_KEY=sk-ant-...   # or: cp .env.example .env && edit it
```

## Run it

```bash
# Default task: write fizzbuzz + a pytest test, run it, fix any failures.
python agent.py

# Or give it your own task:
python agent.py "Create a palindrome checker in palindrome.py with pytest tests, then run them."
```

The agent works inside a `workspace/` directory (created automatically and
git-ignored), so its files don't clutter the repo. You'll see the loop turn in
your terminal as it writes files, runs the tests, and self-corrects.

## Notes

- **Model:** `agent.py` defaults to `claude-sonnet-4-6`. Change `MODEL_ID` (or set
  the `MODEL_ID` env var) to use a different Claude model.
- **Safety:** the `shell` tool runs real commands on your machine. It's scoped to
  the `workspace/` directory by the system prompt, but read the task you give it.
  Strands hooks (see `hooks.py`) are the seam where you'd add approval gates or
  command allow-lists for stricter control.
