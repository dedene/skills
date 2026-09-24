---
name: lead-offer
description: Designs a transitional offer for a service business (lead magnet, quiz, estimator, micro-app, mini-webinar, challenge) with its opt-in, thank-you page and 3-5 email nurture. Use for freebies, opt-ins, "what can we give away for emails" or visitors not ready to book. For writing site pages, use page-copy; for reviewing a live page, use conversion-audit.
---

# Lead Offer

Most first-time visitors are comparing, not buying. This skill designs the second path on the site: a small, genuinely useful offer that earns an email, a thank-you page that offers the booking, and a short nurture sequence that brings people back until they're ready. Output is an offer spec plus ready-to-edit copy for every asset.

Scope: small and medium **service** businesses (trades, clinics, coaches, consultants, agencies, local pros). Not e-commerce catalogues. SaaS only loosely: a free trial is a product decision, not a lead magnet. When the core paid offer itself is weak, the skill says so and fixes the offer first.

## Start with context

1. If `.agents/business-context.md` exists, read it first. Ask only for what's missing or marked inferred.
2. If it doesn't exist, run a 5-question mini-brief inline, one question at a time: ideal customer · the site's one job and primary CTA · offer and pricing stance · proof available · locale and languages. For a multi-service or multi-language funnel, suggest running `site-brief` first instead. Nobody available to answer: proceed on inferred values, tag them, and list the questions under Open gaps.
3. Then collect the lead-offer inputs the brief rarely has:
   - the problem customers hire you for, and the question prospects ask most before buying
   - expertise or content you can repackage (checklists you already use, pricing logic, FAQs, videos)
   - traffic sources (organic, referrals, YouTube, ads, email signature) and the booking or email tool in use
   - real capacity and seasonality (only needed if scarcity comes up)
4. Never invent proof. Use placeholders such as `[PROOF NEEDED: testimonial about how fast the checklist paid off]` and list each one under Open gaps.

## Workflow

1. **Protect the primary path.** Name the primary CTA (book, call, get a quote). The lead offer feeds it and never replaces it (LEAD-01, CTA-01, CTA-10). No primary CTA or booking path yet? Define it before designing a freebie.
2. **Check the core offer.** If the paid service is vague or unpackaged, score the value equation (OFFER-01), fix the lowest lever, and package and name it (OFFER-02) before building a magnet on top.
3. **Place the buyer.** Pick the stage the offer serves: problem-aware, solution-comparing, or decision-ready but hesitant (stage table in `references/lead-offer.md`). Service businesses usually earn most from the decision stage: estimators, package-finder quizzes, sample plans.
4. **Place the traffic.**
   - Cold organic: full opt-in page.
   - Warm (YouTube, referrals, email signature, AI recommendations): headline, email field, button, nothing else.
   - Paid: a dedicated page that repeats the ad's promise (principle 15). In the EU, pixels and retargeting need consent (BE-14).
5. **Pick the format** by business type and stage, then confirm it fits the content and the person (LEAD-08):

   | Business | Default format | Watch out |
   |---|---|---|
   | Urgent or local trade (plumber, roofer) | DIY quick-win checklist or short video, seasonal checklist | Solve a slice; the bigger job still needs them (LEAD-03) |
   | Quote-based project (renovation, landscaping, removals) | Price estimator or calculator (LEAD-13) | Ballpark open, personal estimate gated (C13) |
   | Clinic, therapist, wellness | Short challenge or at-home routine video (LEAD-17) | Regulated-profession rules in BE (BE-26) |
   | Consultant, agency, advisor (B2B) | Scored assessment or quiz (LEAD-12), micro-app (LEAD-14), mini-webinar (LEAD-16) | "Personalized" must be real (LEAD-09) |
   | Designer, creative studio | Style quiz (LEAD-12) | Payoff must feel worth the email |
   | Coach, trainer | Timed challenge (LEAD-17) or mini-webinar | Promise doing, not learning (LEAD-05) |

   **Micro-app (2026 option):** only if it passes "it takes X and gives me Y" in one sentence. Ground its logic in the business's real prices or method, and publish it on the business's own domain (LEAD-14). Treat a custom GPT as a dated fallback (LEAD-15).
