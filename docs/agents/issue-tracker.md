# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues. Prefer the `gh` CLI for all operations. If `gh` is not on `PATH`, fall back to VS Code GitHub extension tools (see below).

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v` — `gh` does this automatically when run inside a clone.

## Fallback: VS Code GitHub extension tools

If `gh` is unavailable (e.g. not installed, not authenticated, or not on `PATH`), use the VS Code GitHub extension tools instead:

| `gh` operation | VS Code tool equivalent |
|---|---|
| `gh issue list --label ...` | `github-pull-request_doSearch` with `is:issue is:open label:<label> repo:owner/name` |
| `gh issue view <number>` | `github-pull-request_issue_fetch` with `issueNumber` and `repo` |
| `gh issue list --label ready-for-agent` blocker check | `github-pull-request_issue_fetch` on each blocker; check `.state` field |
| `gh pr create ...` | `github-pull-request_create_pull_request` tool |

**Important**: `github-pull-request_doSearch` searches across all repos by default. Always include `repo:owner/name` in the query to scope results to this repository. To find `owner/name`, run `git remote -v` and parse the GitHub URL, or read it from the repo context attached to the conversation.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments` (or use `github-pull-request_issue_fetch` as fallback).
