# Main branch governance

Use pull requests and successful review checks for changes to `main`. The shipping documentation cleanup and runner update were reviewed through pull requests with CI, security, and infrastructure checks.

The delivery review on 2 October 2026 found that GitHub does not enforce branch protection on `main`. Review discipline is therefore an operating practice, not an enforced repository guarantee.

Recommended ruleset for a team repository:

1. Target `main`.
2. Require a pull request and review approval.
3. Require the relevant CI, security, and infrastructure status checks.
4. Dismiss stale approvals when code changes.
5. Block force pushes and branch deletion.
6. Provide a narrowly scoped exception for the approved GitOps promotion automation, so it can update only the intended image values without disabling the review rules for human changes.

Confirm the exact current check names and automation behavior before enabling a ruleset. Do not enable rules that silently prevent verified image promotion.
