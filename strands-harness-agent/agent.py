"""A mini coding agent built on the Strands harness.

Agent = Model + Harness. Here the model is Claude and the harness is everything
else: the agent loop (invoke -> tool call -> result -> repeat), the tools that
give it hands (file read/write + shell), a system prompt that steers it
(feedforward), and a hook that lets us watch and shape the loop (feedback).

Run:
    python agent.py
    python agent.py "Create a palindrome checker with pytest tests and run them."
"""

import os
import sys
from pathlib import Path

from strands import Agent
from strands.models.anthropic import AnthropicModel
from strands_tools import file_read, file_write, shell

from hooks import LoopTracer

# Claude model to run against. Override with the MODEL_ID env var if you like.
MODEL_ID = os.environ.get("MODEL_ID", "claude-sonnet-4-6")

# The agent does all its work here so generated files don't clutter the repo.
WORKSPACE = Path(__file__).parent / "workspace"

# Feedforward: durable, project-wide context that's true on every turn.
# Note what's absent: the specific task. Per-task instructions live in the task.
CODING_PROMPT = f"""You are a coding agent working inside the {WORKSPACE} directory.
Always write files there using relative paths under that directory.

Workflow for every task:
1. Write the implementation and its tests to files with file_write.
2. Run the tests with the shell tool (e.g. `pytest -q`).
3. If anything fails, read the output, fix the code, and re-run.
4. Only report success once the tests actually pass.

Keep files small and focused. Never claim something works without running it."""

DEFAULT_TASK = (
    "Create fizzbuzz.py with a fizzbuzz(n) function and a pytest test file, "
    "then run the tests and fix any failures."
)


def build_agent() -> Agent:
    """Wrap a bare Claude model in a harness: tools, prompt, and a tracing hook."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit(
            "ANTHROPIC_API_KEY is not set. Export it or copy .env.example to .env.\n"
            "  export ANTHROPIC_API_KEY=sk-ant-..."
        )

    model = AnthropicModel(model_id=MODEL_ID, max_tokens=4096)

    return Agent(
        model=model,
        system_prompt=CODING_PROMPT,
        # Tools are the agent's hands: durable storage (file_read/file_write)
        # and code execution (shell) so it can verify its own work.
        tools=[file_read, file_write, shell],
        # Hooks are the feedback seam. LoopTracer just prints the loop; swap in
        # validation/approval hooks here for a more controlled harness.
        hooks=[LoopTracer()],
    )


def main() -> None:
    task = " ".join(sys.argv[1:]).strip() or DEFAULT_TASK

    WORKSPACE.mkdir(exist_ok=True)

    print(f"Model:     {MODEL_ID}")
    print(f"Workspace: {WORKSPACE}")
    print(f"Task:      {task}\n")

    agent = build_agent()

    # This single call runs the agent loop until the model produces a final
    # answer. Everything you see scroll by is the harness executing the model's
    # decisions and feeding the results back in.
    result = agent(task)

    print("\n--- final answer ---")
    print(result)


if __name__ == "__main__":
    main()
