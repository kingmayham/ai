"""Smart AI coding assistant core module with basic code-generation support."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import difflib
import re
from typing import Iterable, List, Sequence


INTENT_KEYWORDS = {
    "bugfix": ["fix", "bug", "issue", "error", "broken", "crash"],
    "feature": ["add", "implement", "create", "build", "support"],
    "refactor": ["refactor", "cleanup", "restructure", "simplify"],
    "tests": ["test", "coverage", "unit test", "integration test"],
    "docs": ["document", "docs", "readme", "comment"],
    "performance": ["optimize", "performance", "faster", "latency"],
}


@dataclass
class FileEdit:
    path: str
    content: str


@dataclass
class AssistantResult:
    task: str
    intent: str
    relevant_files: List[str]
    plan: List[str]
    commands: List[str]
    response: str


class SmartCodingAssistant:
    """Repository-aware assistant that can suggest and apply simple code edits."""

    def analyze_task(self, task: str) -> str:
        lowered = task.lower()
        scores = {
            intent: sum(1 for kw in kws if kw in lowered)
            for intent, kws in INTENT_KEYWORDS.items()
        }
        best_intent = max(scores, key=scores.get)
        return best_intent if scores[best_intent] > 0 else "general"

    def gather_repo_files(self, repo_path: Path, max_files: int = 300) -> List[str]:
        exts = {
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".md",
            ".json",
            ".toml",
            ".yaml",
            ".yml",
            ".html",
            ".css",
        }
        files: List[str] = []
        for path in repo_path.rglob("*"):
            if (
                path.is_file()
                and path.suffix in exts
                and ".git" not in path.parts
                and "__pycache__" not in path.parts
            ):
                files.append(str(path.relative_to(repo_path)))
                if len(files) >= max_files:
                    break
        return sorted(files)

    def pick_relevant_files(self, task: str, files: Sequence[str], limit: int = 8) -> List[str]:
        tokens = [t for t in re.split(r"\W+", task.lower()) if len(t) > 2]
        scored = []
        for f in files:
            lowered = f.lower()
            score = sum(1 for t in tokens if t in lowered)
            if score > 0:
                scored.append((score, f))
        scored.sort(key=lambda x: (-x[0], x[1]))
        picked = [name for _, name in scored[:limit]]
        if picked:
            return picked
        return list(files[:limit])

    def build_plan(self, task: str, intent: str, relevant_files: Sequence[str]) -> List[str]:
        base = [
            f"Clarify acceptance criteria for: {task.strip()}",
            "Inspect relevant files and current behavior before changing code.",
        ]

        intent_steps = {
            "bugfix": "Reproduce the issue and implement the smallest safe fix.",
            "feature": "Implement the feature behind clear interfaces and update integration points.",
            "refactor": "Refactor incrementally while preserving behavior.",
            "tests": "Add/adjust focused tests that validate target behavior.",
            "docs": "Update documentation and examples to reflect current behavior.",
            "performance": "Measure baseline performance and optimize the main bottleneck first.",
            "general": "Implement changes in small, reviewable commits.",
        }

        base.append(intent_steps[intent])

        if relevant_files:
            base.append("Touch these likely files first: " + ", ".join(relevant_files[:4]))

        base.extend(
            [
                "Generate patch proposal and review before applying.",
                "Run tests/lint checks and fix regressions.",
                "Summarize changes and follow-up improvements.",
            ]
        )
        return base

    def suggest_commands(self, intent: str, relevant_files: Sequence[str]) -> List[str]:
        cmds = ["git status --short", "rg --files"]

        if relevant_files:
            quoted = " ".join(relevant_files[:5])
            cmds.append(f"sed -n '1,200p' {quoted}")

        intent_cmds = {
            "bugfix": ["python -m unittest discover -s tests -p 'test_*.py'"],
            "feature": ["python -m unittest discover -s tests -p 'test_*.py'"],
            "refactor": ["python -m unittest discover -s tests -p 'test_*.py'"],
            "tests": ["python -m unittest discover -s tests -p 'test_*.py'"],
            "docs": ["python -m unittest discover -s tests -p 'test_*.py' || true"],
            "performance": ["python -m timeit 'pass'"],
            "general": ["python -m unittest discover -s tests -p 'test_*.py' || true"],
        }
        cmds.extend(intent_cmds[intent])
        return cmds

    def generate_file_edits(
        self,
        task: str,
        intent: str,
        relevant_files: Sequence[str],
        repo_path: Path,
    ) -> List[FileEdit]:
        """Generate conservative code edits for common tasks.

        Current behavior:
        - If task asks to add a Python function and a likely .py file exists, append a
          function stub with TODO guidance.
        - If task asks for docs, append a checklist entry to README.md.
        """
        edits: List[FileEdit] = []
        lowered = task.lower()

        if "function" in lowered and intent in {"feature", "general", "refactor"}:
            target = next((f for f in relevant_files if f.endswith(".py")), None)
            if target:
                fn_name = self._extract_function_name(task)
                file_path = repo_path / target
                original = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
                if f"def {fn_name}(" not in original:
                    addition = (
                        "\n\n"
                        f"def {fn_name}(*args, **kwargs):\n"
                        f"    \"\"\"Auto-generated stub for task: {task.strip()}\"\"\"\n"
                        "    # TODO: implement logic\n"
                        "    raise NotImplementedError('Implement this function')\n"
                    )
                    edits.append(FileEdit(path=target, content=original.rstrip("\n") + addition + "\n"))

        if intent == "docs":
            readme = repo_path / "README.md"
            if readme.exists():
                text = readme.read_text(encoding="utf-8")
                marker = f"- [ ] {task.strip()}"
                if marker not in text:
                    edits.append(FileEdit(path="README.md", content=text.rstrip("\n") + f"\n\n## TODO\n{marker}\n"))

        return edits

    def build_patch(self, repo_path: Path, edits: Sequence[FileEdit]) -> str:
        chunks: List[str] = []
        for edit in edits:
            path = repo_path / edit.path
            before = path.read_text(encoding="utf-8").splitlines(keepends=True) if path.exists() else []
            after = edit.content.splitlines(keepends=True)
            diff = difflib.unified_diff(
                before,
                after,
                fromfile=edit.path,
                tofile=edit.path,
            )
            chunks.append("".join(diff))
        return "\n".join(chunk for chunk in chunks if chunk)

    def apply_edits(self, repo_path: Path, edits: Sequence[FileEdit]) -> List[str]:
        changed: List[str] = []
        for edit in edits:
            path = repo_path / edit.path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(edit.content, encoding="utf-8")
            changed.append(edit.path)
        return changed

    def draft_response(
        self,
        task: str,
        intent: str,
        plan: Sequence[str],
        commands: Sequence[str],
        relevant_files: Sequence[str],
        patch_preview: str = "",
    ) -> str:
        files_line = ", ".join(relevant_files) if relevant_files else "(none detected)"
        message = (
            f"Intent: {intent}.\n"
            f"Task: {task.strip()}\n"
            f"Likely files: {files_line}\n"
            "Plan:\n- "
            + "\n- ".join(plan)
            + "\nRecommended commands:\n- "
            + "\n- ".join(commands)
        )
        if patch_preview:
            message += "\nPatch preview:\n" + patch_preview
        return message

    def run(
        self,
        task: str,
        repo_path: Path | None = None,
        files: Iterable[str] | None = None,
        apply: bool = False,
    ) -> AssistantResult:
        repo = repo_path or Path.cwd()
        intent = self.analyze_task(task)

        if files is not None:
            discovered = sorted(set(files))
        else:
            discovered = self.gather_repo_files(repo)

        relevant = self.pick_relevant_files(task, discovered)
        plan = self.build_plan(task, intent, relevant)
        commands = self.suggest_commands(intent, relevant)

        edits = self.generate_file_edits(task, intent, relevant, repo)
        patch = self.build_patch(repo, edits) if edits else ""
        if apply and edits:
            changed = self.apply_edits(repo, edits)
            commands = [f"# Applied edits to: {', '.join(changed)}"] + commands

        response = self.draft_response(task, intent, plan, commands, relevant, patch)

        return AssistantResult(
            task=task,
            intent=intent,
            relevant_files=relevant,
            plan=plan,
            commands=commands,
            response=response,
        )

    @staticmethod
    def _extract_function_name(task: str) -> str:
        match = re.search(r"function\s+([a-zA-Z_][a-zA-Z0-9_]*)", task)
        if match:
            return match.group(1)
        return "generated_function"
