#!/usr/bin/env node
import { readdir, readFile, stat } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';

const REQUIRED_FILES = [
  'plan.md',
  'orchestration.md',
  'state.json',
  'integration.md',
  'final-report.md',
];

const REQUIRED_DIRS = ['packets', 'results'];
const ALLOWED_STATUSES = new Set(['planning', 'delegating', 'integrating', 'verifying', 'complete', 'blocked', 'cancelled']);
const TERMINAL_STATUSES = new Set(['complete', 'blocked', 'cancelled']);
const CLOSED_RESOURCE_STATUSES = new Set(['closed', 'released', 'stopped', 'removed', 'cleaned', 'handed-off']);
const ETA_CONFIDENCE_VALUES = new Set(['low', 'medium', 'high']);
const PROGRESS_STATUSES = new Set(['green', 'yellow', 'red']);

function usage() {
  return `Usage: verify-ultracode-run.mjs [options] <run-dir>

Validate the basic artifact contract for an Ultracode workflow run.

Options:
  --strict       Fail on incomplete final handoff fields and live resources
  -h, --help     Show this help
`;
}

function parseArgs(argv) {
  const args = { strict: false, runDir: null };
  const positionals = [];

  for (const arg of argv) {
    if (arg === '-h' || arg === '--help') {
      args.help = true;
    } else if (arg === '--strict') {
      args.strict = true;
    } else if (arg.startsWith('-')) {
      throw new Error(`Unknown option: ${arg}`);
    } else {
      positionals.push(arg);
    }
  }

  if (positionals.length > 1) {
    throw new Error(`Expected one run directory, received ${positionals.length}`);
  }

  args.runDir = positionals[0] ?? null;
  if (!args.help && !args.runDir) {
    throw new Error('Missing required run directory');
  }

  return args;
}

async function pathDetails(candidate) {
  try {
    return await stat(candidate);
  } catch (error) {
    if (error.code === 'ENOENT') return null;
    throw error;
  }
}

async function pathType(candidate) {
  const details = await pathDetails(candidate);
  if (!details) return null;
  if (details.isDirectory()) return 'directory';
  if (details.isFile()) return 'file';
  return 'other';
}

function hasRequiredHeadings(text, headings) {
  return headings.every((heading) => text.includes(`## ${heading}`));
}

function sectionBody(text, heading) {
  const marker = `## ${heading}`;
  const start = text.indexOf(marker);
  if (start === -1) return '';

  const bodyStart = text.indexOf('\n', start);
  if (bodyStart === -1) return '';

  const nextHeading = text.indexOf('\n## ', bodyStart + 1);
  if (nextHeading === -1) {
    return text.slice(bodyStart).trim();
  }
  return text.slice(bodyStart, nextHeading).trim();
}

function hasMeaningfulSectionBody(text, heading) {
  const body = sectionBody(text, heading);
  if (!body) return false;

  const placeholders = new Set(['-', '- [ ]', 'todo', 'tbd', 'n/a']);
  return body
    .split(/\r?\n/)
    .map((line) => line.trim())
    .some((line) => line && !placeholders.has(line.toLowerCase()));
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

async function readIgnoreFile(ignoreFile) {
  if ((await pathType(ignoreFile)) !== 'file') return [];
  const content = await readFile(ignoreFile, 'utf8');
  return content
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith('#'));
}

async function ignorePatterns(root) {
  const context = await gitContext(root);
  if (!context) return null;

  const patterns = new Set();
  const expectedPattern = workflowExcludePattern(root, context.worktreeRoot);
  const ignoreFiles = [
    path.join(context.gitDir, 'info', 'exclude'),
    path.join(context.worktreeRoot, '.gitignore'),
  ];

  const rootGitignore = path.join(root, '.gitignore');
  if (rootGitignore !== ignoreFiles[1]) {
    ignoreFiles.push(rootGitignore);
  }

  for (const ignoreFile of ignoreFiles) {
    for (const pattern of await readIgnoreFile(ignoreFile)) {
      patterns.add(pattern);
    }
  }

  return { patterns, expectedPattern };
}

async function workflowIsGitExcluded(root) {
  const result = await ignorePatterns(root);
  if (!result) return null;

  const { patterns, expectedPattern } = result;
  const workflowPatterns = new Set([
    '.workflow/',
    '.workflow',
    '.workflow/**',
    '.workflow/*',
    '**/.workflow/',
    '**/.workflow/**',
    '**/.workflow/*',
    '/.workflow/',
    '/.workflow',
    expectedPattern,
    `/${expectedPattern}`,
    `${expectedPattern}**`,
    `${expectedPattern}*`,
    `/${expectedPattern}**`,
    `/${expectedPattern}*`,
    expectedPattern.replace(/\/$/g, ''),
  ]);

  return Array.from(workflowPatterns).some((pattern) => patterns.has(pattern));
}

function inferredRootFromRunDir(runDir) {
  const parent = path.dirname(runDir);
  const grandparent = path.dirname(parent);
  if (path.basename(parent) === 'ultracode' && path.basename(grandparent) === '.workflow') {
    return path.dirname(grandparent);
  }
  return runDir;
}

