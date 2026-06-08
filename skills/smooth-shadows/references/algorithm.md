# Layered Smooth Box-Shadow Algorithm

This skill implements the technique described in [Smoother & sharper shadows with layered box-shadows](https://tobiasahlin.com/blog/layered-smooth-box-shadows/) by Tobias Ahlin (2019). The original `shadows.brumm.af` generator (and its successor `smoothshadows.com`) turned the article into an interactive tool with exactly the controls exposed by this skill.

## Core Idea

A single `box-shadow` is a blurred silhouette — it tends to look square or "computerish". By stacking multiple shadows with **increasing offset and blur**, we get fine-grained control over:

- **Spread / distance** (how far the shadow travels)
- **Concentration of depth** (how sharp or soft the falloff feels)
- **Overall softness**

Example from the article (5 layers, constant low alpha):

```css
box-shadow: 0 1px 1px rgba(0,0,0,0.12),
            0 2px 2px rgba(0,0,0,0.12),
            0 4px 4px rgba(0,0,0,0.12),
            0 8px 8px rgba(0,0,0,0.12),
            0 16px 16px rgba(0,0,0,0.12);
```

Notice the power-of-2 (or near power-of-2) progression. This is the classic "smooth" look.

## How the Three Styles Map to Curves

The generator uses the same progression principles and then varies alpha and blur multipliers per style (matching the Soft / Sharp / Linear buttons in the original UIs).

- **soft** — gentler, "dreamier". Slightly higher blur multiplier on outer layers + a milder alpha ramp. Feels modern and premium (the default most people want for cards/modals).
- **sharp** — more defined edges. Higher alpha on the inner layers, decreasing on the outer ones. Good for buttons, data-dense UIs, or when you want the shadow to feel more "pressed" or crisp.
- **linear** — even steps in offset and blur. Less "exponential magic", more predictable. Useful when you want the layers to feel evenly spaced.

You can also decouple blur from offset (the original article shows examples) — the script exposes `--blur` separately from `--vertical` so you can do exactly that.

## Alpha Strategy

- Low base opacity (0.06–0.10) spread across several layers is the secret to the "expensive" look.
- The script never lets a single layer get too opaque.
- For dark mode we simply raise the effective opacity (or you can pass a lighter `--color`).

## Practical Guidelines (baked into the skill)

- 3 layers: subtle separation
- 4–5 layers: the classic sweet spot (what the original tool defaulted to)
- 6+ layers: very soft / atmospheric (can start to feel muddy if opacity isn't lowered)

The script caps at 12 and recommends 3–6 in the help text.

## Further Reading

- Original article (with many visual examples): https://tobiasahlin.com/blog/layered-smooth-box-shadows/
- The old generator (archive / inspiration): shadows.brumm.af
- Current web UI: https://smoothshadows.com/

The JS implementation in `scripts/generate-smooth-shadow.js` is intentionally small and self-contained so it can be run from any installed location of this skill.
