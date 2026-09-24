# Style guide

Paste the chosen style block verbatim at the start of every render prompt in a series. Change a style only by editing it here, so every later prompt picks up the change. Style blocks never set the aspect ratio; that goes in the prompt's constraints, per channel.

**Accent color rule:** give the accent to the one element that carries the idea. That's the thing that changes, the side that wins, or the point the arrow lands on. Never give it to decoration. In comparisons, red marks the problem side and green marks the good side (use both only when the contrast is the idea).

## Default: trace-ready marker (use when no house style is set)

```
White background, simple thick black marker lines, no shading, no gradients, no textures, plenty of empty space, centered composition, clean shapes that are easy to trace, bold hand-lettered all-caps text.
```

Optional accent: add `One accent color only: red (#E63946) for the key element.` (or green `#2A9D8F` for the positive side of a comparison). Use accents for meaning, never for decoration.

## Default: finished minimal post

```
Minimal hand-drawn explainer illustration on an off-white background (#F7F7F5). Confident black marker strokes of even weight, slight hand-drawn wobble, no shading or gradients. Bold rounded hand-lettered all-caps text. Palette: black #111111, accent red #E63946 (optional second accent green #2A9D8F for the good side of a comparison), optional soft gray #D9D9D9 fills. Generous whitespace, one focal element.
```

## House style (user's own) — not set yet

To fill in: run the meta-prompt in `prompting.md` with 5–7 of the user's best visuals. Then paste the resulting style block, the do/don't rules and the reference image paths below.

```
<style block>
```

- Reference images: `<absolute paths>`
- Do: …
- Don't: …

## Rules learned from rejected outputs

Append a line every time an output is rejected for a reason that will come up again.

- Never add icons, emoji or decorative elements that aren't in the concept.
