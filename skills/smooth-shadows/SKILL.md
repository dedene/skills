---
name: smooth-shadows
description: "Generate smooth, multi-layer box-shadow CSS that faithfully recreates the classic shadows.brumm.af / Tobias Ahlin layered technique. Use when you need soft, realistic elevation for cards, buttons, modals, overlays, or any UI element instead of a single harsh shadow. Supports the original controls: style (soft/sharp/linear), number of layers, vertical & horizontal distance, blur, base opacity, and shadow color. Produces ready-to-paste CSS or Tailwind arbitrary values."
---

# Smooth Shadows

Generate production-quality **layered smooth box-shadows** that look like the beloved (now offline) `shadows.brumm.af` tool and the current `smoothshadows.com` successor.

This skill implements the technique from Tobias Ahlin's canonical article and gives agents the same parameters the original UI exposed (Style, Opacity, Blur, Layered shadows count, Vertical/Horizontal distance, Colors).

## Quick Start

```bash
/smooth-shadows soft lift on a dashboard card, vertical 32px, 5 layers, blur around 24

/smooth-shadows --style sharp --layers 4 --vertical 16 --output css
```

Natural language or explicit flags both work.

The skill will return the full `box-shadow` value (and usually a Tailwind version too).

## Parameters (match the original UI)

| Control            | Flag / Param          | Default | Notes |
|--------------------|-----------------------|---------|-------|
| Style              | `--style`             | soft    | `soft` (gentle, larger blur), `sharp` (crisper, stronger inner layers), `linear` (even steps) |
| Layered shadows    | `--layers`, `-l`      | 5       | 3–6 is the sweet spot for most UIs. More = softer spread but can get muddy. |
| Vertical distance  | `--vertical`, `-v`    | 32      | The "lift" / main y offset of the largest layer (px). |
| Horizontal         | `--horizontal`, `--h-dist` | 0   | Side offset (rarely needed, but supported). |
| Blur               | `--blur`              | 24      | Base/max blur radius. The generator scales it across layers. |
| Opacity            | `--opacity`           | 0.08    | Base alpha for the shadow color (very low = modern & subtle). |
| Color              | `--color`             | #030712 | Any hex. The same color is used for every layer with varying alpha. |
| Output             | `--output`            | raw     | `raw` (just the value), `css` (full `box-shadow: ...;`), `tailwind` (arbitrary `shadow-[...]`). |
| Dark mode          | `--dark`              | false   | Boosts opacity for dark surfaces (or use a lighter color). |

## Workflow

1. **Understand the request**  
   Extract (or ask for) the visual intent: how "lifted" does it feel? Soft & dreamy, crisp & defined, or even linear? Any dark mode context?

2. **Choose good defaults or map the request**  
   - Soft card / modal lift → style=soft, 4–6 layers, vertical 24–40, low opacity (0.06–0.10)
   - Crisp button or pressed state → style=sharp, 3–4 layers, smaller vertical
   - Subtle background separation → style=linear or soft, 3 layers, very low opacity

3. **Generate (preferred: use the deterministic script)**  
   Call the bundled script for pixel-perfect, repeatable output instead of the model inventing numbers.

4. **Present & refine**  
   Return:
   - The raw `box-shadow` value
   - A ready `<div style="box-shadow: ...">` or CSS rule snippet
   - Tailwind arbitrary value version
   - One-sentence note on why these numbers (e.g. "5 layers with geometric progression gives the classic soft falloff")

5. **Offer variations**  
   "Want a slightly more dramatic version? I can give you vertical 48 / 6 layers."  
   "Dark surface? I can regenerate with --dark."

## Scripts

### `scripts/generate-smooth-shadow.js`

The single source of truth for the layer math. Run it directly for perfect reproducibility.

**From inside the installed skill (recommended form):**

```bash
node <this-skill-dir>/scripts/generate-smooth-shadow.js --vertical 32 --layers 5 --style soft --opacity 0.08 --blur 24 --color '#030712'
node <this-skill-dir>/scripts/generate-smooth-shadow.js -v 16 -l 3 --style sharp --output css
node <this-skill-dir>/scripts/generate-smooth-shadow.js --vertical 40 --layers 6 --style linear --dark --output tailwind
```

**Full help:**

```bash
node <this-skill-dir>/scripts/generate-smooth-shadow.js --help
```

The script also exports `generateSmoothShadow(params)` so an agent that has located the skill directory can `require()` it programmatically if desired.

Resolve script paths relative to this skill directory when installed.

## References

- `references/algorithm.md` — The Tobias Ahlin technique, how the three styles map to alpha & blur curves, and the concrete examples the generator is based on.
- `references/examples.md` — Ready-to-copy `box-shadow` declarations for common UI patterns (with the exact params that produced them).

## Integration with Other Skills

- Pairs extremely well with **make-interfaces-feel-better** (which explicitly recommends "Use layered box-shadow with transparency" to avoid hard borders).
- Use the output with any frontend-design / impeccable flow when building cards, modals, navigation, etc.
- For Figma: the values translate directly to multiple `DROP_SHADOW` effects on a node (see figma-use effect-style patterns for the API shape). The skill can also just emit the numbers for you to apply manually.

## Troubleshooting

### "The shadow feels too heavy / has hard edges"
Reduce `--layers` to 3–4 or lower `--opacity`. The classic look uses surprisingly low opacity spread across several layers.

### "I need it for a dark surface"
Add `--dark` (the script increases opacity). You can also pass a lighter `color` (e.g. a soft warm gray) for a different aesthetic.

### "The numbers don't match smoothshadows.com exactly"
The generator targets the *visual character* of the original tool using the public algorithm. Small differences in the exact easing curve are normal; the result will still look smooth and professional. Tweak vertical/blur/layers by hand if you need pixel-perfect parity with a specific screenshot.

### "I want a full elevation scale (xs → 2xl)"
Run the generator several times with increasing `--vertical` values (e.g. 4, 8, 16, 32, 48) and the same style. Or ask the skill: "give me a 6-step smooth shadow elevation scale".

### "Tailwind output looks ugly"
The arbitrary value is intentionally ugly in source but produces the correct runtime shadow. Extract it to a component or `@layer utilities` if you will reuse it often.

## Why This Exists

Single `box-shadow` values almost always look cheap or "computer-y". Layering several shadows with carefully increasing offset + blur (and controlled alpha) is one of the highest-leverage micro-details in UI craft. This skill makes that technique trivial and repeatable for agents.

Credit: technique by [Tobias Ahlin](https://tobiasahlin.com/blog/layered-smooth-box-shadows/), original generator by Philipp Brumm, current web UI at smoothshadows.com.
