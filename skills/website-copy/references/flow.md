# 26 — Flow: the page as an argument

The blueprint (STRUCT-02) says which sections a page needs and in what default order. This file checks the thing the blueprint can't: whether each section **earns the next one**, so a cold reader is carried from "what is this?" to "I'll book that call" without a gap. A page can have every section in the right order and still read like a pile of blocks. That is the failure this file targets.

> **Not from Wes.** `[R: source]` = an outside primary source (full list in `sources.md`, "Flow sources"). The procedures are rewritten for small service businesses; no source text is copied. On a page, "story" still means structure, not a "Meet Sally" tale (STORY-01, STORY-02).

## The model

A page is a **chain of beliefs**. The reader arrives believing one thing and must leave believing "a call with these people is worth 20 minutes and low-risk". Every section relies on beliefs already accepted higher up and adds **one** new belief. Readers accept a claim only when they've been prepared for it; a claim that arrives early reads as hype and the reader stops following `[R: Schwartz 1966, "Gradualization"]`.

Three ways the chain breaks:

- **Leak:** a belief the reader needs, with no section that installs it.
- **Ballast:** a section that installs no belief on the chain. It may be true and nicely written; it still costs attention.
- **Broken seam:** two neighbouring sections that connect only with "and also".

## FLOW-01 — Map the argument before laying out sections

Write the map before any body copy (and in an audit, rebuild it from the live page):

1. **Start state:** what the reader believes and asks on arrival (awareness stage, FLOW-02; traffic temperature from the brief).
2. **End state:** the belief that makes the primary CTA feel obvious.
3. **The beliefs in between**, 4–7, in dependency order: a belief comes after every belief it needs.

