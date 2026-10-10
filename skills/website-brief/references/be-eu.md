# 60 — Belgium / EU layer

> **Practical guidance, not legal advice; check with counsel for regulated sectors.** Checked against primary sources on 2026-09-24.

> **Not from Wes.** `[L: source]` = legal claim checked against that source. `[G]` = practitioner or conversion advice. **verify** = not confirmed. Where a Wes rule conflicts with EU/BE law, the law wins.

## Language (NL / FR / EN / DE)

**BE-01 — Pick languages by service area, not by ambition.** `[G]` Flanders → NL. Wallonia → FR. Brussels → FR + NL, often EN. East Belgium → DE where relevant. Only publish a language you can also *serve* in (calls, quotes, invoices). No law dictates website or advertising language; language rules target staff documents and product labels/manuals `[L: adjunctvandegouverneur.be, taalverplichtingen bedrijven]`.

**BE-02 — Transcreate; don't translate.** `[G]` Redo the voice-of-customer work per language (BRIEF-11/12). Write NL in **Belgian Dutch** (hand NL copy to the `belgisch-nederlands-redacteur` skill if available) and FR in Belgian usage. Wes's "customer language" rule applies per language.

**BE-03 — Formality per language and sector.** `[G]` NL: "u" for legal, medical, financial and older audiences; "je" common for trades, lifestyle, younger B2C. Hold one choice across site, email and forms. FR: "vous" by default. COPY-08 is about tone, not the pronoun.

**BE-04 — Belgian reassurance words for the booster line (CTA-08).** `[G]` NL: *vrijblijvend*, *gratis*, *binnen 1 werkdag*, *geen verborgen kosten*. FR: *sans engagement*, *gratuit*, *réponse sous 24 h*. E.g. "Vraag je vrijblijvende offerte aan" / "Demandez votre devis gratuit". Same wording everywhere per language (CTA-04). "Gratis" must be true (BE-21); healthcare may not advertise free care (BE-26).

**BE-05 — Technical setup.** `[G]` One URL per language (`/nl/`, `/fr/`, `/en/`) with `hreflang` (+ `x-default`) and self-referencing canonicals; translated slugs; a text switcher ("NL · FR · EN"), not flags; no automatic IP/browser redirects. Design the hero for the **longest** language (FR/NL run 10–25% longer than EN) at 390 px.

**BE-06 — Local names per language.** `[G]` Gent/Gand, Antwerpen/Anvers, Brussel/Bruxelles, Leuven/Louvain, Mechelen/Malines, Kortrijk/Courtrai, Luik/Liège, Bergen/Mons, Namen/Namur. Service-area lists and HERO-06 follow suit.

**BE-07 — Formats.** `[G]` `+32` in `tel:` links, local display (09 123 45 67, 0470 12 34 56). Numbers 1.250,50 (FR also 1 250,50; pick one). NL "€ 1.250", FR "1.250 €". Dates DD/MM/YYYY.

## Legal information on the site

**BE-08 — Mandatory business identification.** `[L: WER art. XII.6; WVV art. 2:20; FOD Economie]` Easily, directly and permanently accessible on the site and business social accounts:
- name and geographic address; contact details **including email** (FOD Economie: at least two channels, email + phone if you sell or book online);
- enterprise number (KBO/BCE); VAT number if VAT-liable;
- licensed activity: supervisory authority. Regulated profession: professional body, title + country granted, link to the professional rules. Any code of conduct and where to read it.
- Legal entities add: legal form, exact seat address, "RPR/RPM" + court of the seat (e.g. "RPR Gent, afdeling Gent"), "in vereffening" if applicable (fiscosearch.be/collecties/wetboek-vennootschappen-verenigingen/artikel-2-20).
- Remove old EU ODR-platform links: the platform closed 20 July 2025 (Reg. (EU) 2024/3228).
- Place: footer + a "Juridische info / Mentions légales" page. Source: economie.fgov.be/nl/themas/online/elektronische-handel/verkoop-internet/bedrijfswebsite-en-accounts-op
- **Conflict with Wes:** "never publish your email address" `[W:ClD037qJSTQ 2025]`. Resolution: publish it (the law wins), keep the form or booking tool as the *primary* path, use a role address (info@) with spam filtering.

