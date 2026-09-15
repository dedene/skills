# Screenshot assets

Use this only when replacing or preparing a screenshot asset, not for every browser observation.

1. Pick the newest PNG from ~/Desktop or ~/Downloads when Peter says “use a screenshot.” Inspect it to confirm the intended UI.
2. Check dimensions with `sips -g pixelWidth -g pixelHeight <file>`. Prefer a 2x source when available and preserve the target asset's expected dimensions.
3. Optimize with `imageoptim <file>` when installed. If unavailable, use an existing suitable optimizer or report that optimization was skipped; do not block a simple replacement on installation. Install tooling only within the requested setup scope.
4. Replace the intended asset, run the relevant build or asset check, and inspect the rendered result. Check CI only when it covers the changed asset and the task includes that workflow.
