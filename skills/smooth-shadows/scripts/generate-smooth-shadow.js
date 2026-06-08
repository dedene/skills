#!/usr/bin/env node
/**
 * generate-smooth-shadow.js
 *
 * Pure Node (no dependencies) generator for smooth layered box-shadows.
 * Recreates the visual behavior and controls of the classic shadows.brumm.af
 * tool (inspired by https://tobiasahlin.com/blog/layered-smooth-box-shadows/).
 *
 * This file lives inside the smooth-shadows skill. When the skill is installed
 * (via npx skills add or equivalent), this script is available at a path relative
 * to the loaded skill directory.
 *
 * Skill-relative path resolution note:
 *   Always refer to this script from SKILL.md and documentation as:
 *     scripts/generate-smooth-shadow.js
 *     or <this-skill-dir>/scripts/generate-smooth-shadow.js
 *   Never use repo-absolute paths. The skill may be symlinked and executed
 *   from arbitrary working directories.
 *
 * Usage examples:
 *   node scripts/generate-smooth-shadow.js --help
 *   node scripts/generate-smooth-shadow.js --vertical 32 --layers 5 --style soft --opacity 0.08 --blur 24 --color '#030712'
 *   node scripts/generate-smooth-shadow.js -v 24 -l 4 --style sharp --output css
 *
 * The script also exports generateSmoothShadow(params) for programmatic use
 * by agents that can require() it after locating the installed skill.
 */

const args = process.argv.slice(2);
const VALID_STYLES = new Set(['soft', 'sharp', 'linear']);
const VALID_OUTPUTS = new Set(['raw', 'css', 'tailwind']);
const VALUE_OPTIONS = new Set([
  '--style',
  '--layers',
  '-l',
  '--vertical',
  '-v',
  '--horizontal',
  '--h-dist',
  '--blur',
  '--opacity',
  '--color',
  '--output',
]);
const FLAG_OPTIONS = new Set(['--dark', '--help', '-h']);
const KNOWN_OPTIONS = new Set([...VALUE_OPTIONS, ...FLAG_OPTIONS]);

function showHelp() {
  console.log(`
smooth-shadows generator (layered box-shadow)

Options:
  --style <soft|sharp|linear>   Style preset (default: soft)
  --layers <n>                  Number of layers (default: 5, typical 3-6)
  --vertical, -v <px>           Max vertical distance / lift (default: 32)
  --horizontal, --h-dist <px>   Max horizontal offset (default: 0)
  --blur <px>                   Base/max blur radius (default: 24)
  --opacity <0-1>               Base opacity for the shadow color (default: 0.08)
  --color <hex>                 Shadow color, e.g. #030712 or #000000 (default: #030712)
  --output <raw|css|tailwind>   Output format (default: raw)
  --dark                        Produce a dark-mode friendly variant (increases opacity slightly)
  --help, -h                    Show this help

Examples:
  node scripts/generate-smooth-shadow.js --vertical 32 --layers 5 --style soft
  node scripts/generate-smooth-shadow.js -v 16 --layers 3 --style sharp --output css --color '#000000'
  node scripts/generate-smooth-shadow.js --vertical 40 --layers 6 --style linear --opacity 0.10 --blur 32
`);
}

function parseArgs(argv = args) {
  const opts = {
    style: 'soft',
    layers: 5,
    vertical: 32,
    horizontal: 0,
    blur: 24,
    opacity: 0.08,
    color: '#030712',
    output: 'raw',
    dark: false,
    help: false,
  };

  const readValue = (option, index) => {
    const value = argv[index + 1];
    if (value === undefined || KNOWN_OPTIONS.has(value)) {
      throw new Error(`${option} requires a value`);
    }
    return value;
  };

  const parseNumber = (option, value) => {
    if (String(value).trim() === '') {
      throw new Error(`${option} must be a finite number`);
    }
    const num = Number(value);
    if (!Number.isFinite(num)) {
      throw new Error(`${option} must be a finite number`);
    }
    return num;
  };

  const parseInteger = (option, value) => {
    const num = parseNumber(option, value);
    return parseInt(String(num), 10);
  };

  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];

    if (a === '--help' || a === '-h') {
      opts.help = true;
    } else if (a === '--style') {
      opts.style = readValue(a, i).toLowerCase();
      i++;
    } else if (a === '--layers' || a === '-l') {
      opts.layers = parseInteger(a, readValue(a, i));
      i++;
    } else if (a === '--vertical' || a === '-v') {
      opts.vertical = parseNumber(a, readValue(a, i));
      i++;
    } else if (a === '--horizontal' || a === '--h-dist') {
      opts.horizontal = parseNumber(a, readValue(a, i));
      i++;
    } else if (a === '--blur') {
      opts.blur = parseNumber(a, readValue(a, i));
      i++;
    } else if (a === '--opacity') {
      opts.opacity = parseNumber(a, readValue(a, i));
      i++;
    } else if (a === '--color') {
      opts.color = readValue(a, i);
      i++;
    } else if (a === '--output') {
      opts.output = readValue(a, i).toLowerCase();
      i++;
    } else if (a === '--dark') {
      opts.dark = true;
    } else if (a.startsWith('-')) {
      throw new Error(`Unknown option: ${a}`);
    } else {
      throw new Error(`Unexpected argument: ${a}`);
    }
  }

  if (!VALID_STYLES.has(opts.style)) {
    throw new Error(`--style must be one of: ${Array.from(VALID_STYLES).join(', ')}`);
  }
  if (!VALID_OUTPUTS.has(opts.output)) {
    throw new Error(`--output must be one of: ${Array.from(VALID_OUTPUTS).join(', ')}`);
  }
  if (!isValidHexColor(opts.color)) {
    throw new Error('--color must be a 3- or 6-digit hex color, with or without #');
  }

  return opts;
}