**BE-09 — Privacy notice and cookie policy** `[L: GDPR art. 13]` linked from every form and the footer; name your processors (booking tool, email platform, CRM, analytics, chat) and non-EU transfers.

## Forms and GDPR

**BE-10 — Minimal fields are also a legal rule.** `[L: GDPR art. 5(1)(c), 6(1)(b)]` Ask only what you need to answer the request (FORM-01); don't make phone mandatory "just in case". Answering a quote or booking request rests on pre-contractual steps at the person's request, not consent, so no consent box is needed to submit.

**BE-11 — Separate the request from marketing consent.** `[L: WER art. XII.13; KB 4 April 2003 art. 1; GBA Recommendation 01/2025]` Marketing email needs prior consent; a quote request isn't consent, and a prospect isn't a customer. Use a separate, **unticked** checkbox ("Ja, stuur me af en toe tips en aanbiedingen" / "Oui, envoyez-moi des conseils") and a free, easy unsubscribe in every email.
- **Soft opt-in** only if all apply: address obtained directly from the customer **in a sale**; mail only about **similar products/services you provide yourself**; free, easy objection offered at collection and in every message.
- B2B: no consent needed for **impersonal** legal-entity addresses (info@); named work addresses are personal data.
- Double opt-in is **not legally required**; `[G]` use it anyway to prove consent (GDPR art. 7(1)) and block typos and bots.
- Source: gegevensbeschermingsautoriteit.be/publications/aanbeveling-01-2025-over-de-verwerking-van-persoonsgegevens-bij-direct-marketing.pdf

**BE-12 — Lead magnets and consent.** `[L: GDPR art. 7(4); EDPB Guidelines 05/2020]` Tying a download to newsletter consent is presumed not freely given. Safer `[G]`: (a) describe the deliverable honestly as an email series ("5 short emails over 8 days, unsubscribe anytime") so the emails *are* the service; or (b) deliver the freebie and ask newsletter consent via a separate checkbox. Say exactly what they'll receive (LEAD-06).

**BE-13 — Near every form:** `[G]` one line on what you do with the data + privacy-notice link; expected response time (FORM-07). No pre-ticked boxes.

## Cookie banner above the fold

**BE-14 — Consent before non-essential cookies.** `[L: Kaderwet 30 July 2018 art. 10/2; GBA cookie checklist]` (gegevensbeschermingsautoriteit.be/publications/cookie-checklist.pdf)
- Without consent, only strictly necessary cookies (session, load balancing, language, cookie preference, cart). **Analytics/visitor counting needs consent in Belgium**, as do pixels, session recording, heatmaps, local storage and fingerprinting.
- First layer: "Alles weigeren / Tout refuser" beside "Alles accepteren", same styling; "Settings" beside "Accept all" is **not** enough. Layer one also names purposes, who sets cookies, and how to withdraw.
- No pre-ticked boxes; no consent from scrolling or closing; no cookie walls.
- A permanent "Cookie settings" link; one-click withdrawal that actually stops tracking.
- Re-ask after about **6 months** (GBA); keep a dated, versioned cookie policy.

**BE-15 — Don't let the banner eat the hero.** `[G]` No rule sets banner size; this is conversion practice within BE-14. A full-screen mobile modal hides headline and CTA, so the 5-second test fails.
- Compact bottom sheet or bar (≤ ~30% of 390×844), with Accept and Reject both visible without scrolling.
- Hero headline and primary CTA stay visible and tappable.
- Run the 5-second test and audit screenshots **with** the banner (A-F4). Plain-language copy in the page's language.

**BE-16 — Two-click embeds.** `[G]` YouTube (privacy-enhanced, click-to-load), Google Maps (static image + "open map"), booking, review and chat widgets often set third-party cookies: load after consent or on click (BE-14). Also helps speed (STRUCT-13).

