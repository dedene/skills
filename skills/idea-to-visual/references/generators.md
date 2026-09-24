# Generators

The skill doesn't depend on any one tool. Use the first one that is reachable, in this order: the one the user names, then Higgsfield, then any other image-capable tool in the session. "Reachable" means it answers a single probe (`"$MCP" list <server>`, see below) in this session. Don't retry a failed probe in a loop. If none is reachable, deliver prompts ready to paste.

## Higgsfield (MCP via mcporter)

MCP servers are called through mcporter, never as native MCP tools. Use the executable in `MCPORTER_BIN` when it is set (hosts that need a credential wrapper set it); otherwise use the installed `mcporter`:

```bash
MCP="${MCPORTER_BIN:-mcporter}"
```

1. **Check status**: `"$MCP" list higgsfield`
   - If it says `auth required`, stop and ask the user to run `"$MCP" auth higgsfield` themselves. It is an interactive browser OAuth, so don't try to automate it.
2. **Discover tools**: `"$MCP" list higgsfield --schema`. Read the tool names, parameters, and model/aspect-ratio options from the schema. Don't assume names from memory; they change.
3. **Pick a model**: prefer one that renders text well and accepts reference images (e.g. Nano Banana / Gemini image or GPT image variants when offered) for concept visuals with lettering. Prefer the model's native aspect-ratio parameter over asking in the prompt.
4. **Call**: `"$MCP" call higgsfield.<tool> key=value ...` (quote values that contain spaces). For long prompts, write the prompt to the run folder first and pass it in the way the schema allows. Pass reference images the way the schema expects: URLs, uploads, or file paths.
5. **Collect**: generation may be asynchronous and return a job id. Poll the status tool from the schema, then download the result into the run folder (`curl -sSL -o <run>/<n>.png <url>`).
6. **Record**: append the tool, model, parameters and job id to `prompt.md`.

## Other tools

- **Gemini / Nano Banana** (app or API): strong text rendering, good with multiple reference images and conversational edits. Use it for style references and "change X" edits.
- **ChatGPT image**: strong text, good at style transfer from a photographed sketch and at conversational edits.
- **Midjourney-style models**: beautiful but weaker at exact text and layout. Render without text and add lettering afterwards, or avoid for text-heavy concepts.
- **No generator available**: output the final prompt(s) in fenced blocks, one per variant, with the aspect ratio and any reference-image roles listed above each.

## Run folder

```
./visuals/<YYYY-MM-DD>-<slug>/
  prompt.md        # idea, chosen concept, exact prompts, tool/model, params, reference paths
  01.png, 02.png…  # outputs, numbered in generation order
  sheet.png        # contact sheet when comparing > 2
```

## Contact sheet (compare variants at a glance)

```bash
FONT=/System/Library/Fonts/Supplemental/Arial.ttf   # macOS; elsewhere any .ttf path, e.g. from `fc-list`
magick montage -font "$FONT" -label '%f' <run>/0*.png \
  -tile 3x -geometry 600x600+16+16 -pointsize 22 -background white <run>/sheet.png
```
`-label` must come before the input files or the labels are silently dropped. Pass `-font` explicitly, because some ImageMagick installs have no default font and fail with "unable to read font".

Give the user absolute paths to the sheet and to each file.

## Verifying output

Open every generated image before reporting. Check:
- the on-image text is spelled exactly as quoted, with no extra text
- the core idea is readable in 3–4 seconds
- there are no invented icons, clutter or lost details (small arrows)
- the style matches the style block and references

Fix failures with targeted edit prompts, and say plainly in the report which issues remain.
