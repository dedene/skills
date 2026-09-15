#!/usr/bin/env python3
"""Compare canonical skills with installed copies; apply only a reviewed hash plan."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile


IGNORED = {'.git', '__pycache__', '.DS_Store'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_file(path):
    if path.is_symlink():
        raise ValueError(f'Symlink file is unsupported: {path}')
    if path.exists() and not path.is_file():
        raise ValueError(f'Expected file: {path}')
    return path.read_bytes() if path.exists() else None


def checksum(data):
    return None if data is None else digest(data)


def roots(source, target):
    source, target = Path(source), Path(target)
    if not source.is_absolute() or not target.is_absolute():
        raise ValueError('Skill roots must be absolute')
    source, target = source.resolve(), target.resolve()
    if not source.is_dir():
        raise ValueError(f'Missing source directory: {source}')
    if target.exists() and not target.is_dir():
        raise ValueError(f'Expected target directory: {target}')
    if source != target and (source in target.parents or target in source.parents):
        raise ValueError(f'Overlapping skill roots: {source}, {target}')
    return source, target


def child(root, relative):
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or '..' in rel.parts:
        raise ValueError(f'Unsafe relative path: {relative}')
    result = root / rel
    for item in [result, *result.parents]:
        if item == root:
            break
        if item.is_symlink():
            raise ValueError(f'Symlink within skill: {item}')
        if item != result and item.exists() and not item.is_dir():
            raise ValueError(f'Expected parent directory: {item}')
    return result


def build_plan(manifest):
    changes, seen, source_roots, target_roots = [], set(), [], []
    entries = json.loads(Path(manifest).read_text())
    for entry in entries:
        for target in entry['targets']:
            source, target = roots(entry['source'], target)
            source_roots.append(source)
            if source == target:
                continue
            target_roots.append(target)
            for file in sorted(source.rglob('*')):
                rel = file.relative_to(source)
                if any(p in IGNORED for p in rel.parts) or file.suffix == '.pyc':
                    continue
                if file.is_symlink():
                    raise ValueError(f'Symlink within source: {file}')
                if not file.is_file():
                    continue
                destination = child(target, str(rel))
                if destination in seen:
                    raise ValueError(f'Duplicate destination: {destination}')
                seen.add(destination)
                before, after = read_file(destination), file.read_bytes()
                if before != after:
                    changes.append(dict(source_root=str(source), target_root=str(target),
                                        relative=str(rel), source_sha256=digest(after),
                                        target_sha256=checksum(before)))
    for target in target_roots:
        for source in source_roots:
            if target == source or target in source.parents or source in target.parents:
                raise ValueError(f'Target overlaps a canonical source: {target}')
    return {'version': 1, 'changes': changes}


def apply_plan(plan):
    if plan.get('version') != 1:
        raise ValueError('Unsupported plan version')
    pending, seen, all_roots, source_roots, target_roots = [], set(), [], [], []
    for change in plan['changes']:
        source, target = roots(change['source_root'], change['target_root'])
        if source == target:
            raise ValueError('Plan targets its canonical source')
        all_roots.extend([source, target])
        source_roots.append(source)
        target_roots.append(target)
        src, dst = child(source, change['relative']), child(target, change['relative'])
        if dst in seen:
            raise ValueError(f'Duplicate destination: {dst}')
        seen.add(dst)
        after, before = read_file(src), read_file(dst)
        if after is None or checksum(after) != change['source_sha256']:
            raise ValueError(f'Source changed since plan: {src}')
        if checksum(before) != change['target_sha256']:
            raise ValueError(f'Destination changed since plan: {dst}')
        pending.append((src, dst, after, before))
    for target in target_roots:
        if any(target == source or target in source.parents or source in target.parents
               for source in source_roots):
            raise ValueError(f'Target overlaps a canonical source: {target}')
    for src, dst, _, _ in pending:
        if any(dst == other or dst in other.parents or other in dst.parents
               for other, _, _, _ in pending):
            raise ValueError(f'Destination overlaps a source: {dst}')
        if any(dst != other and (dst in other.parents or other in dst.parents)
               for _, other, _, _ in pending):
            raise ValueError(f'Overlapping destinations: {dst}')
    if not pending:
        return None
    backup_parent = Path(tempfile.gettempdir()).resolve()
    if any(backup_parent == root or root in backup_parent.parents for root in all_roots):
        raise ValueError('Temporary backup directory is inside a skill root')
    backup = Path(tempfile.mkdtemp(prefix='skill-sync-backup-', dir=backup_parent))
    index = []
    for number, (_, dst, _, before) in enumerate(pending):
        name = str(number)
        if before is not None:
            (backup / name).write_bytes(before)
        index.append({'destination': str(dst), 'backup': name if before is not None else None})
    (backup / 'index.json').write_text(json.dumps(index, indent=2) + '\n')
    for _, dst, after, _ in pending:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(after)
    return backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', default='config/skill-sources.json')
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--check', action='store_true', help='Report drift (default); exit 1 if changed')
    action.add_argument('--plan', metavar='FILE', help='Write a reviewable JSON plan; do not sync')
    action.add_argument('--apply', metavar='PLAN', help='Verify all hashes, back up, then apply plan')
    args = parser.parse_args()
    try:
        if args.apply:
            backup = apply_plan(json.loads(Path(args.apply).read_text()))
            print(f'Applied plan; backup: {backup}' if backup else 'No changes')
            return 0
        plan = build_plan(args.manifest)
        if args.plan:
            output = Path(args.plan).resolve()
            for entry in json.loads(Path(args.manifest).read_text()):
                for directory in [entry['source'], *entry['targets']]:
                    root = Path(directory).resolve()
                    if output == root or root in output.parents:
                        raise ValueError('Plan output must be outside skill directories')
            if output.exists():
                raise ValueError(f'Plan file already exists: {output}')
            output.write_text(json.dumps(plan, indent=2) + '\n')
        for change in plan['changes']:
            print(str(Path(change['target_root']) / change['relative']))
        print(f"{len(plan['changes'])} changed files")
        return 0 if args.plan or not plan['changes'] else 1
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
