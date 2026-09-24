---
name: site-brief
description: Builds or refreshes .agents/business-context.md for a service business website, auto-drafting from an existing URL, repo or copy and then interviewing only for gaps. Use for "website brief", "business context", "who is my ideal customer", or before auditing or rewriting a site. For audits use conversion-audit; for writing pages use page-copy.
---

# Site Brief

Build the brief that every conversion skill reads first: `.agents/business-context.md`. Draft it from what already exists (live site, repo, reviews), then interview the owner one question at a time for what is missing or uncertain. Messaging comes before copy, and copy before design; this file is the messaging. Scope: websites of small and medium service businesses (trades, clinics, coaches, consultants, agencies, local pros). Not e-commerce catalogues. SaaS fits only loosely, because the template assumes a consult, quote or booking sale.

## Context step

1. Look for `.agents/business-context.md` in the project root.
   - **Exists:** read it. Report its version, the last two changelog entries, and every field still `inferred` or `missing`. Ask which sections to refresh and touch only those.
   - **Missing:** this skill creates it. If `.agents/product-marketing.md` or an older brief exists, read it as a source. Don't move or delete it.
2. One file per site. A sub-brand with its own site gets its own file in its own project; with a rebuild in flight, use the repo that will be live next and say where you put it. If the repo serves several brands, ask which one this brief is for.

## Workflow

1. **Collect sources before asking anything (BRIEF-01).** Owners describe their business in insider language; the existing site and reviews often hold better lines.
   - **URL:** use `agent-browser` if available, otherwise a plain fetch. Read home, services, about, pricing, contact, reviews/testimonials; about ten pages is enough. Log every URL used.
   - **Repo:** README, PRODUCT.md, AGENTS.md, content or copy folders, locale files, CMS exports, meta descriptions.
   - **Reviews:** the owner's and competitors' reviews, for verbatim customer language (BRIEF-11). Keep the source URL next to each phrase.
   - **Internal docs:** strategy notes, business cases, decision logs. Record each doc's date; dated owner decisions outrank the live site.
   - **B2B, where reviews are rare:** proposals, sales-call notes, RFPs, LinkedIn posts and comments.
2. **Auto-draft every field** of the template in `references/brief.md`, and tag each one:
   - `confirmed`: the owner stated or approved it in this session, or an earlier version confirmed it and nothing contradicts it.
   - `decided: <doc, date>`: an owner decision recorded in a dated internal doc, not re-confirmed this session.
   - `inferred: <source>`: drafted from a page, file or review, not yet approved. Text on the owner's own site is still inferred; old sites often say what the owner no longer means. A plan or recommendation in a doc is `inferred: <doc> (planned)`, not a decision.
   - `conflict: <source A> vs <source B>`: sources of equal rank disagree. Goes first in the owner questions.
   - `missing`: no evidence. Leave it empty. A plausible guess is worse than a gap; unsourced hypotheses go only in the owner questions, never in a field.

   **Source precedence:** owner in this session > dated owner decisions in docs > live site > older or undated docs. When precedence settles a disagreement, use the winner and log the loser under *Conflicts & weak spots*.
3. **Settle four decision points early**, because later answers depend on them:
   - **Locale.** Service area, languages, formality. Belgian or EU business (`.be` domain, KBO/BCE number, NL/FR copy) → read `references/be-eu.md` and record: languages the team can actually serve in (BE-01), formality per language (BE-03), legal identification fields (BE-08), VAT status of prices (BE-20), professional-body limits on proof (BE-26).
   - **Sale type.** Consumer/local vs B2B complex sale. B2B → fill the template's B2B block (buyer vs user role, buying group, sales cycle, minimum project size, procurement or public tenders, DPA/security expectations) and skip the B2C-only fields (life stage, self-/social image) (BRIEF-02).
   - **Offer mix → homepage type (BRIEF-06).** One offer brings ≥ ~80% of revenue → the homepage is that offer's landing page. One offer slightly dominant → flagship-weighted. Roughly equal → a router with one headline covering both. No revenue split yet (new brand or sub-brand) → decide by the strategic priority offer and record why.
   - **Traffic temperature (BRIEF-15).** Share of cold search, paid, and warm traffic (referrals, YouTube, AI assistants). Paid traffic → note that it needs a dedicated landing page. Mostly warm → note a shorter page and faster booking (principle 15).
