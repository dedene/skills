# Prompting image generators

## Contents
- Prompt anatomy
- Templates: render, metaphor object, design assist, style transfer, edits
- Style transfer library
- Reference images
- Meta-prompt: turn reference images into a written style guide
- Alt text

---

## Prompt anatomy

Build every render prompt from these blocks, in this order:

1. **Style block**: copy it verbatim from `style-guide.md`. Never paraphrase it between images in a series; consistency depends on identical wording.
2. **Scene**: the objects and their layout. Use absolute positions (left/right, top/bottom, center) and relative sizes ("the right circle is twice as large").
3. **Text**: every on-image string in double quotes, with its case and where it sits. Keep the total to about 12 words or fewer. End with "No other text."
4. **Emphasis**: the one element that carries the idea gets the accent color (see the accent rule in `style-guide.md`).
5. **Constraints**: aspect ratio (1:1 for social feeds, 4:5 for portrait feeds, 16:9 for slides), plenty of empty space, no extra icons or decoration, no watermark or signature.

Keep it literal. Describe what to draw, not what it means. "A bucket with holes in it" works. "The hidden cost of customer churn" doesn't.

---

## Templates

### Render a chosen concept
```
{STYLE BLOCK}
{Scene: objects + layout}.
Text: "{STRING 1}" {position}; "{STRING 2}" {position}. All caps hand-lettered. No other text.
Emphasis: {element} in {accent color}.
Aspect ratio {1:1}. Plenty of empty space. No icons, no shading, no decoration beyond what is described.
```

### Metaphor object (to trace or reuse)
```
Illustrate {object, e.g. "a lit match" / "a paper plane mid-flight" / "a hand holding a smartphone"}.
Style: simple outline, one thick black stroke, no shading, no color, smooth closed shapes, plain white background, centered, lots of empty space, clean SVG-like shapes that are easy to trace.
```
One object per image. For a family of objects, keep the style line identical.

### Design assist (an effect or cleanup the user can't draw)
Attach the user's element, then describe the change narrowly and say what must stay the same:
```
Redraw this {circle} so it looks like a slowly deflating balloon, sagging on one side. Keep the same marker style, line weight and size. Nothing else changes.
```
```
Tidy these arrows: 4 arrows of equal length converging on the word "SHIP" from the four corners, evenly angled. Keep the word, line weight and colors unchanged.
```

### Style transfer (user's rough sketch → styled)
Attach the sketch.
```
Restyle this sketch. Keep the composition, element positions and the exact text ("{STRING 1}", "{STRING 2}") unchanged; correct only obvious handwriting errors. {STYLE DESCRIPTION}. Keep the {small arrow / detail} pointing at {target}.
```
Name any small detail explicitly, because transfers tend to lose tiny arrows and fine marks.

### Edit follow-ups (prefer these over regenerating)
- `Change "{old}" to "{new}". Keep everything else identical.`
- `Make it square (1:1) without cropping any element or text.`
- `Remove {element}. Keep everything else identical.`
- `Make {element} smaller/larger; keep positions.`

---

## Style transfer library

Short, distinct style descriptions to swap into the style-transfer template. These are our own wording; tune them to taste.

| Name | Description |
|---|---|
| Black marker on white | Thick black marker on pure white, one accent color (red or green) for the key element, hand-lettered caps, no shading. |
| Notebook ballpoint | Blue ballpoint on lined notebook paper, slightly wobbly lines, doodle energy, visible paper texture. |
| Whiteboard | Quick dry-erase marker sketch on a whiteboard, one or two marker colors, loose arrows, faint smudges. |
| Flat infographic | Flat vector shapes, high contrast, bold sans-serif labels, two-color palette, modern and clean. |
| Ink + watercolor sketchbook | Loose expressive ink lines with soft watercolor washes on warm off-white paper, imperfect and lively. |
| Comic panel | Single comic panel: thick outlines, halftone dots, speech-bubble text, bold saturated contrast. |
| Napkin sketch | Quick pen drawing on a slightly crumpled paper napkin, casual and informal. |
| Chalkboard | White and pastel chalk on a dark green or black chalkboard, handwritten labels, light chalk dust. |
| Blueprint | Thin white technical lines on blue, small measurement ticks, labels in a technical font. |
| Mid-century print | 1950s print ad look: bold black ink, minimal flat color, slight halftone and paper grain. |

Style transfer is fast. Accuracy is decent, and consistency across a series is the weak spot. For a series, pick one style, fix its wording, and add style reference images.

---

## Reference images

- **Structure reference** (the user's sketch): "Use the attached sketch for composition and text only."
- **Style references** (past visuals, 3–7 images): "Match the line weight, lettering, palette and amount of whitespace of the attached reference images. Do not copy their subjects or text."
- Say which attachment plays which role when mixing both: "Image 1 is the layout to follow. Images 2–6 are style references only."
- More constraints give more consistency: fixed aspect ratio, exact background color, "use only these colors: #111111, #FFFFFF, #E63946", "same bold hand-lettered font as the references".

---

## Meta-prompt: reference images → written style guide

Run once with a vision-capable model and the user's 5–7 best visuals attached. Save the result into `style-guide.md` under the user's house style.

```
I want to create images in the exact visual style of the attached reference images, using a single text prompt without attaching the images.
Analyze them and write a reusable style block for an image generator. Cover: background (exact color as hex), line work (stroke weight relative to canvas, color, texture, wobble), lettering (case, weight, letterform description), color palette (hex codes and what each color is used for), use of whitespace and composition habits, level of detail, what never appears (shading, gradients, icons, etc.).
Output: 1) a compact style block of 60–100 words to paste at the start of prompts, 2) a list of do/don't rules, 3) one example prompt using the style block.
```

Then test it: render two concepts using only the text style block, compare them with the references in a contact sheet, and tighten the wording where they drift.

---

## Alt text

For every published visual, offer one or two sentences of alt text: what is drawn, what the text says, and the idea it conveys. Example: "Two identical buckets. The left one, labeled 'More leads', is full of holes and water sprays out under a running tap. The right one, labeled 'Fix the leaks first', is patched and filling up."
