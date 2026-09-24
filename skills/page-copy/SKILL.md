---
name: page-copy
description: Writes or rewrites conversion copy for service-business homepages, landing, service, about and contact pages, delivering a wireframe, section copy annotated with rule IDs, headline and CTA alternatives, and an open-gaps list. Use for "write my homepage", "rewrite this hero", "landing page copy for my ads". For reviewing an existing page, use conversion-audit.
---

# Page Copy

Write the words for one page at a time: pick the structure, then write copy section by section so a stranger understands the offer in five seconds and knows what to do next. Scope is small and medium **service** businesses (trades, clinics, coaches, consultants, agencies, local pros). E-commerce catalogues are out of scope; SaaS pages only loosely fit. The output is copy plus a wireframe, not a design or HTML.

## Start with the business context

1. If `.agents/business-context.md` exists, read it first. Use it as the source of truth and ask only for what the page needs and the file lacks.
2. If it's missing, run a mini-brief, one question at a time:
   - Ideal customer: who, what situation, what they call the problem.
   - The site's one job: the primary action, and what happens after the click.
   - Offer and pricing stance: what is sold, and exact / from / ranges / factors / hidden.
   - Proof available: reviews (platform, rating, count), quotable clients, real numbers, photos.
   - Locale: country, languages, formality (je/u, tu/vous).
   For a full-site rewrite or a thin answer set, suggest running `site-brief` first and say why. Nobody available to answer: proceed on inferred values and list the questions under Open gaps.
