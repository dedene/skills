# 40 — Conversion audit: checklist, killers, severity, measurement, test backlog

"Fix the bad food before moving the restaurant to a busier street": fix conversion before buying traffic `[W:t4gF4aVRcDY 2024]`. Audit in order of impact: **message → structure → proof → CTA → friction → tech** (the same ordering `[MS]` uses: value proposition first, friction last). Wes's own audit prompt asks for "a prioritized checklist, most to least impact" `[W:-n392pJo00I 2024]`.

## Step 0 — Scope, capture, context

- Which page: homepage first, then the page with the most traffic or ad spend; no data → the page or section carrying the primary or entry offer. One-page site, or an offer with only a card/section: audit that section plus its conversion path as the de facto landing page (A-S10).
- Page type (homepage, service, paid LP, About, pricing, opt-in) and its one conversion goal.
- Traffic source and temperature: paid social, Google Ads, organic, referral, YouTube, AI assistant, GBP. Paid → judge against the paid-LP order and message match. Paid + organic (a service page that also gets ad clicks) → C2 hybrid rule in `principles.md`.
- Device split (analytics), current conversion rate and lead quality if known, what's been tried `[MS]`.
- Capture desktop (1440 px) and mobile (390 px) screenshots, full page and above the fold: the fold **with** the consent banner, the rest after dismissing it [G].
- Run the 5-second test (A-M1) **blind, before** reading the context below, so the score reflects a stranger.
- `.agents/business-context.md` (template in `brief.md`); if missing, draft it from the page first (BRIEF-01). Nobody to answer → proceed on inferred context and list questions for the owner.

## Step 1 — Message

| ID | Check | Default severity if failed |
|---|---|---|
| A-M1 | 5-second test passes: what, why it matters, next step (+ why you) (HERO-01; pass rule and scoring only in `hero.md`, 5-second test protocol) | Critical at ≤ 4/10 or a 0 on What/Next step; High at 5–6/10 |
| A-M2 | Headline uses the right formula for the business type; not mysterious, clever, cliché, jargon, unresolved, platitude or SEO-stuffed (HERO-02, HERO-05) | High |
| A-M3 | Subhead supplies what/how + who (+ format, timeline, location where relevant) (HERO-06) | High |
| A-M4 | Customer language: pain and outcome phrases sound like customers, not the industry; jargon count ≈ 0 (COPY-01) | High |
| A-M5 | Customer is the hero: no "Welcome to", awards, origin story or self-label ("AI-first studio · since 2009") above the fold; French test passes (COPY-02) | High |
| A-M6 | Sells the after-state; benefits before features; "so what" answered (COPY-03, COPY-04) | Medium |
| A-M7 | Specific, not clichéd; numbers exact (COPY-11, COPY-12) | Medium |
| A-M8 | Differentiation visible: why you, named method or niche, #1 objection answered somewhere (BRIEF-07/08) | Medium |
| A-M9 | Says what you are early (not in section 3) (COPY-10) | High |
| A-M10 | Message match for paid traffic: headline, offer and visual style echo the ad (STRUCT-03) | Critical for paid LPs; High on hybrid paid + organic pages |
| A-M11 | Ad routing: each ad group or keyword lands on the page that answers its query, not a generic page when a dedicated one exists (PAGE-04, STRUCT-03) | High |

## Step 2 — Structure

