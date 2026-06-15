import { execFile } from 'node:child_process';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';
import assert from 'node:assert/strict';
import test from 'node:test';

const execFileAsync = promisify(execFile);
const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const newRunScript = path.join(scriptDir, 'new-ultracode-run.mjs');
const verifyRunScript = path.join(scriptDir, 'verify-ultracode-run.mjs');

async function run(command, args, options = {}) {
  try {
    const result = await execFileAsync(command, args, {
      ...options,
      env: { ...process.env, ...options.env },
    });
    return { code: 0, stdout: result.stdout, stderr: result.stderr };
  } catch (error) {
    return {
      code: error.code ?? 1,
      stdout: error.stdout ?? '',
      stderr: error.stderr ?? '',
    };
  }
}

async function withTempDir(fn) {
  const root = await mkdtemp(path.join(os.tmpdir(), 'ultracode-run-test-'));
  try {
    return await fn(root);
  } finally {
    await rm(root, { force: true, recursive: true });
  }
}

async function createRun(root, title = 'Demo workflow') {
  const result = await run(process.execPath, [newRunScript, '--root', root, title]);
  assert.equal(result.code, 0, result.stderr);
  return result.stdout.trim().split(/\r?\n/).at(-1);
}

test('new run creates a non-strict-valid durable ledger', async () => {
  await withTempDir(async (root) => {
    const runDir = await createRun(root);
    const state = JSON.parse(await readFile(path.join(runDir, 'state.json'), 'utf8'));

    assert.equal(state.mode, 'durable');
    assert.equal(state.status, 'planning');
    assert.deepEqual(state.phases, []);
    assert.deepEqual(state.agents, []);

    const verification = await run(process.execPath, [verifyRunScript, runDir]);
    assert.equal(verification.code, 0, verification.stdout + verification.stderr);
    assert.match(verification.stdout, /OK:/);
  });
});

test('validator rejects tracked workflow artifacts even when workflow path is ignored', async () => {
  await withTempDir(async (root) => {
    const init = await run('git', ['init'], { cwd: root });
    assert.equal(init.code, 0, init.stderr);

    const runDir = await createRun(root);
    const add = await run('git', ['add', '-f', path.join('.workflow', 'ultracode', path.basename(runDir), 'state.json')], { cwd: root });
    assert.equal(add.code, 0, add.stderr);

    const verification = await run(process.execPath, [verifyRunScript, runDir]);
    assert.equal(verification.code, 1);
    assert.match(verification.stdout, /\.workflow\/ contains tracked or staged artifact/);
  });
});

test('validator uses the run directory root when state root is stale', async () => {
  await withTempDir(async (root) => {
    const init = await run('git', ['init'], { cwd: root });
    assert.equal(init.code, 0, init.stderr);

    const runDir = await createRun(root);
    const statePath = path.join(runDir, 'state.json');
    const state = JSON.parse(await readFile(statePath, 'utf8'));
    state.root = path.join(os.tmpdir(), 'not-the-ultracode-root');
    await writeFile(statePath, `${JSON.stringify(state, null, 2)}\n`, 'utf8');

    const add = await run('git', ['add', '-f', path.join('.workflow', 'ultracode', path.basename(runDir), 'state.json')], { cwd: root });
    assert.equal(add.code, 0, add.stderr);

    const verification = await run(process.execPath, [verifyRunScript, runDir]);
    assert.equal(verification.code, 1);
    assert.match(verification.stdout, /state\.json root does not match run directory root/);
    assert.match(verification.stdout, /\.workflow\/ contains tracked or staged artifact/);
  });
});

test('validator requires exact level-two headings', async () => {
  await withTempDir(async (root) => {
    const runDir = await createRun(root);
    await writeFile(
      path.join(runDir, 'workflow.md'),
      `# Workflow

### Goal

Demo workflow

### Approval Envelope

### Phase Graph

### Execution Rules
`,
      'utf8',
    );

    const verification = await run(process.execPath, [verifyRunScript, runDir]);
    assert.equal(verification.code, 1);
    assert.match(verification.stdout, /workflow\.md missing required sections/);
  });
});
