"""
cli.py — Interactive terminal interface.

Provides a REPL that accepts user input and feeds it to the agent loop.
"""

import sys
import argparse
from .agent import run_agent_loop


def parse_args():
    parser = argparse.ArgumentParser(
        prog="nanocc",
        description="nanoCC — Claude Code in 500 lines of Python.",
    )
    parser.add_argument(
        "-m", "--model",
        default="claude-sonnet-4-20250514",
        help="LiteLLM model identifier (default: claude-sonnet-4-20250514)",
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Initial prompt (if omitted, enters interactive mode)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    model = args.model
    messages = []

    print(f"nanoCC v0.1.0 | model: {model}")
    print("Type your request. Press Ctrl+C to exit.\n")

    # If a prompt was passed as CLI args, run it first
    if args.prompt:
        initial = " ".join(args.prompt)
        print(f"> {initial}\n")
        messages = run_agent_loop(initial, messages, model=model)
        print()

    # Interactive REPL
    try:
        while True:
            try:
                user_input = input("> ").strip()
            except EOFError:
                break

            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "/quit"):
                break

            print()
            messages = run_agent_loop(user_input, messages, model=model)
            print()

    except KeyboardInterrupt:
        print("\nBye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