4. **Interview the gaps, one question at a time**, in this priority order. Show the inferred value first ("Your site says X. Right, or what's different?"); that is faster than an open question. Use the matching question from the interview script in `references/brief.md` and confirm each block back in one sentence.
   1. **Ideal customer:** one person (B2B: a role and its buying group), their situation, the trigger event, the anti-persona (BRIEF-02, BRIEF-03).
   2. **The site's one job:** primary CTA, what happens after the click, what it costs the prospect (BRIEF-04).
   3. **Transitional offer** for visitors not ready to buy (BRIEF-05). "None yet" is a valid answer; record it and point to `lead-offer`.
   4. **Proof inventory:** reviews (platform, rating, count, date checked), testimonials with permission, unrounded numbers, earned logos (BRIEF-10).
   5. **Differentiation:** positioning statement, one-liner under 20 words, named signature method, #1 objection, alternatives including DIY and doing nothing (BRIEF-07, BRIEF-08).
   6. **Pricing stance:** exact, from, ranges, factors plus example jobs, or estimator (BRIEF-09).
   7. **Locale, languages and voice** (BRIEF-14), if step 3 left anything open.

   Then, if the owner has time: customer language (BRIEF-12), constraints such as capacity and season (BRIEF-16), assets (BRIEF-17), traffic numbers.
5. **Push back once on weak answers**, using the heuristics in `references/brief.md`. "Everyone" → ask for the trigger event. "Quality, service, fair prices" → ask for a number, a guarantee, a process detail or a named method. "Tailored to your needs" → ask for the actual process. A slogan or mission line → park it for the About page. If the answer stays vague, record it verbatim, tag it `confirmed (weak)`, and list it under *Conflicts & weak spots* in the file.
6. **Respect the owner's time.** They can stop at any point; write what you have. **Draft mode** (no owner available, or they asked for a draft): skip the interview, write the file with every field tagged, `Source: draft, not owner-reviewed` in the header, and a *Questions for the owner* section in the file (priority order, max 8, conflicts first, each showing the inferred value). The chat reply only summarizes. **Quick mode:** if the user wants speed, ask only the five core fields the sibling skills use for their inline mini-brief (ideal customer, one job + primary CTA, offer/pricing stance, proof available, locale) and leave the rest tagged.
7. **Write the file.** On an update, show what changes before saving. Versioning: new file → `v1`; any substantive change → bump the version, update the date, and prepend a changelog line naming the sections touched and why; a typo fix → no bump. Never rewrite old changelog lines.
8. **Report** with the output contract below and name the next skill to run.

## Output contract

The file follows the template in `references/brief.md`, section order unchanged, with a status tag at the end of every field line and a status count in the header. The count is the number of field lines per tag: one per template field line, a table row counts once (offer-mix rows carry a Status cell), and *Conflicts & weak spots* and *Questions for the owner* aren't counted.

```markdown
# Business context
Version: v2 · Updated: YYYY-MM-DD · Source: auto-draft (<urls, files>) + interview
Status: <n> confirmed · <n> decided · <n> inferred · <n> conflict · <n> missing

## Ideal customer (one)
- Who, situation, location, constraints (B2C: life stage): <value> `confirmed`
- Trigger event (why now): <value> `inferred: <source url or file>`
- Dream outcome (verbatim): <value> `decided: <doc>, YYYY-MM-DD`
- Anti-persona: `missing`

## Proof inventory
- Reviews: <platform> · <rating> · <count> · checked YYYY-MM-DD `inferred: <listing url>`
- Testimonials: [PROOF NEEDED: named testimonial about <objection it should answer>] `missing`

## Conflicts & weak spots
- Positioning: <source A> says X, <source B> says Y `conflict: <A> vs <B>`

## Questions for the owner (draft mode)
1. <question, showing the inferred value or conflict> → <what it unblocks>

## Changelog
- v2 YYYY-MM-DD — <sections touched>: <what changed and why>
- v1 YYYY-MM-DD — Initial brief from auto-draft + interview.
```

Reply in chat with:

