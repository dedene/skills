import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readFile, rm, stat, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { createAutopilotInterviewRun, slugifyTitle } from './new-autopilot-interview-run.mjs';

assert.equal(slugifyTitle('API shape: ask vs decide?'), 'api-shape-ask-vs-decide');
assert.equal(slugifyTitle(''), 'interview');

const root = await mkdtemp(path.join(os.tmpdir(), 'autopilot-interview-test-'));

try {
  await mkdir(path.join(root, '.git', 'info'), { recursive: true });
  await writeFile(path.join(root, '.git', 'info', 'exclude'), '# local excludes\n');

  const first = await createAutopilotInterviewRun({
    root,
    title: 'Checkout retry plan',
    ensureGitExclude: true,
    now: new Date('2026-06-09T12:34:56.789Z'),
  });

  assert.equal(first.runId, '20260609-123456-checkout-retry-plan');
  assert.equal(first.relativeRunDir, '.workflow/autopilot-interview/20260609-123456-checkout-retry-plan');
  assert.equal(first.exclude.status, 'added-local-exclude');
  assert.equal(first.exclude.pattern, '.workflow/');

  const log = await readFile(first.decisionLogPath, 'utf8');
  assert.match(log, /^# Autopilot Interview Decision Log/m);
  assert.match(log, /Goal: Checkout retry plan/);
  assert.match(log, /## Context Capsule/);
  assert.match(log, /## Decision Ledger/);
  assert.match(log, /- Question asked: <exact human prompt or internal decision question>/);
  assert.match(log, /- Options presented: <A\/B\/C options shown, or "not presented; auto-decided">/);

  const skillPath = fileURLToPath(new URL('../SKILL.md', import.meta.url));
  const skill = await readFile(skillPath, 'utf8');
  assert.match(skill, /- Question asked: <exact human prompt or internal decision question>/);
  assert.match(skill, /- Options presented: <A\/B\/C options shown, or "not presented; auto-decided">/);

  const exclude = await readFile(path.join(root, '.git', 'info', 'exclude'), 'utf8');
  assert.match(exclude, /^\.workflow\/$/m);

  await createAutopilotInterviewRun({
    root,
    title: 'Second pass',
    ensureGitExclude: true,
    now: new Date('2026-06-09T12:35:00.000Z'),
  });

  const excludeAfterSecondRun = await readFile(path.join(root, '.git', 'info', 'exclude'), 'utf8');
  assert.equal(excludeAfterSecondRun.match(/^\.workflow\/$/gm).length, 1);

  await stat(path.join(root, '.workflow', 'autopilot-interview', '20260609-123500-second-pass'));

  await assert.rejects(
    createAutopilotInterviewRun({
      root,
      title: 'Second pass',
      ensureGitExclude: true,
      now: new Date('2026-06-09T12:35:00.000Z'),
    }),
    /Run directory already exists/,
  );

  const excludeAfterDuplicate = await readFile(path.join(root, '.git', 'info', 'exclude'), 'utf8');
  assert.equal(excludeAfterDuplicate.match(/^\.workflow\/$/gm).length, 1);

  const linkedWorktreeRoot = path.join(root, 'linked-worktree');
  const linkedGitDir = path.join(root, 'git-data', 'worktrees', 'linked-worktree');
  const linkedProjectRoot = path.join(linkedWorktreeRoot, 'packages', 'app');
  await mkdir(linkedProjectRoot, { recursive: true });
  await mkdir(linkedGitDir, { recursive: true });
  await writeFile(
    path.join(linkedWorktreeRoot, '.git'),
    'gitdir: ../git-data/worktrees/linked-worktree\n',
  );

  const linked = await createAutopilotInterviewRun({
    root: linkedProjectRoot,
    title: 'Nested worktree plan',
    ensureGitExclude: true,
    now: new Date('2026-06-09T12:36:00.000Z'),
  });

  assert.equal(linked.exclude.status, 'added-local-exclude');
  assert.equal(linked.exclude.pattern, 'packages/app/.workflow/');

  const linkedExclude = await readFile(path.join(linkedGitDir, 'info', 'exclude'), 'utf8');
  assert.match(linkedExclude, /^packages\/app\/\.workflow\/$/m);
} finally {
  await rm(root, { recursive: true, force: true });
}
