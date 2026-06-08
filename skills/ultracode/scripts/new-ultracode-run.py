#!/usr/bin/env python3
"""Create an Ultracode workflow run directory."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


GitContext = tuple[Path, Path]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:48].strip("-") or "workflow"


def write_if_missing(path: Path, content: str) -> None:
    if path.exists():
        raise FileExistsError(f"{path} already exists")
    path.write_text(content, encoding="utf-8")


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


def ensure_workflow_git_excluded(root: Path) -> str:
    context = git_context(root)
    if context is None:
        return "not-git"

    worktree_root, git_dir = context
    exclude_path = git_dir / "info" / "exclude"
    pattern = workflow_exclude_pattern(root, worktree_root)
    exclude_path.parent.mkdir(parents=True, exist_ok=True)
    existing = exclude_path.read_text(encoding="utf-8") if exclude_path.exists() else ""
    patterns = {line.strip() for line in existing.splitlines() if line.strip() and not line.lstrip().startswith("#")}
    if pattern in patterns or pattern.rstrip("/") in patterns:
        return "already-excluded"

    prefix = "" if not existing or existing.endswith("\n") else "\n"
    with exclude_path.open("a", encoding="utf-8") as handle:
        handle.write(f"{prefix}{pattern}\n")
    return "added-local-exclude"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an Ultracode workflow run directory.")
    parser.add_argument("title", help="Short task title")
    parser.add_argument("--root", default=".", help="Project root where .workflow should be created")
    parser.add_argument("--slug", help="Optional slug override")
    parser.add_argument("--mode", choices=["workflow", "delegated", "runner"], default="delegated")
    parser.add_argument("--no-git-exclude", action="store_true", help="Do not add .workflow/ to local Git exclude")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not args.no_git_exclude:
        exclude_status = ensure_workflow_git_excluded(root)
        if exclude_status == "added-local-exclude":
            print("Added workflow artifact path to local Git exclude", file=sys.stderr)
        elif exclude_status == "not-git":
            print("Warning: root is not a Git checkout; keep .workflow/ out of version control", file=sys.stderr)

    now = datetime.now(timezone.utc)
    next_check_in = now + timedelta(minutes=10)
    run_slug = slugify(args.slug or args.title)
    run_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{run_slug}"
    run_dir = root / ".workflow" / "ultracode" / run_id

    if run_dir.exists():
        raise SystemExit(f"Run directory already exists: {run_dir}")

    (run_dir / "packets").mkdir(parents=True)
    (run_dir / "results").mkdir()

    state = {
        "title": args.title,
        "runId": run_id,
        "createdAt": now.isoformat().replace("+00:00", "Z"),
        "status": "planning",
        "mode": args.mode,
        "root": str(root),
        "checkInIntervalMinutes": 10,
        "lastCheckInAt": None,
        "nextCheckInDueAt": next_check_in.isoformat().replace("+00:00", "Z"),
        "checkIns": [],
        "resources": [],
        "packets": [],
        "approvals": [],
        "verification": [],
    }

    write_if_missing(
        run_dir / "state.json",
        json.dumps(state, indent=2) + "\n",
    )
    write_if_missing(
        run_dir / "plan.md",
        f"""# Plan

## Goal

{args.title}

## Success Criteria

- [ ] 

## Non-Goals

- 

## Constraints

- 

## Risks

- 

## Verification Gates

- [ ] 
""",
    )
    write_if_missing(
        run_dir / "orchestration.md",
        f"""# Orchestration

## Mode

{args.mode}

## Host Capabilities

- Native subagents:
- Runner:
- Network:
- Write access:

## Work Packets

| Packet | Owner | Scope | Dependencies | Expected result |
| --- | --- | --- | --- | --- |

## Check-In Cadence

- Interval: 10 minutes
- Last check-in:
- Next check-in: {next_check_in.isoformat().replace("+00:00", "Z")}
- Phase-change updates:

## Resource Plan

| Resource | Owner | Purpose | Cleanup |
| --- | --- | --- | --- |

## Stop Conditions

- 

## Budget

- Workers:
- Time:
- Token/cost limit:
""",
    )
    write_if_missing(
        run_dir / "integration.md",
        """# Integration

## Results Reviewed

- 

## Accepted

- 

## Rejected

- 

## Conflicts Resolved

- 

## Integrated Changes

- 
""",
    )
    write_if_missing(
        run_dir / "final-report.md",
        """# Final Report

## Outcome

## Files Changed

- 

## Verification Evidence

- 

## Resource Cleanup

- 

## Remaining Risks

- 

## Follow-Ups

- 
""",
    )

    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
