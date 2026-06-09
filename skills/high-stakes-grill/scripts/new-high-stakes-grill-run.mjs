#!/usr/bin/env node

import { appendFile, mkdir, readFile, stat, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const WORKFLOW_EXCLUDE = '.workflow/';

export function slugifyTitle(title) {
  const slug = String(title || '')
    .toLowerCase()
    .replace(/['"]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 48)
    .replace(/-+$/g, '');

  return slug || 'grill';
}

function formatTimestamp(date) {
  const pad = (value) => String(value).padStart(2, '0');

  return [
    date.getUTCFullYear(),
    pad(date.getUTCMonth() + 1),
    pad(date.getUTCDate()),
    '-',
    pad(date.getUTCHours()),
    pad(date.getUTCMinutes()),
    pad(date.getUTCSeconds()),
  ].join('');
}

function toPosixPath(filePath) {
  return filePath.split(path.sep).join('/');
}

function expandUser(value) {
  if (value === '~') {
    return os.homedir();
  }
  if (value.startsWith('~/')) {
    return path.join(os.homedir(), value.slice(2));
  }
  return value;
}

async function ensureWorkflowExcluded(root) {
  const context = await gitContext(root);
  if (!context) {
    return { changed: false, available: false, path: null, pattern: null, status: 'not-git' };
  }

  const excludePath = path.join(context.gitDir, 'info', 'exclude');
  const pattern = workflowExcludePattern(root, context.worktreeRoot);
  await mkdir(path.dirname(excludePath), { recursive: true });

  let existing = '';
  if (await pathType(excludePath)) {
    existing = await readFile(excludePath, 'utf8');
  }

  const patterns = new Set(
    existing
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter((line) => line && !line.startsWith('#')),
  );

  if (patterns.has(pattern) || patterns.has(pattern.replace(/\/$/g, ''))) {
    return { changed: false, available: true, path: excludePath, pattern, status: 'already-excluded' };
  }

  const separator = existing.endsWith('\n') || existing.length === 0 ? '' : '\n';
  await appendFile(excludePath, `${separator}${pattern}\n`, 'utf8');

  return { changed: true, available: true, path: excludePath, pattern, status: 'added-local-exclude' };
}

async function pathType(candidate) {
  try {
    const details = await stat(candidate);
    if (details.isDirectory()) return 'directory';
    if (details.isFile()) return 'file';
    return 'other';
  } catch (error) {
    if (error.code === 'ENOENT') return null;
    throw error;
  }
}

async function gitContext(root) {
  let candidate = path.resolve(root);

  while (true) {
    const dotGit = path.join(candidate, '.git');
    const type = await pathType(dotGit);

    if (type === 'directory') {
      return { worktreeRoot: candidate, gitDir: dotGit };
    }

    if (type === 'file') {
      const content = (await readFile(dotGit, 'utf8')).trim();
      const prefix = 'gitdir:';
      if (content.toLowerCase().startsWith(prefix)) {
        let gitDir = content.slice(prefix.length).trim();
        if (!path.isAbsolute(gitDir)) {
          gitDir = path.resolve(candidate, gitDir);
        }
        return { worktreeRoot: candidate, gitDir };
      }
    }

    const parent = path.dirname(candidate);
    if (parent === candidate) {
      return null;
    }
    candidate = parent;
  }
}

function workflowExcludePattern(root, worktreeRoot) {
  const workflowDir = path.resolve(root, '.workflow');
  const relative = path.relative(path.resolve(worktreeRoot), workflowDir);

  if (!relative || relative.startsWith('..') || path.isAbsolute(relative)) {
    return WORKFLOW_EXCLUDE;
  }

  return `${toPosixPath(relative).replace(/\/+$/g, '')}/`;
}

function createDecisionLog({ title, runId, createdAt }) {
  return `# High-Stakes Grill Decision Log

- Run: ${runId}
- Goal: ${title}
- Created: ${createdAt.toISOString()}

## Context Capsule

- Goal: ${title}
- Current state: Not started
- Constraints: None recorded yet
- Assumptions: None recorded yet
- Open questions: None recorded yet

## Decision Ledger

Append one entry after every question:

\`\`\`markdown
### Decision N: <question>

- Mode: auto | human
- Chosen answer: <A/B/C or short answer>
- Reason: <one-line rationale>
- Evidence: <repo path, command, source, or "user answer">
- Downstream implications: <what this unlocks or changes>
\`\`\`

## Final Recap

Fill this when the interview closes:

- Auto decisions:
- Human decisions:
- Remaining assumptions:
- Override candidates:
`;
}

export async function createHighStakesGrillRun({
  root = '.',
  title = 'grill',
  ensureGitExclude = true,
  now = new Date(),
} = {}) {
  const absoluteRoot = path.resolve(expandUser(root));
  const runId = `${formatTimestamp(now)}-${slugifyTitle(title)}`;
  const relativeRunDir = toPosixPath(path.join('.workflow', 'high-stakes-grill', runId));
  const runDir = path.join(absoluteRoot, relativeRunDir);
  const decisionLogPath = path.join(runDir, 'decision-log.md');

  if (await pathType(runDir)) {
    throw new Error(`Run directory already exists: ${runDir}`);
  }

  const exclude = ensureGitExclude
    ? await ensureWorkflowExcluded(absoluteRoot)
    : { changed: false, available: false, path: null };

  await mkdir(path.dirname(runDir), { recursive: true });
  await mkdir(runDir);
  await writeFile(
    decisionLogPath,
    createDecisionLog({ title, runId, createdAt: now }),
    { encoding: 'utf8', flag: 'wx' },
  );

  return {
    runId,
    runDir,
    relativeRunDir,
    decisionLogPath,
    exclude,
  };
}

function usage() {
  return `Create a High-Stakes Grill scratch run.

Usage:
  node new-high-stakes-grill-run.mjs "plan title" [--root <path>] [--no-git-exclude]

Options:
  --root <path>        Project root where .workflow should be created (default: .)
  --no-git-exclude    Do not add .workflow/ to .git/info/exclude
  --help              Show this help
`;
}

function parseArgs(argv) {
  const args = [...argv];
  let root = '.';
  let ensureGitExclude = true;
  const titleParts = [];

  while (args.length > 0) {
    const arg = args.shift();

    if (arg === '--help' || arg === '-h') {
      return { help: true };
    }

    if (arg === '--root') {
      root = args.shift();
      if (!root || root.startsWith('-')) throw new Error('--root requires a path');
      continue;
    }

    if (arg.startsWith('--root=')) {
      root = arg.slice('--root='.length);
      if (!root) throw new Error('--root requires a path');
      continue;
    }

    if (arg === '--no-git-exclude') {
      ensureGitExclude = false;
      continue;
    }

    if (arg.startsWith('--')) {
      throw new Error(`Unknown option: ${arg}`);
    }

    titleParts.push(arg);
  }

  return {
    title: titleParts.join(' ') || 'grill',
    root,
    ensureGitExclude,
  };
}

async function main() {
  const options = parseArgs(process.argv.slice(2));

  if (options.help) {
    process.stdout.write(usage());
    return;
  }

  const result = await createHighStakesGrillRun(options);

  if (result.exclude.available && result.exclude.changed) {
    process.stderr.write(`Added ${WORKFLOW_EXCLUDE} to ${result.exclude.path}\n`);
  } else if (!result.exclude.available && options.ensureGitExclude) {
    process.stderr.write('Warning: root is not a Git checkout; keep .workflow/ out of version control\n');
  }

  process.stdout.write(`${result.decisionLogPath}\n`);
}

const isCli = process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1]);

if (isCli) {
  main().catch((error) => {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  });
}