| ID | Check | Default severity |
|---|---|---|
| A-S1 | Homepage type fits the offer mix (landing page vs router) (STRUCT-01) | High |
| A-S2 | Section order follows the blueprint; missing sections flagged: problem, solution/guide with a real human, benefits (3), process (3 steps), testimonials, FAQ, final CTA (STRUCT-02) | High (missing problem/process/final CTA); Medium (others) |
| A-S3 | Nav ≤ 5 items + CTA button top right; no social icons, client login or mega menu in the header; paid LP without nav (STRUCT-05) | Medium (High on paid LPs with nav and links out) |
| A-S4 | Scannable: headings as mini-headlines, 2–3-sentence paragraphs, bullets, bold key ideas, no walls of text (STRUCT-06) | Medium |
| A-S5 | Prototypical layout; no clutter, sliders, parallax or competing decorative elements; enough white space (STRUCT-07/08, HERO-18) | Medium |
| A-S6 | Images: after-state customers in the hero; real team/work; consistent style; sharp; no cheesy stock (HERO-12/13, STRUCT-09) | High (hero), Medium (elsewhere) |
| A-S7 | Service pages built like homepages, not SEO text walls (PAGE-01) | High |
| A-S8 | Copy length: homepage not "a small book"; hero = headline + one sentence (`copy.md`, copy-length rules) | Medium |
| A-S9 | Transitional offer exists and is secondary (LEAD-01) | Medium |
| A-S10 | Every offer that is sold or advertised, including the entry offer, has its own page; an offer that exists only as a card or section is itself a finding (PAGE-04) | High if it is the primary or advertised offer; Medium otherwise |

## Step 3 — Proof

| ID | Check | Default severity |
|---|---|---|
| A-P1 | Proof above the fold (rating + count, faces, a stat or quote) (HERO-11) | High |
| A-P2 | Testimonials are stories/results with photo, name, result headline, from clients who mirror the target customer; no blobs, no anonymous "great service" (PROOF-01/04/06) | Medium |
| A-P3 | Proof placed next to the claims it supports and near CTAs (PROOF-07) | Medium |
| A-P4 | A human face, name and city appear on the homepage (solution section) (PROOF-14) | High for low-trust industries, Medium otherwise |
| A-P5 | Price addressed: price, range, factors or estimator (PRICE-01/03) | High |
| A-P6 | No fake or unverifiable proof: paid "as seen on", invented counters, stock "customers" with quotes, fake scarcity (PROOF-12/13, SCAR-01) | Critical (legal/trust risk) |
| A-P7 | Comparison (if present) is balanced and includes doing nothing (PROOF-22) | Low |
| A-P8 | Reviews shown with source and date; link to the full profile (PROOF-12; BE rules) | Medium |
| A-P9 | Facts consistent across pages: numbers and claims (client counts, years, positioning, service list) match between pages, footer, docs and profiles, and are sourced (AI-03). Unsourced but plausible → here; invented → A-P6 | High |

## Step 4 — CTA