6. **Title it.** Result + constraint (LEAD-04), doing over learning (LEAD-05), phrased around the reader's result (LEAD-11). Write 3 options. Kill any that fail: a quick search gives the same thing free · it's a guide to hiring you · it's a newsletter (LEAD-10) · the description promises something else (LEAD-06) · it's a brochure in disguise (LEAD-07).
7. **Spec the deliverable.** Outline, format, length (consumable in under 30 minutes, works on mobile), the quick win they get today, and the next problem it reveals that the paid service solves (LEAD-03). End with one soft next step, never a pitch (LEAD-07).
8. **Write the opt-in.** Headline matching the button that brought them · visual of the deliverable · 3–5 outcome bullets · proof or placeholder · email (+ first name only if used) · a button that names the thing ("Send me the checklist"; CTA-02, FORM-07) · microcopy on what arrives and how often. Quizzes ask for the email just before the result (LEAD-12). Place it as a secondary path: text link under the hero CTA, its own section lower on the homepage, matching content pages, desktop exit intent, never an instant popup (LEAD-20, CTA-10). Add off-site spots (LEAD-21).
9. **Write the thank-you page.** Confirm and set expectations (THANKS-01), offer the booking as the next step up with the exact primary CTA wording (THANKS-02, LEAD-02, CTA-04), link your best content rather than social profiles (THANKS-03), give it a unique tracked URL and keep it out of the search index (THANKS-04).
10. **Write the nurture, 3–5 emails.** Arc: deliver + first win → value (story → point → bridge) → proof (client story) → objection → direct invitation. For three emails: deliver + first win, a client story that also answers the top objection, then the invitation. Help before asking; each email teases a page on the site and links to it; subject lines use the customer's pain phrases. The invitation says what the call or visit is, how long, what it costs, and real availability only. Quiz leads get emails tailored to their result. After the sequence: a weekly helpful email that re-invites about every fourth send.
11. **Apply locale.** BE/EU business: read `references/be-eu.md`. Write in the business's language and formality (BE-01 to BE-04). Describe the email series honestly or use a separate unticked consent box (BE-11, BE-12), add the privacy line (BE-13), make sure "free" is free (BE-21), and use no fake urgency (BE-22).
12. **Urgency only if real.** Ask for the actual constraint (capacity, season, cohort date). None? Leave urgency out and say why (SCAR-01, SCAR-04). Honest formats: SCAR-02.
13. **QA the copy.** Run the sweep in `references/copy.md` (clarity, customer words, specificity, proof, zero risk). Check the title against the deliverable one last time.

## Output contract

Return one markdown document in the business's language (spec notes may stay in English if the user writes in English):

```markdown
# Lead offer: [chosen title]

## Summary
- Ideal customer: …
- Primary CTA (unchanged): …   · Transitional offer role: secondary path
- Buyer stage: … · Traffic: cold / warm / paid · Locale: …
- Format and why: … (LEAD-xx)
- Next problem it reveals → paid service: …

## Offer spec
- Title: [chosen] · alternatives: [A], [B]
- Promise (result + constraint): …
- Deliverable outline: … · Format: … · Consumption time: …
- Quick win today: …
- Soft next step at the end: …
- Gating: open … / gated … · Fields: …
- Build notes: tool, data or logic needed, effort estimate

## Opt-in page
Section by section, each with its rule IDs: headline, subhead, visual, bullets, proof ([PROOF NEEDED: …]),
form fields, button, booster/microcopy, consent line (EU), FAQ.
Placement on site: … · Off-site: …

## Thank-you page
Confirmation · what happens next · next-step CTA (exact primary wording) · while-you-wait links · tracking URL, noindex

## Nurture sequence
| # | Send | Purpose | Subject | Links to |
|---|---|---|---|---|
Then each email in full: subject, preview text, body, one CTA, rule IDs.

## Honesty and compliance checks
- Proof placeholders: … · Urgency used: none / [real constraint] · "Free" is free: yes/no
- EU only: consent pattern (BE-12), privacy line, cookie consent for pixels, regulated profession check

## Open gaps
- [ ] …
```

## Rules that matter most

- LEAD-01 / CTA-10: the magnet is always the secondary, visually subordinate path.
- LEAD-03: solve one slice of the problem they'd hire you for; the next slice is the paid work.
- LEAD-04, LEAD-05, LEAD-06: specific result, doing over learning, and the title must match the thing.
- LEAD-09 / LEAD-12: personalization must be real; ask for the email just before the quiz result.
- LEAD-14: micro-app passes "takes X, gives Y", logic grounded in real data, on your own domain.
- THANKS-02 / LEAD-02: after the small yes, offer the booking.
- FORM-01: email only (+ first name if used); every extra field needs a reason.
- SCAR-01 / BE-22: only scarcity the buyer could verify.
- OFFER-01: a weak paid offer outranks any lead-magnet tweak.

## References

| File | Read when |
|---|---|
| `references/lead-offer.md` | Always: formats, buyer stages, opt-in, nurture template, scarcity, offer design |
| `references/cta-forms.md` | Writing buttons, form fields, consent placement, the thank-you page |
| `references/copy.md` | Drafting titles, bullets and emails; the copy QA sweep; banned phrases |
| `references/principles.md` | Resolving conflicts (C1 ask ladder, C13 gated calculators); defaults when context is missing |
| `references/be-eu.md` | Business is in Belgium or the EU: language, consent, "free", urgency, regulated professions |
| `references/sources.md` | Checking what a `[W:…]` or `[MS]` citation points to |

## Guardrails

- Truthful psychology only: no fake deadlines, resetting timers, invented spot counts or made-up viewer numbers.
- Never invent proof (testimonials, download counts, ratings, logos, results). Use `[PROOF NEEDED: …]`.
- Stats in the references are marked illustrative. Use them to explain direction; never quote them to a client as fact or promise conversion rates.
- The freebie must deliver its promise the moment they get it. Don't promise a deliverable the business can't produce.
- Ask before publishing anything, editing a live site, connecting email tools, or sending emails.

## Related skills

- `site-brief`: build or refresh `.agents/business-context.md` before a large job.
- `page-copy`: the pages around the offer (homepage section, service pages, guarantees on the paid offer).
- `conversion-audit`: review an existing opt-in or thank-you page before redesigning it.
- `humanizer` or `stop-slop`, if available: de-AI the final copy.
- `belgisch-nederlands-redacteur`, if available: polish Belgian Dutch copy.

Guidance distilled from Wes McDowell's YouTube channel (see references/sources.md). Structure ideas adapted from coreyhaines31/marketingskills (MIT).