function resolveStateRoot(runDir, state) {
  const inferredRoot = inferredRootFromRunDir(runDir);
  const rootValue = state.root;
  if (!rootValue) {
    return inferredRoot;
  }

  const root = expandUser(String(rootValue));
  if (path.isAbsolute(root)) {
    return root;
  }
  return path.resolve(inferredRoot, root);
}

function addProblem(strict, warnings, errors, message) {
  if (strict) {
    errors.push(message);
  } else {
    warnings.push(message);
  }
}

function isPlainObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function validateNativeWorkflow(state, errors) {
  if (!Object.prototype.hasOwnProperty.call(state, 'nativeWorkflow') || state.nativeWorkflow === null) {
    return;
  }

  const nativeWorkflow = state.nativeWorkflow;
  if (!isPlainObject(nativeWorkflow)) {
    errors.push('state.json nativeWorkflow must be null or an object');
    return;
  }

  if (!nativeWorkflow.host || typeof nativeWorkflow.host !== 'string') {
    errors.push('state.json nativeWorkflow.host must be a string when nativeWorkflow is set');
  }

  for (const field of ['runId', 'workflowName', 'scriptPath', 'snapshotPath', 'agentLogDir']) {
    if (nativeWorkflow[field] !== undefined && typeof nativeWorkflow[field] !== 'string') {
      errors.push(`state.json nativeWorkflow.${field} must be a string when present`);
    }
  }

  for (const field of ['totalTokens', 'totalToolCalls', 'durationMs']) {
    if (nativeWorkflow[field] !== undefined && typeof nativeWorkflow[field] !== 'number') {
      errors.push(`state.json nativeWorkflow.${field} must be a number when present`);
    }
  }
}

function validateProgress(state, strict, warnings, errors) {
  const progress = state.progress;
  if (!Object.prototype.hasOwnProperty.call(state, 'progress') || !isPlainObject(progress)) {
    addProblem(strict, warnings, errors, 'state.json progress must be present as an object');
    return;
  }

  const nonEmptyString = (value) => typeof value === 'string' && value.trim() !== '';
  const checks = [
    [typeof progress.percentComplete === 'number' && progress.percentComplete >= 0 && progress.percentComplete <= 100, 'state.json progress.percentComplete must be a number from 0 to 100'],
    [nonEmptyString(progress.eta), 'state.json progress.eta must be a non-empty string'],
    [ETA_CONFIDENCE_VALUES.has(progress.etaConfidence), 'state.json progress.etaConfidence must be low, medium, or high'],
    [Array.isArray(progress.done), 'state.json progress.done must be a list'],
    [Array.isArray(progress.remaining), 'state.json progress.remaining must be a list'],
    [PROGRESS_STATUSES.has(progress.status), 'state.json progress.status must be green, yellow, or red'],
    [nonEmptyString(progress.statusReason), 'state.json progress.statusReason must be a non-empty string'],
  ];

  for (const [valid, message] of checks) {
    if (!valid) addProblem(strict, warnings, errors, message);
  }
}

