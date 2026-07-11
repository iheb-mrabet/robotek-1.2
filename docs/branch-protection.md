# Main branch protection

After the workflows have completed at least once, create a ruleset for `main`:

1. Open **Settings → Rules → Rulesets → New branch ruleset**.
2. Target the default branch `main`.
3. Require a pull request before merging.
4. Require approvals and dismiss stale approvals when new commits are pushed.
5. Require status checks to pass.
6. Add these required checks:
   - `Fast gate`
   - `Unit tests`
   - `Aggregated security gate`
7. Require branches to be up to date before merging.
8. Block force pushes and branch deletion.

## Evidence screenshots

Store screenshots in `docs/evidence/branch-protection/` showing:

- the enabled `main` ruleset;
- the three required checks;
- a pull request blocked by a failing gtest;
- a pull request blocked by an unsafe `robot.yaml`;
- a pull request blocked by the security gate.

Screenshots must be captured from the actual GitHub repository because repository settings cannot be configured or proven from source code alone.
