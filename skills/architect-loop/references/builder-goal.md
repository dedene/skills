# Builder contract rationale

The worker contract in SKILL.md is the canonical dispatch policy.

- Review before implementation surfaces actual objections; "no objections" is a valid outcome. Do not reward manufactured disagreement.
- Stabilize shared interfaces only where concurrent work needs them. Record a superseding decision when evidence or the user changes the contract.
- Independent review helps with high-risk changes. Inspect raw commands, code, and visual evidence; narrative alone is insufficient, but qualitative evidence is valid.
- Explicit allowed actions keep delegation from expanding authority. A reviewer approval, commit capability, or working network never grants permission to publish.
- The handoff supports recovery. If it is missing, reconcile the working tree and logs before redispatching work.
