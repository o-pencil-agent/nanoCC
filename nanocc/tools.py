"""
tools.py — Tool definitions and execution.

Each tool is a dict with name, description, input_schema (JSON Schema),
and an execute() function. The agent calls tools by name; this module
routes the call and returns a result string.
"""

import os
import glob as globlib
import subprocess
from typing import Any

# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

TOOLS: list[dict] = []


def _register(name: str, description: str, schema: dict):
    """Decorator that registers a function as a tool."""

    def decorator(fn):
        TOOLS.append(
            {
                "name": name,
                "description": description,
                "input_schema": {"type": "object", **schema},
                "execute": fn,
            }
        )
        return fn

    return decorator


# ---------------------------------------------------------------------------
# Core tools (6 tools — enough to be a useful coding agent)
# ---------------------------------------------------------------------------


@_register(
    "Read",
    "Read a file and return its contents.",
    {
        "properties": {
            "file_path": {"type": "string", "description": "Absolute or relative file path"},
            "offset": {"type": "integer", "description": "Start line (0-based)", "default": 0},
            "limit": {"type": "integer", "description": "Max lines to read", "default": 2000},
        },
        "required": ["file_path"],
    },
)
def read_file(file_path: str, offset: int = 0, limit: int = 2000, **_) -> str:
    with open(file_path, "r") as f:
        lines = f.readlines()
    selected = lines[offset : offset + limit]
    return "".join(f"{offset + i + 1}\t{line}" for i, line in enumerate(selected))


@_register(
    "Write",
    "Create or overwrite a file with the given content.",
    {
        "properties": {
            "file_path": {"type": "string", "description": "File path to write"},
            "content": {"type": "string", "description": "Content to write"},
        },
        "required": ["file_path", "content"],
    },
)
def write_file(file_path: str, content: str, **_) -> str:
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
    with open(file_path, "w") as f:
        f.write(content)
    return f"Wrote {len(content)} bytes to {file_path}"


@_register(
    "Edit",
    "Replace an exact string in a file with a new string.",
    {
        "properties": {
            "file_path": {"type": "string", "description": "File path"},
            "old_string": {"type": "string", "description": "Exact text to find"},
            "new_string": {"type": "string", "description": "Replacement text"},
        },
        "required": ["file_path", "old_string", "new_string"],
    },
)
def edit_file(file_path: str, old_string: str, new_string: str, **_) -> str:
    with open(file_path, "r") as f:
        content = f.read()
    if old_string not in content:
        return f"ERROR: old_string not found in {file_path}"
    if content.count(old_string) > 1:
        return f"ERROR: old_string matches {content.count(old_string)} locations. Be more specific."
    content = content.replace(old_string, new_string, 1)
    with open(file_path, "w") as f:
        f.write(content)
    return f"Edited {file_path}"


@_register(
    "Bash",
    "Execute a shell command and return stdout + stderr.",
    {
        "properties": {
            "command": {"type": "string", "description": "Shell command to execute"},
            "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30},
        },
        "required": ["command"],
    },
)
def bash(command: str, timeout: int = 30, **_) -> str:
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout + result.stderr
        return output[:50000] or "(no output)"
    except subprocess.TimeoutExpired:
        return f"ERROR: Command timed out after {timeout}s"


@_register(
    "Glob",
    "Find files matching a glob pattern.",
    {
        "properties": {
            "pattern": {"type": "string", "description": "Glob pattern (e.g. '**/*.py')"},
            "path": {"type": "string", "description": "Directory to search in", "default": "."},
        },
        "required": ["pattern"],
    },
)
def glob_search(pattern: str, path: str = ".", **_) -> str:
    matches = sorted(globlib.glob(os.path.join(path, pattern), recursive=True))
    if not matches:
        return "No files matched."
    return "\n".join(matches[:100])


@_register(
    "Grep",
    "Search file contents for a regex pattern using grep.",
    {
        "properties": {
            "pattern": {"type": "string", "description": "Regex pattern to search for"},
            "path": {"type": "string", "description": "File or directory to search", "default": "."},
            "include": {"type": "string", "description": "File glob filter (e.g. '*.py')", "default": ""},
        },
        "required": ["pattern"],
    },
)
def grep_search(pattern: str, path: str = ".", include: str = "", **_) -> str:
    cmd = ["grep", "-rn", "--color=never"]
    if include:
        cmd += [f"--include={include}"]
    cmd += [pattern, path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        output = result.stdout
        return output[:50000] or "No matches found."
    except subprocess.TimeoutExpired:
        return "ERROR: grep timed out"


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def get_tool_schemas() -> list[dict]:
    """Return tool schemas in Anthropic API format."""
    return [
        {"name": t["name"], "description": t["description"], "input_schema": t["input_schema"]}
        for t in TOOLS
    ]


def execute_tool(name: str, args: dict[str, Any]) -> str:
    """Execute a tool by name with the given arguments."""
    for tool in TOOLS:
        if tool["name"] == name:
            try:
                return tool["execute"](**args)
            except Exception as e:
                return f"ERROR: {type(e).__name__}: {e}"
    return f"ERROR: Unknown tool '{name}'"