| ID | Check | Default severity |
|---|---|---|
| A-C1 | A primary CTA exists in the hero and nav | Critical if absent |
| A-C2 | Wording specific (verb + what happens next); none of the banned phrases (CTA-02/03) | High |
| A-C3 | Identical text and style everywhere, including the nav button vs the hero CTA; repeated at ≥ 3 depths on long pages (CTA-04/06) | Medium (High when the nav button competes with a different filled hero CTA) |
| A-C4 | Reserved, high-contrast, filled color not used elsewhere (logo, icons, headings) (CTA-05) | Medium |
| A-C5 | One filled button in the hero; secondary visually subordinate; lead magnet not primary (HERO-10, CTA-10) | Medium |
| A-C6 | Booster line under the main CTA (CTA-08) | Low (quick win) |
| A-C7 | Final CTA section / TL;DR panel at the end (STRUCT-02 #10) | Medium |
| A-C8 | Process Step 1 uses the CTA wording; the click delivers what the label promised (CTA-09/12) | Medium |

## Step 5 — Friction

| ID | Check | Default severity |
|---|---|---|
| A-F1 | Post-click path fits the model: scheduler for consults, short quote form, click-to-call for urgent; no mystery "Contact us" form (`cta-forms.md`, after-the-click table) | High |
| A-F2 | First-contact form ≤ 3–4 fields + 1 qualifier; visible labels; correct mobile keyboards; helpful errors (FORM-01…06) | High if ≥ 7 fields |
| A-F3 | Thank-you page sets expectations and offers the next step (THANKS-01/02) | Medium |
| A-F4 | No instant pop-ups or chat bubbles; exit intent only; cookie banner doesn't block the hero CTA (HERO-20, `be-eu.md`) | High on mobile |
| A-F5 | No links out to social feeds; no bare email as the main path (STRUCT-05). Every CTA a `mailto:` → report as A-F1 High (`cta-forms.md`, after-the-click table) | Low |
| A-F6 | Booking flow has no redundant clicks; data prefilled (BOOK-01) | Medium |
| A-F7 | Choice overload: too many services/packages/actions on one screen → trim or package finder (PAGE-05) | Medium |

## Step 6 — Tech

| ID | Check | Default severity |
|---|---|---|
| A-T1 | Mobile renders correctly: no hover-only content, no broken video, CTA visible above the fold (STRUCT-12) | Critical if broken |
| A-T2 | Speed: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 (field data from PageSpeed Insights / CrUX; otherwise a throttled lab run, reported as "lab only"; a warm local browser session is no signal); heavy images/video/third-party embeds lazy-loaded [G] (STRUCT-13) | High if LCP > 4 s |
| A-T3 | No broken images, links, forms or scheduler embeds; test a real submission `[W:3ahiFlIHvDc 2022]` | Critical if the form fails |
| A-T4 | Conversions tracked: bookings, form submits, call clicks, opt-ins; thank-you URLs/events (THANKS-04) [G] | High (no measurement = no iteration) |
| A-T5 | Accessibility basics: contrast ≥ 4.5:1, labels on fields, alt text, keyboard focus, heading order [G] | Medium |
| A-T6 | SEO basics without hurting the message: title tag and meta description, service + location in the subhead or H1, specific section headings, LocalBusiness structured data (Organization/ProfessionalService for non-local B2B), consistent NAP with GBP [G] `[W:64ie_-xuMgQ 2021, RlMBBbXzQ84 2023]` | Medium |
| A-T7 | BE/EU compliance: legal info (company number, address, email), privacy notice, cookie consent with an equal reject option, review disclosure (`be-eu.md`) | High (legal) |

## Conversion killers: the "remove" list

Subtraction usually beats addition `[W:dUrlwvm-CqQ 2024, pRNny_t8TUE 2025]`:

1. "Welcome to…", awards or a giant logo in the hero `[W:7kG8otQJfws 2021, 8ZX9y8GP0xs 2022]`
2. Sliders/carousels, rotating taglines, busy multi-cut hero video `[W:_hBEZT8-uOw 2018, 2lYdI86YV30 2023]`
3. Hero photos of you/the team, skylines, buildings, empty rooms, "the sausage being made" `[W:OvQvDu5ZKzQ 2020, g_Wk6nJD1_Y 2025]`
4. Cheesy, over-posed stock ("people wonder what else here isn't real"); stock or AI photos of the team `[W:dUrlwvm-CqQ 2024]`
5. Crazy color schemes, clashing gradients, the CTA color reused elsewhere `[W:dUrlwvm-CqQ 2024]`
6. Several different CTAs; "Learn more / Get started / Contact us / Submit" `[W:8ZX9y8GP0xs 2022]`
7. Bloated nav, two-row menus, mega menus, client login top right `[W:dUrlwvm-CqQ 2024, 7hhQf3T3k-Q 2019]`
8. Social icons and embedded Instagram feeds `[W:dUrlwvm-CqQ 2024]`
9. Team-bio grids with hobbies and personal social links `[W:dUrlwvm-CqQ 2024, bYZkDOwQxfg 2022]`
10. Vague "Contact us" forms; long first-contact forms; a published email address as the main path `[W:dUrlwvm-CqQ 2024, ClD037qJSTQ 2025]`
11. Jargon, clichés, "tailored to your unique needs", walls of text `[W:t4gF4aVRcDY 2024, g_Wk6nJD1_Y 2025]`
12. Off-message content (the office coffee slide at a physio clinic) `[W:7kG8otQJfws 2021]`
13. Parallax, heavy animation, decorative elements that attract dead clicks `[W:pRNny_t8TUE 2025]`
14. Instant chat/welcome pop-ups `[W:7hhQf3T3k-Q 2019]`
15. Leftover template sections and unused social icons `[W:trfDoGoXNsE 2025]`
16. Dozens of thin pages that scatter the story `[W:8ZX9y8GP0xs 2022, jPclFEiC2o4 2023]`

## Severity rubric and output buckets

| Severity | Meaning | Examples |
|---|---|---|
| **Critical** | Blocks or breaks conversion, or creates legal/trust risk | No CTA; 5-second test ≤ 4/10; broken form or booking; mobile broken; fake proof; paid LP mismatched with the ad |
| **High** | Materially lowers conversion for most visitors | 5-second test 5–6/10; vague CTA wording; business-centric hero; no proof above the fold; no price info; mystery contact form; no human visible; LCP > 4 s |
| **Medium** | Noticeable drag or missed opportunity | Missing process section; CTA not repeated; nav bloat; blob testimonials; inconsistent images |
| **Low** | Polish | Booster line missing; comparison unbalanced; icon pack mismatch |

Map findings to the output format (from `[MS]`):

- **Quick wins (do this week):** ≤ ~1 hour each, low risk, high confidence. Typical: rewrite the CTA wording and make it identical; add the booster line; move the logo; add the nav CTA button; add the review count to the hero; cut the nav to 5; remove social icons; replace the hero photo; add one real team photo; fix contrast.
- **High-impact changes (prioritize):** bigger work with high expected impact. Typical: rewrite the hero with the right formula; restructure to the blueprint; build service pages like homepages; add pricing ranges; switch to a scheduler; build the transitional offer; collect real testimonials with photos.
- **Test ideas:** plausible but uncertain, and only worth an A/B test with enough traffic (below). Otherwise ship and compare before/after.
- **Copy alternatives:** for the headline, subhead and CTA (plus booster line or eyebrow when that's the fix), 2–3 options each with a one-line rationale citing the rule `[MS]`. Write them in the page's language; findings stay in the user's language.

Each finding: `ID · Severity · Effort (S/M/L)`, then Evidence (quote, selector or screenshot region) · Why (rule ID + mechanism) · Fix (concrete copy or change).

Order within each bucket by severity, then by position on the page (hero first).

## Measurement and iteration

**MEAS-01 — Most SMB sites can't run valid A/B tests.** Sample size grows fast at low baselines: at a 3% conversion rate, detecting a 20% relative lift needs roughly 14,000 visitors *per variant*; a 50% lift ~2,500 per variant (80% power, α 0.05) `[MS]`. A site with 1,500 visits a month can't test button colors. Instead:
- Ship high-confidence fixes (rules above) and compare **before/after** over equal periods (≥ 4 weeks, same season; 8–12 weeks for low-volume B2B, plus lead-quality notes from sales calls), watching leads, booked calls and lead quality, not just clicks [G].
- Use qualitative evidence: 5-second tests with 5 people, session recordings, heatmaps for **dead clicks** and whether anyone clicks the CTA `[W:pRNny_t8TUE 2025]`, form-field drop-off `[MS]`.
- Reserve A/B tests for high-traffic pages (paid LPs with budget) and big swings (headline angle, page length, offer), never micro-tweaks `[MS]` `[W:OtChoVhEI8Y 2025]`.

**MEAS-02 — Define conversions properly [G].** Primary: booked appointments, qualified quote requests, calls over X seconds. Secondary: opt-ins, estimator completions, CTA clicks. Guardrails: no-show rate, lead quality (share that fit the brief), spam. Add "How did you find us?" (incl. AI assistant, YouTube, Google, referral) to the booking or intake form; this is the only practical way to see AI-sourced leads `[W:VXGDHZIGf40 2026]`.

**MEAS-03 — Hypothesis format `[MS]`:** "Because [observation], we believe [change] will cause [outcome] for [audience]; we'll know when [metric] moves by [amount] over [period]." One change per test; decide the sample size and duration up front; no peeking.

**MEAS-04 — Cadence [G].** Month 1: fix Critical + Quick wins. Month 2: High-impact rewrites (hero, structure, pricing, booking). Month 3: transitional offer + nurture. Then quarterly: re-run the 5-second test, refresh testimonials and stats, prune pages. The v1 guide's 30-day rollout follows the same order (message → hero → structure → capture); Wes himself only claims results "in 21 days, maybe less" when starting with the website (illustrative) `[W:bWVyN9VoBB4 2026]`.

**MEAS-05 — Don't chase hacks while the message is broken.** Of 120+ tweaks Wes says he tested, only nine moved conversions (no methodology; illustrative) `[W:mGbLhEY7nPE 2024]`, and Talia Wolf found element-level hacks rarely worked until messaging changed (teamwork.com: +54% signups, 7× homepage conversion; illustrative) `[W:OtChoVhEI8Y 2025]`.

## Traffic quality

- **Return visits beat new visits:** build reasons to come back (lead magnet + email teasers linking to site content; retargeting where consent allows) before buying more cold traffic `[W:cqh4JDnX6KU 2022]`.
- **Paid traffic → dedicated offer page** with visual continuity; never the homepage `[W:kZdXTq5uOEI 2021]`.
- **Awareness mix:** run a pre-sell article next to direct offer pages for less-aware prospects `[W:WktIWzpeMis 2020]`.
- **Warm traffic** (referrals, YouTube, AI recommendations) arrives pre-sold: check that the booking path is fast and visible, and that the page doesn't over-sell `[W:VXGDHZIGf40 2026]`.
- **Promote the lead magnet**, not the brand, in cold ads `[W:1RGMHttqQN4 2019]`.
- In GA4, bounce rate is just 1 − engagement rate; judge pages by engagement rate and conversion events [G].

## Test ideas backlog (SMB-specific)

Pick only those your traffic can support; otherwise treat as before/after changes.

| Area | Test | Hypothesis source |
|---|---|---|
| Hero | Result headline vs problem headline vs plain what-you-do | HERO-02 |
| Hero | Customer after-state photo vs photo of the finished work | HERO-12/15 |
| Hero | Proof row (faces + stars + count) vs none | HERO-11 |
| Hero | Hero outcome checkmarks vs none | HERO-09 |
| Hero | Text-link transitional offer under the button vs none (C1) | CTA-10 |
| Hero | Eyebrow matching the ad vs generic | HERO-08 |
| CTA | "Book a free consultation" vs "Plan a free 20-minute call" (specificity of duration) | CTA-02 |
| CTA | First person ("my") vs "your" (per language) | CTA-11 |
| CTA | Booster line variants: time vs no-obligation vs response time | CTA-08 |
| Proof | Testimonial next to each benefit vs a single testimonial block | PROOF-07 |
| Proof | Video testimonial with TL;DW headline vs text | PROOF-09 |
| Pricing | Ranges on the page vs "request a quote" only | PRICE-01 |
| Pricing | Estimator vs static ranges | LEAD-13 |
| Structure | Short page vs full blueprint for warm (referral/YouTube) traffic | C18 |
| Structure | "Wild card" objection section vs none | STRUCT-02 |
| Forms | Scheduler vs short form (consult businesses) | `cta-forms.md`, after-the-click table |
| Forms | Phone field removed vs optional vs required | FORM-02 |
| Forms | Multi-step quote form starting with service buttons vs single step | FORM-04 |
| Lead | Quiz/package finder vs checklist as transitional offer | LEAD-12 |
| Lead | Email-only vs email + name on opt-in | `[MS]` |
| Scarcity | Truthful capacity line near the CTA vs none | SCAR-02 |
| Mobile | Sticky bottom call/booking bar vs none | STRUCT-12 |