**BE-17 — Measurement under consent.** `[G]` Analytics will under-count. Count conversions from thank-you pages and form/CRM records; server-side or "cookieless" tags that read the device still need consent. Use the "How did you find us?" field (MEAS-02). Retargeting (`[W:cqh4JDnX6KU 2022]`) shrinks in the EU; the email list matters more.

## Reviews and testimonials (EU consumer law)

**BE-18 — Review rules after the Omnibus directive.** `[L: WER art. VI.97, VI.99 §7, VI.100 (law of 8 May 2022); FOD Economie Guidelines Online reviews 2023]` (economie.fgov.be/sites/default/files/Files/Entreprises/guidelines-online-reviews.pdf)
- If you show consumer reviews, state **whether and how you check they come from real customers**, next to the reviews. E.g. "Reviews from our Google Business Profile; we don't verify them ourselves."
- Blacklisted: fake reviews, commissioning them, **misrepresenting reviews**. Showing only positive ones is misleading unless disclosed as a selection. Edit or delete only under published, objective rules. Curated testimonials: label as selected stories, link the full profile (PROOF-12).
- Show source and date; keep counts current (hero "4.9 · 87 reviews" must match the live profile).
- Incentives: allowed only if every review, positive or negative, has equal chance; label paid reviews. **Google is stricter**: no incentives and no review gating (support.google.com/contributionpolicy/answer/7400114). Wes's "first five free" (PROOF-20): free work for *honest*, disclosed feedback, never tied to a Google review.
- `[G]` Store written permission for names and photos in testimonials.

**BE-19 — Google reviews are the default proof for local and consumer services.** `[G]` B2B: named case studies and client quotes (with permission) carry the proof instead. Google rating + count near the hero (HERO-11) with the Google label and a link ("Lees alle 187 reviews op Google" / "Lire les 187 avis sur Google"). Ask right after the job with a direct link; reply in the reviewer's language. Since 2019 Google shows no search stars for self-serving LocalBusiness reviews (Google Search Central, Sept 2019), so the value is on-page trust.

## Prices, "free", urgency (consumer law)

**BE-20 — Consumer prices include VAT and mandatory costs.** `[L: WER art. VI.3–VI.5; ConsumerConnect, prijsaanduiding diensten]` Prices shown to consumers are totals: VAT, taxes and every cost they must pay (e.g. fixed travel costs). Custom work may be priced by quote; a paid quote must be announced beforehand. `[G]` B2B pages may show excl. VAT, clearly labelled. "Vanaf € 1.250 incl. btw" / "À partir de 1.250 € TVAC" fits PRICE-01…07.

**BE-21 — "Free" must be free.** `[L: WER art. VI.100; UCPD Annex I pt 20]` "Gratis offerte" or "free consultation" can't carry costs beyond the unavoidable cost of responding. If an on-site quote visit is paid, say so next to the CTA.

**BE-22 — No fake urgency.** `[L: WER art. VI.100; UCPD Annex I pt 7]` Falsely claiming an offer is available only for a very limited time is blacklisted. Resetting countdowns, perpetual "last places" and invented "X people are looking" are out (SCAR-01, PROOF-13).
- Price reductions `[L: WER art. VI.18]`: show the reference price = **lowest price in the 30 days before** the reduction, per sales channel. **Belgium applies this to services too**, beyond the EU directive (goods only); the Commission opened an infringement procedure in Oct 2025 (stibbe.com). Apply it to "−20%" on services; **verify** whether VI.18 has since changed.

**BE-23 — Comparisons.** `[L: WER art. VI.17]` Comparative advertising must be objective, verifiable, not denigrating. `[G]` Compare with categories ("a typical renovation company", "doing it yourself"), not named competitors (PROOF-22).

**BE-24 — Commercial guarantees don't replace legal rights.** `[L: Dir. (EU) 2019/771 art. 17]` For goods you sell or install, a commercial guarantee must state that the legal warranty remains unaffected. `[G]` For services, word guarantees (GUAR-02) as extras on top of the law; in construction never suggest they replace ten-year liability.

