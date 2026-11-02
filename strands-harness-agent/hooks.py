"""Loop-tracing hook.

Hooks are the harness's feedback/observability seam: callbacks that fire at
lifecycle points during a run. This one just makes the agent loop visible by
printing every tool call before and after it executes, so you can watch the
model reason -> act -> observe in real time.

The same seam is where real harness engineering happens: a hook can validate a
tool call before it runs, retry a flaky one, cap how many times a tool fires, or
require human approval before a destructive action. See the Strands hooks docs:
https://strandsagents.com/docs/user-guide/concepts/agents/hooks/
"""

from strands.hooks import (
    AfterToolCallEvent,
    BeforeToolCallEvent,
    HookProvider,
    HookRegistry,
)


def _summarize_input(tool_use: dict) -> str:
    """Render a short, one-line summary of a tool's input for logging."""
    tool_input = tool_use.get("input", {}) or {}
    if "path" in tool_input:
        return str(tool_input["path"])
    if "command" in tool_input:
        command = str(tool_input["command"]).replace("\n", " ")
        return command[:70] + ("..." if len(command) > 70 else "")
    # Fall back to the first key so every tool prints *something* useful.
    for key, value in tool_input.items():
        return f"{key}={str(value)[:60]}"
    return ""


class LoopTracer(HookProvider):
    """Prints each tool call so the agent loop is visible in the terminal."""

    def register_hooks(self, registry: HookRegistry, **kwargs) -> None:
        registry.add_callback(BeforeToolCallEvent, self.before_tool)
        registry.add_callback(AfterToolCallEvent, self.after_tool)

    def before_tool(self, event: BeforeToolCallEvent) -> None:
        name = event.tool_use["name"]
        detail = _summarize_input(event.tool_use)
        print(f"  -> calling {name}: {detail}")

    def after_tool(self, event: AfterToolCallEvent) -> None:
        name = event.tool_use["name"]
        status = "error" if event.exception else event.result.get("status", "ok")
        print(f"  <- {name} finished ({status})")
