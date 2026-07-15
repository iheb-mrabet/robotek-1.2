# Main branch protection

After the workflows have completed at least once, we create later a ruleset for `main` ( we can't do it now so we just record the steps for later use ):

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

