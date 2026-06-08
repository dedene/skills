#!/usr/bin/env python3
"""Validate the basic artifact contract for an Ultracode workflow run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


GitContext = tuple[Path, Path]


REQUIRED_FILES = [
    "plan.md",
    "orchestration.md",
    "state.json",
    "integration.md",
    "final-report.md",
]

REQUIRED_DIRS = ["packets", "results"]
ALLOWED_STATUSES = {"planning", "delegating", "integrating", "verifying", "complete", "blocked", "cancelled"}
TERMINAL_STATUSES = {"complete", "blocked", "cancelled"}
CLOSED_RESOURCE_STATUSES = {"closed", "released", "stopped", "removed", "cleaned", "handed-off"}


def has_non_placeholder_content(text: str, headings: list[str]) -> bool:
    for heading in headings:
        marker = f"## {heading}"
        if marker not in text:
            return False
    return True


def section_body(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start == -1:
        return ""
    body_start = text.find("\n", start)
    if body_start == -1:
        return ""
    next_heading = text.find("\n## ", body_start + 1)
    if next_heading == -1:
        return text[body_start:].strip()
    return text[body_start:next_heading].strip()


def has_meaningful_section_body(text: str, heading: str) -> bool:
    body = section_body(text, heading)
    if not body:
        return False

    placeholder_lines = {"-", "- [ ]", "todo", "tbd", "n/a"}
    meaningful_lines = [
        line.strip()
        for line in body.splitlines()
        if line.strip() and line.strip().lower() not in placeholder_lines
    ]
    return bool(meaningful_lines)


def git_context(root: Path) -> GitContext | None:
    for candidate in (root, *root.parents):
        dot_git = candidate / ".git"
        if dot_git.is_dir():
            return candidate, dot_git

        if dot_git.is_file():
            content = dot_git.read_text(encoding="utf-8", errors="replace").strip()
            prefix = "gitdir:"
            if content.lower().startswith(prefix):
                git_dir = Path(content[len(prefix) :].strip())
                if not git_dir.is_absolute():
                    git_dir = (candidate / git_dir).resolve()
                return candidate, git_dir

    return None


def workflow_exclude_pattern(root: Path, worktree_root: Path) -> str:
    workflow_dir = (root / ".workflow").resolve()
    try:
        relative = workflow_dir.relative_to(worktree_root.resolve())
    except ValueError:
        return ".workflow/"
    return f"{relative.as_posix().rstrip('/')}/"


def ignore_patterns(root: Path) -> tuple[set[str], str] | None:
    context = git_context(root)
    if context is None:
        return None

    worktree_root, git_dir = context
    patterns: set[str] = set()
    pattern = workflow_exclude_pattern(root, worktree_root)

    ignore_files = [git_dir / "info" / "exclude"]
    worktree_gitignore = worktree_root / ".gitignore"
    root_gitignore = root / ".gitignore"
    ignore_files.append(worktree_gitignore)
    if root_gitignore != worktree_gitignore:
        ignore_files.append(root_gitignore)

    for ignore_file in ignore_files:
        if ignore_file.exists():
            patterns.update(
                line.strip()
                for line in ignore_file.read_text(encoding="utf-8", errors="replace").splitlines()
                if line.strip() and not line.lstrip().startswith("#")
            )

    return patterns, pattern


def workflow_is_git_excluded(root: Path) -> bool | None:
    result = ignore_patterns(root)
    if result is None:
        return None
    patterns, expected_pattern = result
    workflow_patterns = {
        ".workflow/",
        ".workflow",
        ".workflow/**",
        ".workflow/*",
        "**/.workflow/",
        "**/.workflow/**",
        "**/.workflow/*",
        "/.workflow/",
        "/.workflow",
        expected_pattern,
        f"/{expected_pattern}",
        f"{expected_pattern}**",
        f"{expected_pattern}*",
        f"/{expected_pattern}**",
        f"/{expected_pattern}*",
        expected_pattern.rstrip("/"),
    }
    return bool(patterns & workflow_patterns)


def inferred_root_from_run_dir(run_dir: Path) -> Path:
    try:
        if run_dir.parent.name == "ultracode" and run_dir.parent.parent.name == ".workflow":
            return run_dir.parent.parent.parent
    except IndexError:
        pass
    return run_dir


def resolve_state_root(run_dir: Path, state: dict) -> Path:
    inferred_root = inferred_root_from_run_dir(run_dir)
    root_value = state.get("root")
    if not root_value:
        return inferred_root

    root = Path(str(root_value)).expanduser()
    if root.is_absolute():
        return root
    return (inferred_root / root).resolve()


def add_problem(strict: bool, warnings: list[str], errors: list[str], message: str) -> None:
    if strict:
        errors.append(message)
    else:
        warnings.append(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Ultracode workflow run directory.")
    parser.add_argument("--strict", action="store_true", help="Fail on incomplete final handoff fields and live resources")
    parser.add_argument("run_dir", help="Path to .workflow/ultracode/<run-id>")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not run_dir.exists():
        errors.append(f"Run directory does not exist: {run_dir}")
    elif not run_dir.is_dir():
        errors.append(f"Run path is not a directory: {run_dir}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    for rel in REQUIRED_FILES:
        path = run_dir / rel
        if not path.is_file():
            errors.append(f"Missing required file: {rel}")
        elif path.stat().st_size == 0:
            errors.append(f"Required file is empty: {rel}")

    for rel in REQUIRED_DIRS:
        path = run_dir / rel
        if not path.is_dir():
            errors.append(f"Missing required directory: {rel}")

    state_path = run_dir / "state.json"
    state: dict = {}
    if state_path.is_file():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"state.json is invalid JSON: {exc}")
            state = {}

        status = state.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"state.json status must be one of {sorted(ALLOWED_STATUSES)}")

        if not state.get("runId"):
            errors.append("state.json missing runId")
        if not state.get("title"):
            errors.append("state.json missing title")
        if not isinstance(state.get("packets", []), list):
            errors.append("state.json packets must be a list")
        if state.get("checkInIntervalMinutes") != 10:
            add_problem(args.strict, warnings, errors, "state.json checkInIntervalMinutes should be 10")
        if not isinstance(state.get("checkIns"), list):
            add_problem(args.strict, warnings, errors, "state.json checkIns must be a list")
        if not isinstance(state.get("resources"), list):
            add_problem(args.strict, warnings, errors, "state.json resources must be a list")

        root = resolve_state_root(run_dir, state)
        ignored = workflow_is_git_excluded(root)
        if ignored is False:
            add_problem(args.strict, warnings, errors, ".workflow/ is not ignored by Git metadata")

        resources = state.get("resources", [])
        if isinstance(resources, list):
            active_resources = [
                resource
                for resource in resources
                if isinstance(resource, dict)
                and resource.get("status") not in CLOSED_RESOURCE_STATUSES
            ]
            if active_resources:
                message = f"{len(active_resources)} resource(s) still active or unclosed in state.json"
                if status in TERMINAL_STATUSES:
                    add_problem(args.strict, warnings, errors, message)
                else:
                    warnings.append(message)

    plan_path = run_dir / "plan.md"
    if plan_path.is_file():
        plan_text = plan_path.read_text(encoding="utf-8")
        if not has_non_placeholder_content(plan_text, ["Goal", "Success Criteria", "Verification Gates"]):
            errors.append("plan.md missing required sections")
        if "- [ ] " in plan_text:
            add_problem(args.strict, warnings, errors, "plan.md still contains empty checklist items")

    orchestration_path = run_dir / "orchestration.md"
    if orchestration_path.is_file():
        orchestration_text = orchestration_path.read_text(encoding="utf-8")
        if not has_non_placeholder_content(orchestration_text, ["Mode", "Host Capabilities", "Work Packets"]):
            errors.append("orchestration.md missing required sections")
        if not has_non_placeholder_content(orchestration_text, ["Check-In Cadence", "Resource Plan"]):
            add_problem(args.strict, warnings, errors, "orchestration.md missing check-in or resource sections")

    packet_files = sorted((run_dir / "packets").glob("*.md")) if (run_dir / "packets").is_dir() else []
    result_files = sorted((run_dir / "results").glob("*.md")) if (run_dir / "results").is_dir() else []
    if packet_files and len(result_files) < len(packet_files):
        warnings.append(f"{len(packet_files)} packet file(s), but only {len(result_files)} result file(s)")

    final_path = run_dir / "final-report.md"
    if final_path.is_file():
        final_text = final_path.read_text(encoding="utf-8")
        if not has_non_placeholder_content(final_text, ["Outcome", "Verification Evidence", "Remaining Risks"]):
            errors.append("final-report.md missing required sections")
        if not has_non_placeholder_content(final_text, ["Resource Cleanup"]):
            add_problem(args.strict, warnings, errors, "final-report.md missing Resource Cleanup section")
        if not has_meaningful_section_body(final_text, "Outcome"):
            add_problem(args.strict, warnings, errors, "final-report.md outcome appears empty")
        if not has_meaningful_section_body(final_text, "Verification Evidence"):
            add_problem(args.strict, warnings, errors, "final-report.md verification evidence appears empty")
        if not has_meaningful_section_body(final_text, "Resource Cleanup"):
            add_problem(args.strict, warnings, errors, "final-report.md resource cleanup appears empty")
        if not has_meaningful_section_body(final_text, "Remaining Risks"):
            add_problem(args.strict, warnings, errors, "final-report.md remaining risks appears empty")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        return 1

    print(f"OK: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