```markdown
## Business context v<N> written to .agents/business-context.md

**Sources used:** <urls, files, review pages>
**Decisions:** sale type = <consumer / B2B> · homepage type = <type> · traffic = <cold/warm/paid mix> · locale layer = <on (be-eu) / off>

**Confirmed (<n>):** <field>, <field>, …
**Decided in docs (<n>):** <field> (<doc, date>)
**Conflicts (<n>):** <field>: <A> vs <B>
**Inferred, please check (<n>):**
- <Field>: <value> (from <source>)
**Missing (<n>), most important first:**
1. <Field>: <what it blocks, e.g. "hero proof line in page-copy">
**Weak spots:** <field>: <answer as given> → <follow-up question>

Draft mode: keep this reply short (counts, top 3 owner questions, file path); the file holds the full lists.

**Next:** <conversion-audit for the live site / page-copy for <page> / lead-offer, since no transitional offer exists>
```

## Rules that matter most here

- **Read before asking** (BRIEF-01). Every question the source material already answers wastes the owner's patience.
- **Surface conflicts; don't smooth them over.** When the site and the owner's docs disagree, that disagreement is often the most useful line in the brief.
- **One ideal customer, described concretely** (BRIEF-02). Several segments only when the same offer serves them all; record each one.
- **The primary action includes what happens after the click** (BRIEF-04). CTA wording, the booster line and process step 1 all come from it.
- **Proof is inventoried, never imagined** (BRIEF-10). Later copy may only claim what this list supports.
- **Customer words beat owner words** (BRIEF-11, BRIEF-12). Prefer unprompted sources (reviews, emails, DMs) over surveys. Capture trigger, perceived problem, alternatives, objections and dream outcome verbatim.
- **AI-mined phrases need a traceable source** (BRIEF-13). If you can't link it to a real review or message, drop it.
- **Table stakes aren't differentiators** (BRIEF-08). Turn each "why us" into a client benefit, or keep asking.
- **The signature method gets a name, but stays out of the hero** (BRIEF-07). It belongs in the solution and process sections.
- **Real constraints only** (BRIEF-16). No capacity number in the brief means no scarcity claim on the site later.
- **Pricing has a stance** (BRIEF-09). If the owner resists publishing prices, default to ranges plus cost factors and record why.

## References

| File | Read when |
|---|---|
| `references/brief.md` | Always. Template for the context file, BRIEF rules, interview script, weak-brief heuristics. |
| `references/principles.md` | Deciding which gaps matter most, filling defaults when context is missing, or resolving a Wes-era contradiction (e.g. C12 contact form vs scheduler, C18 how much the site must persuade). |
| `references/be-eu.md` | The business operates in Belgium or the EU, or writes in NL, FR or DE: languages, formality, legal info, VAT, review and consent rules; B2B-only sites (BE-31…34). |
| `references/sources.md` | Checking or citing a `[W:id]` video source. |

## Guardrails

- **Never invent proof.** No testimonials, ratings, review counts, client names, logos or numbers that the owner or a source didn't supply. Use placeholders like `[PROOF NEEDED: testimonial about speed of delivery]`.
- **Truthful psychology only.** Scarcity, anchors, "most popular" tiers and guarantees go in the brief only when they are real and the owner confirms them (principle 13).
- **Stats in the references are illustrative.** Use them to explain direction; never quote them to a client or put them in the brief as fact.
- **Testimonial permission.** Record whether each named quote may be published. Don't copy a client's personal details into the file beyond what the business already publishes.
- **Ask before touching anything live.** This skill writes one local file. Don't publish, edit a CMS or change the live site without explicit approval.
- **Not legal advice.** Items marked "verify" in `references/be-eu.md` stay flagged until checked against current official sources.

## Related skills

- `conversion-audit`: audit an existing page against this brief.
- `page-copy`: write or rewrite homepage, landing, services, about or contact pages from this brief.
- `lead-offer`: design the transitional offer when the brief says "none yet".
- `humanizer` or `stop-slop`, if available: strip AI patterns from the drafted one-liner and positioning lines.
- `belgisch-nederlands-redacteur`, if available: check Belgian Dutch phrasing when the brief records NL voice and example sentences.

Guidance distilled from Wes McDowell's YouTube channel (see references/sources.md). Structure ideas adapted from coreyhaines31/marketingskills (MIT).
