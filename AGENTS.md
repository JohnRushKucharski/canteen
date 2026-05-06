# Canteen — Agent Instructions

## Agent skills

### Ralph loop

Autonomously fix all open AFK issues one at a time, using fresh-context subagents, until the queue is empty, a complexity gate triggers, or an error occurs. AFK-safe — no human input required. See `.github/skills/ralph-loop/SKILL.md`.

**Prerequisite**: issues must carry the `ready-for-agent` label before the loop can pick them up. Run the `triage` skill first to move issues from `needs-triage` to `ready-for-agent`.

### Fix issue

Check out an unblocked AFK issue, implement via TDD, run a quality review loop (python-code-review + SOLID + ADR compliance + coverage), and submit a pull request. See `.github/skills/fix-issue/SKILL.md`.

### Issue tracker

Issues live in GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Using default label vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout — one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
