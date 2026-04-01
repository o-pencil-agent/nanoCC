"""
agent.py — The agent loop.

This is the core of nanoCC. It implements a simple loop:

    1. Send messages to the LLM (with tool definitions)
    2. If the LLM responds with text, print it
    3. If the LLM responds with tool_use, execute the tool and append the result
    4. Repeat until the LLM stops calling tools

This is the same pattern used by Claude Code, Codex CLI, and every other
coding agent — just stripped to the essentials.
"""

import sys
import litellm
from .tools import get_tool_schemas, execute_tool

# Suppress litellm's noisy logging
litellm.suppress_debug_info = True

# ---------------------------------------------------------------------------
# System prompt — tells the LLM how to behave as a coding agent
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a coding assistant with access to tools for reading, writing, and \
searching files, as well as executing shell commands. Use tools to explore \
the codebase and make changes as requested.

Guidelines:
- Read files before editing them.
- Use Glob/Grep to find files instead of guessing paths.
- Make minimal, targeted changes.
- Explain what you're doing briefly.
"""

# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------


def run_agent_loop(
    user_message: str,
    messages: list[dict] | None = None,
    model: str = "claude-sonnet-4-20250514",
    max_turns: int = 50,
) -> list[dict]:
    """
    Run the agent loop with one user message.

    Args:
        user_message: The user's input text.
        messages: Conversation history (mutated in place). Starts empty if None.
        model: LiteLLM model identifier.
        max_turns: Safety limit to prevent infinite loops.

    Returns:
        The updated messages list.
    """
    if messages is None:
        messages = []

    messages.append({"role": "user", "content": user_message})
    tools = get_tool_schemas()

    for _ in range(max_turns):
        # --- Step 1: Call the LLM -------------------------------------------
        response = litellm.completion(
            model=model,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            tools=[{"type": "function", "function": t} for t in tools],
            stream=True,
        )

        # --- Step 2: Process the streamed response --------------------------
        assistant_text = ""
        tool_calls = []
        current_tool_call = None

        for chunk in response:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta is None:
                continue

            # Stream text to terminal
            if delta.content:
                sys.stdout.write(delta.content)
                sys.stdout.flush()
                assistant_text += delta.content

            # Accumulate tool calls
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    if tc.id:
                        # New tool call
                        current_tool_call = {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.function.name or "", "arguments": ""},
                        }
                        tool_calls.append(current_tool_call)
                    if current_tool_call and tc.function and tc.function.arguments:
                        current_tool_call["function"]["arguments"] += tc.function.arguments

        if assistant_text:
            print()  # newline after streamed text

        # Build the assistant message
        assistant_msg: dict = {"role": "assistant", "content": assistant_text or None}
        if tool_calls:
            assistant_msg["tool_calls"] = tool_calls
        messages.append(assistant_msg)

        # --- Step 3: If no tool calls, we're done --------------------------
        if not tool_calls:
            break

        # --- Step 4: Execute tools and append results ----------------------
        import json

        for tc in tool_calls:
            name = tc["function"]["name"]
            try:
                args = json.loads(tc["function"]["arguments"])
            except json.JSONDecodeError:
                args = {}

            print(f"\n--- Tool: {name} ---")
            result = execute_tool(name, args)

            # Show a preview of the result
            preview = result[:500] + ("..." if len(result) > 500 else "")
            print(preview)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                }
            )

    return messages
