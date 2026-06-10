#!/usr/bin/env node
import { appendFile, mkdir, readFile, stat, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';

const VALID_MODES = new Set(['workflow', 'delegated', 'runner']);

function usage() {
  return `Usage: new-ultracode-run.mjs [options] "short task title"

Create an Ultracode workflow run directory.

Options:
  --root <path>          Project root where .workflow should be created (default: .)
  --slug <slug>          Optional slug override
  --mode <mode>          workflow, delegated, or runner (default: delegated)
  --no-git-exclude       Do not add .workflow/ to local Git exclude
  -h, --help             Show this help
`;
}

function parseArgs(argv) {
  const args = {
    root: '.',
    slug: null,
    mode: 'delegated',
    noGitExclude: false,
    title: null,
  };

  const positionals = [];
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === '-h' || arg === '--help') {
      args.help = true;
      continue;
    }

    if (arg === '--no-git-exclude') {
      args.noGitExclude = true;
      continue;
    }

    if (arg.startsWith('--root=')) {
      args.root = arg.slice('--root='.length);
      continue;
    }

    if (arg === '--root') {
      args.root = requireValue(argv, index, arg);
      index += 1;
      continue;
    }

    if (arg.startsWith('--slug=')) {
      args.slug = arg.slice('--slug='.length);
      continue;
    }

    if (arg === '--slug') {
      args.slug = requireValue(argv, index, arg);
      index += 1;
      continue;
    }

    if (arg.startsWith('--mode=')) {
      args.mode = arg.slice('--mode='.length);
      continue;
    }

    if (arg === '--mode') {
      args.mode = requireValue(argv, index, arg);
      index += 1;
      continue;
    }

    if (arg.startsWith('-')) {
      throw new Error(`Unknown option: ${arg}`);
    }

    positionals.push(arg);
  }

  if (positionals.length > 1) {
    throw new Error(`Expected one title, received ${positionals.length}`);
  }

  args.title = positionals[0] ?? null;

  if (!args.help && !args.title) {
    throw new Error('Missing required title');
  }

  if (!VALID_MODES.has(args.mode)) {
    throw new Error(`--mode must be one of: ${Array.from(VALID_MODES).join(', ')}`);
  }

  return args;
}

function requireValue(argv, index, option) {
  const value = argv[index + 1];
  if (!value || value.startsWith('-')) {
    throw new Error(`${option} requires a value`);
  }
  return value;
}

function slugify(value) {
  const slug = value.toLowerCase().replace(/[^a-z0-9]+/gi, '-').replace(/^-+|-+$/g, '');
  return slug.slice(0, 48).replace(/-+$/g, '') || 'workflow';
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

async function writeIfMissing(filePath, content) {
  if (await pathType(filePath)) {
    throw new Error(`${filePath} already exists`);
  }
  await writeFile(filePath, content, 'utf8');
}

async function gitContext(root) {
  let candidate = root;

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
    return '.workflow/';
  }

  return `${relative.split(path.sep).join('/').replace(/\/+$/g, '')}/`;
}

async function ensureWorkflowGitExcluded(root) {
  const context = await gitContext(root);
  if (!context) {
    return 'not-git';
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
    return 'already-excluded';
  }

  const prefix = !existing || existing.endsWith('\n') ? '' : '\n';
  await appendFile(excludePath, `${prefix}${pattern}\n`, 'utf8');
  return 'added-local-exclude';
}

function pad(value) {
  return String(value).padStart(2, '0');
}

function formatRunTimestamp(date) {
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

function isoZ(date) {
  return date.toISOString();
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error(`ERROR: ${error.message}`);
    console.error(usage().trimEnd());
    return 2;
  }

  if (args.help) {
    console.log(usage().trimEnd());
    return 0;
  }

  const root = path.resolve(expandUser(args.root));
  if (!args.noGitExclude) {
    const excludeStatus = await ensureWorkflowGitExcluded(root);
    if (excludeStatus === 'added-local-exclude') {
      console.error('Added workflow artifact path to local Git exclude');
    } else if (excludeStatus === 'not-git') {
      console.error('Warning: root is not a Git checkout; keep .workflow/ out of version control');
    }
  }

  const now = new Date();
  const nextCheckIn = new Date(now.getTime() + 10 * 60 * 1000);
  const runSlug = slugify(args.slug || args.title);
  const runId = `${formatRunTimestamp(now)}-${runSlug}`;
  const runDir = path.join(root, '.workflow', 'ultracode', runId);

  if (await pathType(runDir)) {
    throw new Error(`Run directory already exists: ${runDir}`);
  }

  await mkdir(path.join(runDir, 'packets'), { recursive: true });
  await mkdir(path.join(runDir, 'results'));

  const state = {
    title: args.title,
    runId,
    createdAt: isoZ(now),
    status: 'planning',
    mode: args.mode,
    root,
    checkInIntervalMinutes: 10,
    lastCheckInAt: null,
    nextCheckInDueAt: isoZ(nextCheckIn),
    progress: {
      percentComplete: 5,
      eta: 'unknown',
      etaConfidence: 'low',
      done: [],
      remaining: ['Write packets', 'Run workers', 'Verify'],
      status: 'green',
      statusReason: 'Workflow initialized',
    },
    checkIns: [],
    resources: [],
    nativeWorkflow: null,
    packets: [],
    approvals: [],
    verification: [],
  };

  await writeIfMissing(path.join(runDir, 'state.json'), `${JSON.stringify(state, null, 2)}\n`);
  await writeIfMissing(
    path.join(runDir, 'plan.md'),
    `# Plan

## Goal

${args.title}

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
`,
  );
  await writeIfMissing(
    path.join(runDir, 'orchestration.md'),
    `# Orchestration

## Mode

${args.mode}

## Host Capabilities

- Native subagents:
- Runner:
- Network:
- Write access:

## Artifact Ownership

- Bookkeeper:
- Run directory: ${runDir}
- Parent responsibilities: user interaction, approvals, budget/resource decisions, worker lifecycle, progress reports, final synthesis
- Worker artifact rule: workers return results; they do not edit \`.workflow/\`.

## Work Packets

| Packet | Owner | Scope | Dependencies | Expected result |
| --- | --- | --- | --- | --- |

## Progress Cadence

- Interval: 10 minutes
- Last progress report:
- Next progress report: ${isoZ(nextCheckIn)}
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
`,
  );
  await writeIfMissing(
    path.join(runDir, 'integration.md'),
    `# Integration

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
`,
  );
  await writeIfMissing(
    path.join(runDir, 'final-report.md'),
    `# Final Report

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
`,
  );

  console.log(runDir);
  return 0;
}

main()
  .then((code) => {
    process.exitCode = code;
  })
  .catch((error) => {
    console.error(`ERROR: ${error.message}`);
    process.exitCode = 1;
  });