function isValidHexColor(hex) {
  return /^#?(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(String(hex).trim());
}

function hexToRgb(hex) {
  // Accepts #rgb, #rrggbb. Returns "r g b" string.
  let h = hex.replace('#', '').trim();
  if (h.length === 3) {
    h = h.split('').map(c => c + c).join('');
  }
  const num = parseInt(h, 16);
  if (isNaN(num)) return '0 0 0';
  const r = (num >> 16) & 255;
  const g = (num >> 8) & 255;
  const b = num & 255;
  return `${r} ${g} ${b}`;
}

function clamp(n, min, max) {
  return Math.min(max, Math.max(min, n));
}

/**
 * Core generator. Returns the value portion of a box-shadow declaration
 * (comma-separated layers), e.g.:
 *   "0 1px 1px rgba(3,7,18,0.12), 0 2px 2px rgba(3,7,18,0.12), ..."
 *
 * The math is generalized from the canonical examples in
 * https://tobiasahlin.com/blog/layered-smooth-box-shadows/
 * and tuned to feel like the classic smooth shadow generator UIs.
 */
function generateSmoothShadow(params = {}) {
  const {
    style = 'soft',
    layers = 5,
    vertical = 32,
    horizontal = 0,
    blur = 24,
    opacity = 0.08,
    color = '#030712',
    dark = false,
  } = params;

  const n = clamp(Math.round(layers), 1, 12);
  const maxY = Math.max(0, vertical);
  const maxX = horizontal;
  const maxB = Math.max(1, blur);
  let baseO = clamp(opacity, 0.01, 0.6);

  if (dark) {
    // Dark surfaces need stronger (or lighter-colored) shadows.
    // We take the pragmatic route of boosting opacity.
    baseO = clamp(baseO * 1.9, 0.03, 0.55);
  }

  const rgb = hexToRgb(color);
  const shadows = [];

  for (let i = 1; i <= n; i++) {
    const t = i / n; // 0 < t <= 1

    // Geometric-ish progression gives the classic "smooth" falloff
    // (very close to the original tool and the article's 1,2,4,8,16 pattern when maxY ~16-32).
    let y = Math.round(maxY * Math.pow(t, 0.92));
    let x = Math.round(maxX * Math.pow(t, 0.92));
    let b = Math.round(maxB * Math.pow(t, 0.95));

    let o = baseO;

    if (style === 'sharp') {
      // Inner layers stronger, outer layers fade more (concentrated depth)
      o = baseO * (1.65 - t * 0.95);
      b = Math.round(b * 0.82);
    } else if (style === 'soft') {
      // Gentler, dreamier: extra blur on outer layers, slightly softer overall
      b = Math.round(b * 1.18);
      o = baseO * (0.65 + t * 0.55);
    } else if (style === 'linear') {
      // More even steps (still benefits from multiple layers)
      o = baseO;
      b = Math.round(maxB * t);
      y = Math.round(maxY * t);
      x = Math.round(maxX * t);
    }

    o = clamp(o, 0.015, 0.6);

    // Use the modern rgba(r g b / a) syntax — widely supported and clean.
    // Fall back to classic comma syntax if you need IE11 (rare in 2026).
    const layer = `${x}px ${y}px ${b}px rgba(${rgb} / ${o.toFixed(3)})`;
    shadows.push(layer);
  }

  return shadows.join(', ');
}

function formatOutput(value, format) {
  switch (format) {
    case 'css':
      return `box-shadow: ${value};`;
    case 'tailwind':
      // Tailwind arbitrary value escaping:
      // - Replace the ", " separator between shadow layers first (becomes ,_)
      // - Then turn remaining spaces into _
      // This avoids ugly ",__" artifacts.
      const safe = value
        .replace(/, /g, ',_')
        .replace(/\s+/g, '_');
      return `shadow-[${safe}]`;
    case 'raw':
    default:
      return value;
  }
}

function main() {
  let p;

  try {
    p = parseArgs();
  } catch (err) {
    console.error(`Error: ${err.message}`);
    console.error('Run with --help to see valid options.');
    process.exit(1);
  }

  if (p.help) {
    showHelp();
    process.exit(0);
  }

  // Normalize numeric inputs (generateSmoothShadow also clamps, but this keeps the log accurate)
  p.layers = clamp(Math.round(Number(p.layers) || 5), 1, 12);
  p.vertical = Number.isFinite(p.vertical) ? p.vertical : 32;
  p.horizontal = Number.isFinite(p.horizontal) ? p.horizontal : 0;
  p.blur = Number.isFinite(p.blur) ? Math.max(1, p.blur) : 24;
  p.opacity = Number.isFinite(p.opacity) ? clamp(p.opacity, 0.01, 0.6) : 0.08;

  const value = generateSmoothShadow(p);
  const out = formatOutput(value, p.output);

  console.log(out);

  // Also emit a small hint on stderr for humans (agents usually capture stdout)
  if (process.stderr.isTTY) {
    console.error(`\n# layers=${p.layers} style=${p.style} v=${p.vertical} blur=${p.blur} opacity=${p.opacity}`);
  }
}

// Export for agents that locate the installed skill and do require(...)
module.exports = {
  generateSmoothShadow,
  formatOutput,
};

if (require.main === module) {
  main();
}
