# my-pull-requests

Summarize the GitHub pull requests assigned to the authenticated user for the workspace repository when running Codex inside VS Code. Use this prompt whenever you need an actionable status board before coding or context-switching.

## Workflow

1. **Confirm repository context**
   - Run `git rev-parse --show-toplevel` to ensure you are inside a Git repository.
   - Use `gh repo view --json nameWithOwner -q .nameWithOwner` to capture the `<owner>/<repo>` slug that all subsequent `gh pr` commands need.
2. **Identify the current GitHub user**
   - Execute `gh api user -q .login` to record the signed-in username.
   - If authentication fails, pause and run `gh auth login` before retrying the prompt.
3. **List open pull requests assigned to the user**
   - Call `gh pr list --repo <owner>/<repo> --assignee <login> --state open --json number,title,updatedAt,url`.
   - If no results are returned, report that there are no open PRs assigned to the user and stop.
4. **Collect rich details for each PR**
   - For every PR number, run:
     ```
     gh pr view <number> --repo <owner>/<repo> \
       --json title,number,url,headRefName,baseRefName,author,assignees,reviewDecision,reviewRequests,statusCheckRollup,mergeStateStatus,latestReviews,body,updatedAt
     ```
   - Parse `statusCheckRollup` to flag failed or pending checks and capture their names.
   - Use `reviewDecision`, `reviewRequests`, and `latestReviews` to detect whether reviews are outstanding, approved, or require changes.
   - Note any blockers (merge conflicts, draft state, failing checks) and suggest next actions such as addressing feedback, re-running CI, or pinging reviewers.
5. **Compose the response**
   - Present each PR with: number, title, branch pair (head → base), short purpose blurb (from the PR body), latest update time, outstanding tasks, review status, and CI state.
   - Highlight PRs that are waiting for reviewer attention or have failing checks so the user can follow up immediately.
   - If every check passed and no blockers remain, recommend merging or notifying stakeholders.
6. **Handle errors and edge cases**
   - If GitHub CLI commands fail (network, auth, or missing repo), state the issue and provide the remediation command (`gh auth login`, `gh repo set-default`, etc.).
   - When the repo is private or inaccessible, note the limitation and suggest verifying permissions.

## Examples

- After opening a repository in VS Code, run `prompt my-pull-requests` to see every open PR assigned to you plus its review/CI state.
- Use the prompt before stand-up to know which PRs are blocked on reviewers versus awaiting your updates.

## Notes

- Requires GitHub CLI (`gh`) with authenticated access to the repository remote.
- The prompt operates within the currently opened VS Code workspace; ensure you are in the correct repo before invoking it.
- Works best when PR titles and bodies succinctly describe their scope, allowing Codex to provide meaningful summaries.