3. If a page already exists, read it before writing (the URL via `agent-browser` or a plain fetch, or the repo's templates/content). Good lines are often already there, buried (BRIEF-01).
4. State every assumption you make in the output. Never invent proof: no testimonials, ratings, client counts, logos or results that the brief doesn't contain. Use placeholders such as `[PROOF NEEDED: testimonial about speed of delivery]`.

## Workflow

1. **Pin the job.** Decide four things before writing a word, and state them at the top of the output:

   | Decision | Options | What it changes |
   |---|---|---|
   | Page type | Homepage · service page · paid landing page · About · contact/booking · pricing · FAQ · testimonials | Structure: homepage type by offer mix (STRUCT-01) then the 10-section blueprint (STRUCT-02); service page wireframe (PAGE-01); paid LP order (STRUCT-03); About wireframe (ABOUT-01…07); other pages in `references/page-types.md` |
   | Traffic temperature | Cold organic · paid (ad click) · warm (referral, YouTube, AI assistant) | Cold: the full argument. Paid: dedicated page, eyebrow and headline echo the ad, no nav, 3–5 testimonials on the page (C2, STRUCT-03). Warm: shorter page, booking block high, full argument below (AI-04, C18) |
   | Sale type | Local/consumer · B2B complex sale | Consumer: reviews, faces and after-state images as proof; booking, quote or call CTA. B2B: proof = named case studies and client quotes (logos only with permission; PROOF-12); CTA = a discovery call that says who they'll talk to and for how long (CTA-02, BOOK-02); address both the champion and the decision maker (e.g. an FAQ or section for IT/DPO); price via ranges or a minimum project size (PRICE-03); hero image = the real product or deliverable in use (HERO-12) |
   | Locale | Language + country + formality | Write the copy in the business's language (Dutch for Flanders, French for Wallonia). BE/EU: apply `references/be-eu.md` (BE-01…07: transcreate, formality, booster words, place names, formats) |

   Allowed order deviations: emergency trades put benefits and proof straight after the hero; warm-traffic pages may merge problem and solution (C17).
2. **Fix the actions.** One primary action per page (CTA-01). Write its button text once (action verb + what happens next, CTA-02, never a CTA-03 phrase), its booster line (CTA-08), and process Step 1 in the same words (CTA-09). Pick the after-click path by business model (booking vs quote form vs call, C12). Add a transitional offer only as a subordinate text link or its own lower section (CTA-10, C1). Paid LPs get no secondary action.
3. **Write the hero.** Choose the headline formula by business type (HERO-02: transformation, problem, or plain what-you-do), anchored on the customer's desire, not your category (HERO-03). The subhead supplies the missing half: what/how, who, format, place (HERO-06). Add an eyebrow (HERO-08), three outcomes (HERO-09), one button + booster (HERO-10), real proof or a placeholder (HERO-11), and an image brief showing the customer's after-state (HERO-12). Check it against the seven failures (HERO-05) and the 5-second test (HERO-01).
4. **Lay out the sections.** Order from the chosen structure; one job per section; every heading is a mini-headline, not a label (STRUCT-06). Map proof to claims before writing body copy (PROOF-08).
5. **Write each section.** Customer words over industry words (COPY-01), "you" dominant except on About (COPY-02, C5), benefits first with the feature that enables them (COPY-04), specifics over clichés (COPY-11), grade 7–8 reading level (COPY-09; ≈ CEFR B1, "klare taal" in NL, "langage clair" in FR). Put each testimonial next to the claim it proves (PROOF-03, PROOF-07). Say something concrete about price (PRICE-01, PRICE-03). FAQ alternates real questions with objections and includes logistics answers (AI-01).
6. **Cut and sweep.** Cut the draft roughly in half where people decide (C3, copy-length table in `references/copy.md`). Run the copy QA sweep in that file (clarity → customer language → so what → prove it → specificity → emotion → zero risk → consistency → locale). Scan the banned-phrase list.
7. **Deliver** using the output contract below, then offer a de-AI pass (`humanizer` / `stop-slop`) and, for NL-BE copy, `belgisch-nederlands-redacteur` if available.
8. **Implementation is a separate step.** Don't produce HTML unless asked. If the project has a codebase and the user asks to implement, get the copy approved first, then build it in the project's existing components, or hand off. Ask before editing a live site or CMS.

## Output contract

Copy is in the page's language, at the COPY-09 reading level for that language; annotations and rationale are in the language the user writes to you in.

```markdown
# [Page] copy: [business name]

**Page type:** … · **Traffic:** cold / paid / warm · **Sale type:** consumer / B2B · **Language:** … (formality) · **Primary CTA:** "…" · **Secondary:** "…" or none
**Context used:** .agents/business-context.md (vN) / mini-brief / existing page at … · **Assumptions:** …

## Wireframe
| # | Section | Job on this page | Rules applied |
|---|---|---|---|
| 1 | Hero | What, why it matters, what next, why you | HERO-02 (formula 2), HERO-06, HERO-10, CTA-08 |
| 2 | … | … | … |

## Copy

### 1. Hero · HERO-02 (formula …), HERO-06, HERO-08, HERO-09, HERO-10, HERO-11
- Eyebrow: …
- Headline: …
- Subheadline: …
- Outcomes: … / … / …
- Button: … · Booster: …
- Proof: … or [PROOF NEEDED: …]
- Image brief: …
> Why: one line on the choice that matters.

### 2. [Section name] · [rule IDs]
- Heading: …
- Body: …
- Button (if any): same wording as the hero
> Why: …

(one block per wireframe row)

## Alternatives
**Headlines**
1. "…" · formula … · why / when to pick it
2. "…" · …
3. "…" · …

**Primary CTA**
1. "…" · …
2. "…" · …

## Meta (web pages)
- Title tag: … · Meta description: …

## Open gaps
- [PROOF NEEDED: …] → how to get it (PROOF-20)
- Assumptions to confirm: …
- Assets needed: real team photo, portfolio shots, …
- Decisions for the owner: e.g. price ranges public or gated (C13)
```

## Rules that matter most here

- **One reader, one page, one action.** Write to the brief's single ideal customer (BRIEF-02); one CTA, worded identically everywhere (CTA-01, CTA-04).
- **The hero carries the page.** Formula by business type (HERO-02); headline and subhead together answer what, for whom, why it matters (HERO-01, HERO-06). No "Welcome to", awards, clever puns or unexplained method names in the hero (HERO-05, BRIEF-07).
- **Clear beats clever.** Plain, conversational, the customer's verbatim phrases (COPY-01, COPY-08). Clever lines survive only if the next line resolves them.
- **Customer as hero, business as guide.** Lead with their problem and after-state; introduce yourself in the solution section with empathy plus authority (COPY-02, STRUCT-02 row 3). On a page, story means structure, not a "Meet Sally" tale (STORY-01, STORY-02).
- **Brag → benefit → proof.** Every claim answers "so what?" (COPY-03) and has proof within one scroll (PROOF-07). Unprovable superlatives get cut.
- **Specific or cut.** Numbers, timeframes, process details; unrounded numbers only if real (COPY-11, COPY-12, PROOF-10).
- **Talk about price.** Exact, from, ranges, factors or example jobs by pricing type (PRICE-03).
- **Short where people decide.** Hero = headline + one sentence + button; 3 benefits, 3 steps, ~6 FAQs (C3, copy-length table). About and advertorials may run long.

## References

| File | Read when |
|---|---|
| `references/principles.md` | Always skim first: the 15 principles, defaults when context is missing, contradictions C1–C21 and how to resolve them |
| `references/brief.md` | No context file exists, or you need the context template, voice-of-customer questions, or positioning rules |
| `references/hero.md` | Writing any hero: formulas, failures, anatomy, layouts by business type, rewrite gallery, 5-second test |
| `references/page-structure.md` | Choosing the homepage type and section order, paid/organic LP orders, story frameworks, nav, scannability |
| `references/page-types.md` | Service, multi-service, About, testimonials, contact/booking, FAQ and pricing pages |
| `references/copy.md` | Writing section copy: messaging rules, section headline formulas, storytelling, length table, banned phrases, QA sweep |
| `references/proof-trust.md` | Selecting and placing proof, no-testimonial fallbacks, comparison tables, guarantees, pricing display |
| `references/cta-forms.md` | Button wording, booster lines, booking vs form vs call, form fields, thank-you page |
| `references/lead-offer.md` | The page includes a transitional offer section, an opt-in page or a thank-you page |
| `references/ai-search.md` | FAQ and pricing copy that should answer AI-assistant questions; warm, pre-sold traffic |
| `references/be-eu.md` | The business is in Belgium or the EU: language, formality, legal footer, consent, reviews and price rules |
| `references/sources.md` | Checking where a rule comes from, or citing a source |

## Guardrails

- Truthful psychology only: scarcity, urgency, social proof, anchors and "as seen on" must be real and verifiable (principle 13, C14, C15).
- No invented proof. Missing proof becomes a `[PROOF NEEDED: …]` placeholder and an item in Open gaps.
- Stats in the references marked illustrative (Wes's and guests' numbers) explain direction. Never put them in client copy or quote them to a client as fact.
- Copy for regulated professions (medical, legal, financial) stays within their advertising rules; flag claims to check.
- Ask before publishing, pushing to a CMS, or editing a live site.

## Related skills

- `site-brief`: build or refresh `.agents/business-context.md` before a large rewrite.
- `conversion-audit`: find what's wrong with an existing page before rewriting it.
- `lead-offer`: design the transitional offer, its opt-in and thank-you pages, and the nurture emails.
- `humanizer` / `stop-slop` (if available): strip AI-writing patterns from the final copy.
- `belgisch-nederlands-redacteur` (if available): polish Belgian-Dutch copy.

Guidance distilled from Wes McDowell's YouTube channel (see references/sources.md). Structure ideas adapted from coreyhaines31/marketingskills (MIT).