async function listMarkdownFiles(dirPath) {
  if ((await pathType(dirPath)) !== 'directory') return [];
  const entries = await readdir(dirPath, { withFileTypes: true });
  return entries
    .filter((entry) => entry.isFile() && entry.name.endsWith('.md'))
    .map((entry) => path.join(dirPath, entry.name))
    .sort();
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

  const runDir = path.resolve(expandUser(args.runDir));
  const errors = [];
  const warnings = [];

  const runType = await pathType(runDir);
  if (!runType) {
    errors.push(`Run directory does not exist: ${runDir}`);
  } else if (runType !== 'directory') {
    errors.push(`Run path is not a directory: ${runDir}`);
  }

  if (errors.length > 0) {
    for (const error of errors) {
      console.log(`ERROR: ${error}`);
    }
    return 1;
  }

  for (const rel of REQUIRED_FILES) {
    const filePath = path.join(runDir, rel);
    const details = await pathDetails(filePath);
    if (!details || !details.isFile()) {
      errors.push(`Missing required file: ${rel}`);
    } else if (details.size === 0) {
      errors.push(`Required file is empty: ${rel}`);
    }
  }

  for (const rel of REQUIRED_DIRS) {
    const dirPath = path.join(runDir, rel);
    if ((await pathType(dirPath)) !== 'directory') {
      errors.push(`Missing required directory: ${rel}`);
    }
  }

  const statePath = path.join(runDir, 'state.json');
  let state = {};
  if ((await pathType(statePath)) === 'file') {
    try {
      state = JSON.parse(await readFile(statePath, 'utf8'));
    } catch (error) {
      errors.push(`state.json is invalid JSON: ${error.message}`);
      state = {};
    }

    const status = state.status;
    if (!ALLOWED_STATUSES.has(status)) {
      errors.push(`state.json status must be one of ${JSON.stringify(Array.from(ALLOWED_STATUSES).sort())}`);
    }

    if (!state.runId) {
      errors.push('state.json missing runId');
    }
    if (!state.title) {
      errors.push('state.json missing title');
    }
    if (!Array.isArray(state.packets ?? [])) {
      errors.push('state.json packets must be a list');
    }
    if (state.checkInIntervalMinutes !== 10) {
      addProblem(args.strict, warnings, errors, 'state.json checkInIntervalMinutes should be 10');
    }
    if (!Array.isArray(state.checkIns)) {
      addProblem(args.strict, warnings, errors, 'state.json checkIns must be a list');
    }
    if (!Array.isArray(state.resources)) {
      addProblem(args.strict, warnings, errors, 'state.json resources must be a list');
    }
    validateNativeWorkflow(state, errors);
    validateProgress(state, args.strict, warnings, errors);

    const root = resolveStateRoot(runDir, state);
    const ignored = await workflowIsGitExcluded(root);
    if (ignored === false) {
      addProblem(args.strict, warnings, errors, '.workflow/ is not ignored by Git metadata');
    }

    const resources = state.resources;
    if (Array.isArray(resources)) {
      const activeResources = resources.filter(
        (resource) => resource && typeof resource === 'object' && !CLOSED_RESOURCE_STATUSES.has(resource.status),
      );
      if (activeResources.length > 0) {
        const message = `${activeResources.length} resource(s) still active or unclosed in state.json`;
        if (TERMINAL_STATUSES.has(status)) {
          addProblem(args.strict, warnings, errors, message);
        } else {
          warnings.push(message);
        }
      }
    }
  }

  const planPath = path.join(runDir, 'plan.md');
  if ((await pathType(planPath)) === 'file') {
    const planText = await readFile(planPath, 'utf8');
    if (!hasRequiredHeadings(planText, ['Goal', 'Success Criteria', 'Verification Gates'])) {
      errors.push('plan.md missing required sections');
    }
    if (/(^|\n)- \[ \][ \t]*(\n|$)/.test(planText)) {
      addProblem(args.strict, warnings, errors, 'plan.md still contains empty checklist items');
    }
  }

  const orchestrationPath = path.join(runDir, 'orchestration.md');
  if ((await pathType(orchestrationPath)) === 'file') {
    const orchestrationText = await readFile(orchestrationPath, 'utf8');
    if (!hasRequiredHeadings(orchestrationText, ['Mode', 'Host Capabilities', 'Work Packets'])) {
      errors.push('orchestration.md missing required sections');
    }
    const hasProgressCadence = ['Progress Cadence', 'Check-In Cadence'].some((heading) => hasRequiredHeadings(orchestrationText, [heading]));
    if (!hasProgressCadence || !hasRequiredHeadings(orchestrationText, ['Resource Plan'])) {
      addProblem(args.strict, warnings, errors, 'orchestration.md missing progress cadence or resource sections');
    }
    if (!hasRequiredHeadings(orchestrationText, ['Artifact Ownership'])) addProblem(args.strict, warnings, errors, 'orchestration.md missing Artifact Ownership section');
  }

  const packetFiles = await listMarkdownFiles(path.join(runDir, 'packets'));
  const resultFiles = await listMarkdownFiles(path.join(runDir, 'results'));
  if (packetFiles.length > 0 && resultFiles.length < packetFiles.length) {
    warnings.push(`${packetFiles.length} packet file(s), but only ${resultFiles.length} result file(s)`);
  }

  const finalPath = path.join(runDir, 'final-report.md');
  if ((await pathType(finalPath)) === 'file') {
    const finalText = await readFile(finalPath, 'utf8');
    if (!hasRequiredHeadings(finalText, ['Outcome', 'Verification Evidence', 'Remaining Risks'])) {
      errors.push('final-report.md missing required sections');
    }
    if (!hasRequiredHeadings(finalText, ['Resource Cleanup'])) {
      addProblem(args.strict, warnings, errors, 'final-report.md missing Resource Cleanup section');
    }
    if (!hasMeaningfulSectionBody(finalText, 'Outcome')) {
      addProblem(args.strict, warnings, errors, 'final-report.md outcome appears empty');
    }
    if (!hasMeaningfulSectionBody(finalText, 'Verification Evidence')) {
      addProblem(args.strict, warnings, errors, 'final-report.md verification evidence appears empty');
    }
    if (!hasMeaningfulSectionBody(finalText, 'Resource Cleanup')) {
      addProblem(args.strict, warnings, errors, 'final-report.md resource cleanup appears empty');
    }
    if (!hasMeaningfulSectionBody(finalText, 'Remaining Risks')) {
      addProblem(args.strict, warnings, errors, 'final-report.md remaining risks appears empty');
    }
  }

  for (const warning of warnings) {
    console.log(`WARNING: ${warning}`);
  }
  for (const error of errors) {
    console.log(`ERROR: ${error}`);
  }

  if (errors.length > 0) {
    return 1;
  }

  console.log(`OK: ${runDir}`);
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