Default chain for a service business, cold traffic (adapt it; don't copy it blindly):

| # | Belief | Usually installed by |
|---|---|---|
| B1 | "This is for someone like me, about my situation" | Hero (HERO-01, HERO-06) |
| B2 | "This problem is real, costs me something, and is worth fixing now" | Problem |
| B3 | "These people understand it and know how to fix it" | Solution / guide (empathy + authority) |
| B4 | "Their way fits my situation" | Offer, services, benefits, mechanism |
| B5 | "It worked for people like me" | Proof next to the claims (PROOF-03, PROOF-07) |
| B6 | "It's doable: the effort, time and price are acceptable" | Process, price, what's included |
| B7 | "The next step is small and safe" | CTA + booster (CTA-08), FAQ leftovers |

B2B adds a belief the champion needs: "I can defend this choice internally" (named cases, price logic, DPA/security for IT; BE-33). The chain decides which sections exist; STRUCT-02 is the default shape, not the authority. The belief-chain framing with leaks and ballast is adapted from Theycallmeholla/skills `conversion-audit` (MIT).

## FLOW-02 — Start where the reader already is

The top of the page meets the reader's awareness stage; the rest of the page does the convincing `[R: Schwartz 1966, ch. 2; Wiebe 2016]`.

| Reader arrives… | Typical traffic | Open with | The page can skip or shorten |
|---|---|---|---|
| **Most aware**: knows you, wants the offer | Referral, returning visitor, AI-assistant recommendation | Offer, price, how to book | Problem agitation; keep proof and logistics (C18, AI-04) |
| **Product aware**: knows offers like yours, comparing | Comparison search, LinkedIn post | What makes yours different (BRIEF-07/08) | Basic problem explanation |
| **Solution aware**: knows a fix exists, not yours | Service + city search | The outcome + why your approach | Long education |
| **Problem aware**: feels the pain, no fix in mind | Symptom search, social | The problem in their words (STRUCT-02 #2) | — (full chain) |
| **Unaware** | Cold social | Not a service page: use a pre-sell article (STRUCT-03) | — |

Mixed traffic: write for the coldest large segment and give the warm segment a visible shortcut (booking block high, C18).

## FLOW-03 — One section, one belief, one open question

In the wireframe, every section row gets three cells:

- **Requires:** the beliefs (B-numbers) it leans on. All of them must be installed above it.
- **Establishes:** the one belief it adds. Two beliefs → split the section or cut one. None → ballast: cut it, move it to its own page, or fold it into the section whose belief it supports.
- **Leaves open:** the question the reader has after reading it. The next section answers that question (FLOW-04).

The "requires / establishes" bookkeeping is adapted from Matt Pocock's `writing-beats` skill (MIT): a beat is only reachable once everything it needs is already established.

## FLOW-04 — The question chain

Each section answers the question the previous section raised, so headings read as answers to questions the reader is already asking `[R: Wiebe 2016]`. Wiebe's homepage order: what is it → why should I care → do people like me care → how does it work → how will my life improve → why should I believe you → what now. Her diagnosis of the losing control page: "A didn't lead to B, B didn't lead to C."

Procedure: above each heading, write the reader's question in their words. If the section below doesn't answer it, reorder, add a bridge line, or add the missing section. Flag any section answering a question nobody has asked yet (typically services or features before the problem lands), and any question still open at the final CTA.

**Headings-only test:** read only the section headings, top to bottom. They should tell the argument on their own; labels ("Our services", "About us", "Process") tell nothing (STRUCT-06).

## FLOW-05 — The seam test: "therefore" or "but", never "and also"

Write each section's gist in one line. Join each pair of neighbours with **therefore / so**, **but** or **because** `[R: Parker & Stone 2011; Olson 2015]`. If only "and also" fits, the seam is broken: the sections are a parallel list (merge them into one section) or one is in the wrong place.

- Good: "Your team already uses AI tools on their own, **but** nobody agreed what's safe → **so** we set the rules together in one workshop."
- Broken: "We offer workshops **and also** we do strategy **and also** we build tools." That's a services list pretending to be an argument.

The last line of a section should hand off to the next heading: a plain bridge sentence that names the next question. Not bucket-brigade filler ("Here's the thing…", "But wait…"); that clashes with the banned-phrase list and reads as sales talk, especially in Belgium.

## FLOW-06 — No claim before its prerequisites

A claim placed above the beliefs it needs lands as hype `[R: Schwartz 1966, "Gradualization"]`. Common misplacements:

| Too early | Why it fails | Move it after |
|---|---|---|
| Programme, features or method | The reader doesn't yet feel why they'd need it | Problem (B2) and guide (B3) |
| "Why us" / awards / stat row | Nobody cares who you are before they care about the problem | Problem; keep the hero to one proof line (HERO-11) |
| Price without context | Price before value reads as cost | The outcome (B4) and process (B6); price near the CTA (PRICE-01) |
| A hard booking ask | Asking before trust | At least one proof section (B5); a soft CTA higher up is fine (CTA-06) |
| Your origin story | It's about you | About page (STORY-02, C5) |

Set the stakes before the product: name what changed in the reader's world and what the alternatives (including doing nothing, doing it in-house, hiring the usual supplier) can't do, then present the offer as the answer to exactly those gaps `[R: Dunford 2023; Raskin 2016]`. Every service or feature shown must answer a problem or criterion set up earlier on the page; one that doesn't is ballast.

## FLOW-07 — Answer each objection where it arises

Build an objection / counter-objection table before writing body copy `[R: Conversion Rate Experts, O/CO]`:

| Objection (customer words) | Arises at section | Counter | Proof that carries it |
|---|---|---|---|
| "Will this work for a company our size?" | Offer (B4) | Who it's for, who it isn't for | A case from a similar company |
| "It'll cost a fortune" | Process / price (B6) | From-price, what's included, subsidy if real (BE-31) | Price example |

- Sources: sales-call notes, emails, reviews, chat logs, the brief's objection list (BRIEF-08). Look for the obvious ones, the embarrassing ones ("I don't understand AI myself") and the assumed ones.
- Common service-business objections: **trust** (are they real and good), **fit** (for someone like me), **price**, **effort** (how much of my time), **timing** (why now). B2B adds **internal buy-in** and **IT / data**.
- Place each counter **in the section where the doubt comes up**, with its proof right next to it (PROOF-03, PROOF-07). The FAQ only catches what's left; if the #1 objection lives only in the FAQ, it's misplaced (use the "wild card" section, STRUCT-02 optional inserts).
- **Counter only** for objections people won't say out loud: answer without naming the fear ("Geen technische voorkennis nodig" rather than "Bang dat je het niet snapt?").
- A detached proof band (logos + three quotes in one strip) proves only the claim directly above it.

## FLOW-08 — Ask at the point of conviction

- The final CTA comes after the last open question is closed (FLOW-04), restating the chain in one line: outcome + the main reason to believe + the small next step (STRUCT-02 #10).
- Mid-page CTA repeats (CTA-06) sit after sections that **close** a belief (proof, process), not after sections that **open** a doubt (problem, price without a booster).
- Shift points: the copy moves from promise → mechanism → proof at the moment the reader would ask "how?" and then "says who?". A long promise stretch without proof, or proof before any promise, is a misplaced shift.

## FLOW-09 — The hostile reader panel

After drafting, or as an audit step, read the page top to bottom as five cold readers who are **not told the page's goal**. Each reports where they stopped and why, in the form "I stopped at section N because…" or "I don't believe ___ because ___":

| Reader | Reads | Looks for |
|---|---|---|
| **Scanner** | Hero + headings only, ~8 seconds | Does the heading sequence alone tell the argument? (headings-only test) |
| **Skeptic** | Every claim | Claims without proof, superlatives, vague promises. In Belgium a superlative is itself a red flag |
| **Comparer** | With other tabs open | Why you vs the alternatives, including doing nothing or doing it in-house; price |
| **Wrong fit** | Hero, offer, FAQ | Can I tell quickly that this isn't for me? (that's a feature: it filters bad leads) |
| **Not now** | Middle and end | Why act now; is there a smaller first step? (truthful only, SCAR-01) |

An objection raised by **3 or more** readers is critical: fix it (usually with FLOW-06 or FLOW-07), then run the panel once more. Personas are a thinking tool, not evidence; don't present them to the owner as user research. Adapted from the hostile-validation phase in yashaiguy-dev `Sales-Page-Copywriting-Skill` and the cold-visitor panel in Theycallmeholla/skills `conversion-audit` (both MIT).

## Argument map format

Both `website-copy` (wireframe) and `website-conversion-audit` (Storyline section) use this table:

| # | Section | Requires | Establishes | Reader's question after | Seam to next | Status (audit) |
|---|---|---|---|---|---|---|
| 1 | Hero | — | B1 | "Why would I need this?" | so → | covered |
| 2 | Problem | B1 | B2 | "Who can fix this?" | but → | weak: symptoms in our words, not theirs |
| 3 | … | | | | | |

Below it: **Leaks** (beliefs with no section), **Ballast** (sections with no belief), **Broken seams** ("and also" pairs), **Misplaced** (FLOW-06/07 items), **Open at CTA** (questions never answered).

## Worked example (fictional)

A B2B page selling AI workshops to SMB teams, as drafted:

1. Hero: "AI-workshops op maat" → 2. Our three workshop formats → 3. About our team → 4. Logos → 5. Problem: "Je team gebruikt AI al, maar zonder afspraken" → 6. FAQ → 7. CTA.

Diagnosis: the formats (2) arrive before the reader feels the problem (5): FLOW-06. "About our team" (3) and logos (4) install B3/B5 for nobody yet; they're early, and the logos prove no claim (FLOW-07). Seam 2→3 and 3→4 is "and also" (FLOW-05). B6 ("doable, affordable") is a leak: price and time investment appear only in the FAQ. The headings-only test reads as a brochure.

Reordered: hero (outcome for the team, "je") → problem in the team's words (B2) → "Zo pakken we het aan" with one human face (B3) → the formats, each tied to a symptom from the problem section (B4) → a case from a similar company right after the format it proves (B5) → three steps, time per step, from-price (B6) → FAQ with the leftovers (IT, data, "geen voorkennis nodig") → CTA restating outcome + case + "vrijblijvend kennismakingsgesprek van 20 minuten" (B7).
