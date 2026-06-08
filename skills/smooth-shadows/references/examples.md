# Ready-to-Use Examples

All examples were produced by the deterministic script in this skill. Copy the `box-shadow` (or Tailwind) value directly.

## Soft Card Lift (the classic "modern" look)

Command (matches the screenshot defaults):
```
node scripts/generate-smooth-shadow.js --vertical 32 --layers 5 --style soft --opacity 0.08 --blur 24 --color '#030712' --output css
```

Result:
```css
box-shadow: 0px 7px 6px rgba(3 7 18 / 0.061),
            0px 14px 12px rgba(3 7 18 / 0.070),
            0px 20px 18px rgba(3 7 18 / 0.078),
            0px 26px 22px rgba(3 7 18 / 0.087),
            0px 32px 28px rgba(3 7 18 / 0.096);
```

Tailwind (using the improved escaping from the generator):
```
node scripts/generate-smooth-shadow.js --vertical 32 --layers 5 --style soft --opacity 0.08 --blur 24 --color '#030712' --output tailwind
```

```html
<div class="shadow-[0px_7px_6px_rgba(3_7_18_/_0.061),_0px_14px_12px_rgba(3_7_18_/_0.070),_0px_20px_18px_rgba(3_7_18_/_0.078),_0px_26px_22px_rgba(3_7_18_/_0.087),_0px_32px_28px_rgba(3_7_18_/_0.096)] ...">
```

Use for: dashboard cards, content containers, popovers.

## Crisp / Sharp Small Shadow (buttons, menu items)

```
node scripts/generate-smooth-shadow.js -v 16 -l 4 --style sharp --color '#000000' --output css
```

Result:
```css
box-shadow: 0px 4px 5px rgba(0 0 0 / 0.113),
            0px 8px 10px rgba(0 0 0 / 0.094),
            0px 12px 15px rgba(0 0 0 / 0.075),
            0px 16px 20px rgba(0 0 0 / 0.056);
```

Use for: primary buttons, select triggers, compact UI elements where you want definition without softness.

## Larger Soft / Atmospheric (modals, big overlays)

```
node scripts/generate-smooth-shadow.js --vertical 40 --layers 6 --style soft --opacity 0.06 --blur 36 --output css
```

Result:
```css
box-shadow: 0px 8px 8px rgba(3 7 18 / 0.044),
            0px 15px 15px rgba(3 7 18 / 0.050),
            0px 21px 22px rgba(3 7 18 / 0.056),
            0px 28px 28px rgba(3 7 18 / 0.061),
            0px 34px 35px rgba(3 7 18 / 0.067),
            0px 40px 42px rgba(3 7 18 / 0.072);
```

Feels expensive and distant.

## Small Linear / Even (subtle borders between sections)

```
node scripts/generate-smooth-shadow.js -v 8 -l 3 --style linear --output css
```

Result:
```css
box-shadow: 0px 3px 8px rgba(3 7 18 / 0.080),
            0px 5px 16px rgba(3 7 18 / 0.080),
            0px 8px 24px rgba(3 7 18 / 0.080);
```

Use when you want separation without "floating" the element much.

## Dark Mode Variant (same card as first example)

Add `--dark` (or manually raise opacity / use a lighter color).

The script boosts opacity ~1.9× while keeping the same progression.

## Tips for Full Elevation Scales

Call the generator multiple times with a geometric sequence of vertical values:

- xs: v=4–6, 3 layers, very low opacity
- sm: v=8–12, 3–4 layers
- md: v=16–20, 4 layers
- lg: v=28–32, 5 layers (the screenshot default)
- xl: v=40–48, 5–6 layers
- 2xl: v=56+, 6 layers, even lower base opacity

Store them as CSS custom properties or a Tailwind `boxShadow` theme extension.

## How to Regenerate Any Example

Every block above includes the exact command. Run it from the installed skill directory (or use the relative form `<this-skill-dir>/scripts/...` inside the agent).
