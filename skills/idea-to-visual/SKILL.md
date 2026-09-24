---
name: idea-to-visual
description: This skill should be used when turning an idea, quote, insight, book chapter, post, or talk section into a simple explanatory visual (concept sketch, visual metaphor, comparison, diagram-style illustration) and when prompting image generators for it — Higgsfield (via mcporter), Gemini / Nano Banana, ChatGPT image, or any other image tool, with or without reference images. Covers visual/element brainstorming, concept critique and captions, generator-ready prompts, style transfer of rough sketches, tracing-friendly metaphor objects, and a consistent house style. Triggers on "visualize this idea", "make a visual for", "illustrate this concept", "run VB / EB / CB" (visual, element, caption brainstorm), "style transfer my sketch", "caption for this visual".
---

# Idea to Visual

Turn one idea into one clear, simple visual that lands in a few seconds. Image models are good renderers and poor concept-makers. Given a bare prompt like "illustrate this quote", they produce average, literal images. The value is in the brainstorm before the prompt. This skill runs that brainstorm, filters the concepts hard, and only then writes the prompt and generates the image.

## Core principles (apply to every step)

1. **One idea per visual.** Pick a single takeaway. This is not an infographic.
2. **Clarity beats cleverness.** If a clever version confuses, drop it. Test: would a stranger get it in 3–4 seconds, even if they disagree with it?
3. **Novelty.** Show a familiar idea from an unexpected angle, through an unexpected combination, or so simply that it feels new.
4. **Resonance.** Name what the audience feels, fears, thinks, or says. Relatable moments beat abstractions.
5. **Amplify, don't repeat.** The text and caption should add a punch, a question, or advice on top of the image, not describe it.
6. **Flow.** Elements and words should read in order and click together, sometimes with a rhythm or rhyme ("easy to start / hard to stop").
7. **Few words, few text placements, big shapes.** Generators drop small details like tiny arrows and fine labels, and extra text clutters. Keep total on-image text short.
8. **Taste is the filter.** Most generated concepts are mediocre. Treat them as fuel for the next step, and pull out useful fragments (a layout, a metaphor, a phrase) even when the whole concept fails.

## Pick the mode

Infer the mode from the request. Ask only when the source idea itself is missing.

| Mode | When | Output |
|---|---|---|
| **EB: Element Brainstorm** | An idea to explore; stuck; default first step | 10–15 one-line text elements + ~12 one-line visual elements |
| **VB: Visual Brainstorm** | Ready for concrete concepts | Core insight + style block once + 10 concept paragraphs (one per visual lane) + Top 3 |
| **Render** | A chosen concept (or a VB paragraph) | Final prompt + generated image(s) + short critique |
| **CB: Critique & Caption** | A finished or draft visual (image attached) | Checklist scores with one fix each + 6 caption options |
| **Style transfer** | User supplies a rough sketch/photo | Restyled image that keeps the composition and text exactly |
| **Metaphor object / design assist** | Need one object or effect to trace or reuse | Tracing-friendly single-object image |
| **Chapter expansion** | Long or dense source (chapter, article, transcript) | Expansion notes + 4 plain-language concept statements, then EB/VB on the best one |

The full method for EB, VB, CB and chapter expansion is in `references/method.md`. Load it before running any of those modes.

## Default end-to-end workflow

When the user says "make a visual for X" without naming a mode:

0. **Load.** `references/method.md` and `references/style-guide.md`. Settle the output intent (below) and the channel's aspect ratio (1:1 feed, 4:5 portrait feed, 16:9 slides).
1. **Core insight.** Restate the one takeaway in a single plain sentence (roughly 10-year-old reading level). Skip stories and side details. Name the audience if it's known.
2. **Compact EB.** Print about 6 text elements and about 6 visual elements. Run the full-size EB only in standalone EB mode.
3. **VB.** 10 concept paragraphs across the visual lanes, then a **Top 3** with one line each on why it's strong. Refer to concepts by lane number.
4. **Choose.** In an interactive chat, **stop here** and ask the user to pick from the Top 3, unless they said "just pick", "go ahead", or are running this unattended. In that case pick the strongest, state why, and continue.
5. **Render.** Load `references/prompting.md` and `references/generators.md`. Build the prompt with the full style block pasted verbatim. Generate 2–4 variations if the tool allows; with no generator, write 2 prompt variants in the fallback format from generators.md.
6. **Review.** Open every output image. Check that the text is spelled right, the core idea reads in 3–4 seconds, and no extra icons or clutter crept in. Fix with targeted edit prompts ("change 'plan' to 'habit'", "make it square", "remove the extra arrow") instead of regenerating from scratch. Skip this step when no image exists.
7. **Wrap-up.** Give 6 captions, a scorecard for the final pick, and alt text. Without an image, score the concept and label the scorecard "provisional".

If the user explicitly wants a quick render and no brainstorm, do it, and add one line saying the output will be generic without a brainstorm.

## Output intent decides the style

Establish which of these applies. Infer from context and state the assumption.

- **Trace-ready draft** (default for professional or book work): white background, thick black strokes, no shading, lots of empty space. The user will redraw it in Figma or FigJam in their own line weights, so accuracy of shapes matters more than polish.
- **Finished post**: apply the house style from `references/style-guide.md` so a series stays consistent. If no house style is set, use its "Default: finished minimal post" block.
- **Authentic hand-drawn look**: deliberately imperfect marker, whiteboard or notebook styles. Consider this when the audience is tired of glossy AI images.

## Reference material

- **User's sketch as structure reference**: keep its composition, element positions and exact text. Change only the rendering style. Sketches with big, broad shapes transfer well. Tiny details get lost, so call them out explicitly in the prompt.
- **Style reference images** (the user's past visuals): attach them and say to match line quality, font, palette and whitespace, and not to copy their content. For recurring use, convert them once into a written style guide with the meta-prompt in `references/prompting.md`, then store it in `references/style-guide.md` so later prompts work without re-uploading.
- **No references**: rely on the written style block. Expect some drift between images, and keep the style block identical across a series.

## Generating images

Use whatever image tool is available. `references/generators.md` gives the order to try tools in, how to check Higgsfield via mcporter (probe it once), and the fallback format. When no generator is reachable, deliver the prompts in that fallback format and say so.

Save every run under `./visuals/<YYYY-MM-DD>-<slug>/` in the current project unless the user names another location, and do this even when only prompts were produced. Put a `prompt.md` in the folder with the idea, the chosen concept, the exact prompt(s), the tool/model and the reference files used, so any image can be reproduced or iterated. When comparing more than two variants, build a labeled contact sheet (command in generators.md) and give its absolute path.

## Gotchas

- Critique prompts drift toward "add icons, add color, add detail". Reject suggestions that fight simplicity or change the concept.
- Style drifts between generations even with the same prompt. Fix the style block and reuse the reference images, and don't expect pixel-level consistency.
- Model text rendering is now mostly reliable. Still quote every on-image string exactly, give its case, and state "no other text".
- Iterate by conversation: small follow-up edits usually beat a rewritten prompt.
- Refine the prompts in this skill over time. When the user rejects an output for a reason that will come up again, add that rule to the relevant reference file.