**BE-25 — Online-booked paid services: withdrawal right.** `[L: WER art. VI.47–VI.53; Dir. 2011/83/EU; consumerconnect.be]`
- Consumer service contracts concluded at a distance **or off-premises** (e.g. a quote signed at the client's home) carry a 14-day withdrawal right; up to 12 months longer if you don't inform about it.
- Starting within 14 days needs the consumer's **express request** (unticked checkbox); withdrawing then costs them a proportionate amount, and once **fully performed** (with acknowledgment) the right lapses.
- Exceptions include date-specific leisure services and urgent repairs the consumer called you for. Free consultations: not relevant.
- **Withdrawal button** `[L: Dir. (EU) 2023/2673, CRD art. 11a]`: from **19 June 2026**, contracts concluded online need a clearly labeled "withdraw from contract here" function, available throughout the withdrawal period, with confirmation (eur-lex.europa.eu/eli/dir/2023/2673/oj). Belgian WER implementation: **verify** (a secondary source cites a law of 19 July 2026, art. VI.61/2; not confirmed on ejustice).

## Regulated professions

**BE-26 — Check your professional body before using Wes-style proof.** BE-08 still applies. Headline rules:
- **Healthcare providers** `[L: law 22 April 2019 art. 31; riziv.fgov.be/nl/professionals/info-voor-allen/publiciteit-door-zorgverleners]`: truthful, objective, verifiable; no "free care" or reimbursement as a selling point; no pushing unnecessary treatment. Doctors `[L: Orde der artsen, code art. 37; ordomedic.be]`: no patient testimonials, no misleading or comparative publicity.
- **Aesthetic medicine/surgery** `[L: law 23 May 2013 art. 20/1]`: advertising banned; factual practice information only.
- **Real-estate agents** `[L: WER XII.6; BIV code art. 20; biv.be]`: title + BIV number + country, BIV code link, liability insurer + policy number.
- **Lawyers, pharmacists, architects, accountants (ITAA)**: publicity allowed within each deontology code; **verify** current rules on testimonials, prices, comparisons.
- `[G]` Flashpoints: testimonials, before/after photos, price promotions, comparisons. The audit flags these as "check with your body" instead of recommending them.

## Local trust signals that work in Belgium

- Company and VAT number visible (trust signal for skeptical buyers).
- Real address or service area by municipality; photos of real premises and vans (PROOF-16).
- **Ten-year liability insurance** `[L: law 31 May 2017 "Peeters-Borsus", in force 1 July 2018; economie.fgov.be/nl/themas/financiele-diensten/verzekeringen/bouwsector/de-verzekering-tienjarige]`: mandatory on **residential** work where an architect is legally required. Certificate to owner and architect **before work starts**; insurer name, enterprise number and policy number in the **contract documents**. No website mention required; `[G]` it's still a strong trust line. Put it, federation memberships and labels near pricing/FAQ and in the footer.
- Response-time promise in the booster line and on the contact page.
- Local price case: "Keukenrenovatie in Deinze: 8 weken, € 24.500 incl. btw" (PRICE-03).
- Renovation/energy work: mention regional premiums and paperwork help; schemes differ per region and change often, so verify names first.

## Contact channels

**BE-27 — Click-to-call and messaging.** `[G]` Every phone number is a `tel:` link. Urgent trades: sticky mobile bar "Bel nu" / "Appelez-nous" + callback form (C11). Show opening hours and out-of-hours handling. Offer WhatsApp only if someone answers within the promised time.

**BE-28 — Deposits and payments.** `[L: FOD Economie, since 1 July 2022]` Consumer-facing businesses must offer at least one electronic payment method (transfer counts), without surcharge (economie.fgov.be/nl/themas/verkoop/prijsbeleid/betalingen/verplichting-om-een). `[G]` Online deposits: Bancontact (card + Bancontact Pay, which replaced the Payconiq brand in spring 2026; Wero accepted alongside, per bancontact.com). Structured payment reference on invoices. Show methods near the booking step.

## Seasonality and capacity (for truthful scarcity)

`[G]` The summer construction holiday (bouwverlof), school holidays that now differ between the Flemish and French-speaking communities, and year-end rushes create real capacity limits. Use them for honest capacity lines (SCAR-02): "Voor een renovatie vóór de zomer plannen we de werken nu in" is truthful urgency; a fake countdown is not.

## Accessibility

**BE-29 — Build to WCAG 2.1 AA regardless of legal scope.** `[L: law 5 Nov 2023 → WER Book VIII title 5, in force 28 June 2025; etaamb.openjustice.be/nl/wet-van-05-november-2023_n2023046827.html]`
- In scope: consumer banking and **e-commerce services** (services at a distance via website/app, at the consumer's request, **to conclude a consumer contract**). Online booking + payment or ordering is in scope; a brochure site with a quote form most likely isn't.
- **Micro-enterprises** (< 10 staff and turnover or balance sheet ≤ €2 M) are outside the Belgian law **only until 28 June 2030** (art. 40); later exemption needs a Royal Decree. Narrower than the directive's permanent exemption.
- Benchmark EN 301 549 (≈ WCAG 2.1 AA); `[G]` aim for 2.2 AA. It helps conversion too (CTA-05, FORM-03).

## B2B-only sites

`[G]` Still apply: legal info (BE-08), privacy and cookies (BE-09, BE-14–17), forms and email (BE-10–13), comparisons (BE-23), AI Act where relevant (BE-30, BE-34). Consumer rules BE-18–25 are mostly n/a: report them as one line, "BE-18–25: n/a (B2B only)". B2B advertising must not mislead either (**verify** WER art. VI.105).

**BE-31 — Subsidy claims.** `[G]` Claims like "eligible for the KMO-portefeuille" change often: check the official page first, date the claim, never promise approval. **verify** eligibility.

**BE-32 — Back data-location claims.** `[G]` "Data blijft in België/EU" or "sovereign AI" needs substance: name the hosting location and provider, and any processing outside the EU (BE-09).

**BE-33 — DPA and security documents are trust assets.** `[G]` IT, DPOs and procurement ask for a data processing agreement (GDPR art. 28), a security overview and certifications. Offer them as downloads or "on request" near the FAQ; list only certifications you hold.

## AI features

**BE-30 — Disclose AI assistants.** `[L: AI Act art. 50; digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act]` Since **2 August 2026**, AI systems that talk directly with people must say so at the first interaction unless obvious. The duty sits with the *provider* (the vendor, or you if you build the bot and deploy it under your name); the Digital Omnibus did not delay it. `[G]` Disclose anyway ("Digitale assistent (AI)"). Constrain AI chat and estimators to published prices and conditions; hand binding matters (firm quotes, medical/legal advice) to a human (AI-07).

**BE-34 — Selling AI systems? Your clients' AI Act duties are part of your pitch.** `[G]` Clients who deploy what you build take on duties (AI literacy, chatbot transparency, BE-30). Say in the offer and FAQ who handles what; don't claim "AI Act compliant" without saying for which system and role. **verify** obligations.

## BE/EU audit add-on checklist

- [ ] Languages match service area; Belgian Dutch; hreflang, text switcher, no IP redirect; hero fits longest language
- [ ] Legal info complete (BE-08); no ODR link
- [ ] Privacy link at every form; separate unticked marketing consent
- [ ] Cookies: "Reject all" on layer one, analytics blocked until consent, compact mobile banner, embeds after consent
- [ ] Reviews: verification statement, source + date, current counts, no Google-review incentives
- [ ] Prices incl. VAT; "free" is free; no fake urgency; 30-day reference price
- [ ] Online bookings: withdrawal info, express-start checkbox, withdrawal button, electronic payment, WCAG 2.1 AA
- [ ] Regulated-profession rules checked
- [ ] Click-to-call; opening hours; AI chat disclosed
- [ ] B2B: consumer items as one "n/a" line; subsidy and data-location claims backed; DPA and security documents offered (BE-31–34)
