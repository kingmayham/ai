"""CLI for the smart AI coding assistant."""

from __future__ import annotations

import argparse
from pathlib import Path

from coding_assistant import SmartCodingAssistant


def main() -> int:
    parser = argparse.ArgumentParser(description="Smart AI coding assistant")
    parser.add_argument("--task", required=True, help="Natural language coding task")
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository path used for file discovery (default: current directory)",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        default=None,
        help="Optional explicit file list (overrides --repo scanning)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply generated edits directly to files (default: preview only)",
    )

    args = parser.parse_args()

    assistant = SmartCodingAssistant()
    result = assistant.run(
        task=args.task,
        repo_path=Path(args.repo),
        files=args.files,
        apply=args.apply,
    )

    print("=== SMART AI CODING ASSISTANT ===")
    print(f"Task: {result.task}")
    print(f"Intent: {result.intent}")
    print("Relevant files:")
    for f in result.relevant_files:
        print(f"- {f}")
    print("Plan:")
    for step in result.plan:
        print(f"- {step}")
    print("Suggested commands:")
    for cmd in result.commands:
        print(f"- {cmd}")
    print("\nResponse draft:\n")
    print(result.response)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
