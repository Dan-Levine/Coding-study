# agents.md — Codex-Ready Operations Guide

## Purpose
Define how human maintainers and OpenAI Codex collaborate on this repo (Interview Prep Guide: LaTeX.js + GitHub Pages) with **verification-first** rules to avoid hallucinations and ensure only true, merged outcomes are recorded.

---

## Safety & Verification Rules (Read First)
1. Source of truth = repo `main` branch. Never trust Codex output blindly.
2. A task is “Done” only after:
   - The PR is merged into `main`.
   - Post-merge verification passes (see “Verification Playbook”).
3. Task list updates must reflect **observed repo state** (files, JSON, links) — not intentions or draft PRs.
4. Codex must include diffs, file paths, and reasons in PR descriptions; humans verify line-by-line.
5. If any verification step fails, revert task status to “Blocked” and open/annotate an issue.

---

## Roles

### 🧠 ContentAgent (Codex)
Goal: Create or revise `.tex` files.

Responsibilities:
- Generate topic outlines and produce valid LaTeX (`.tex`) without external packages.
- Keep structure simple so LaTeX.js renders cleanly.
- Add entries to manifest only after verifying file presence.

Default trigger:
- Label: `content`.
- Issue comment: `@codex content: add <topic> with outline <...>`.

Required outputs (PR):
- New/updated `tex/*.tex` with clear sections.
- PR description: list of files, snippets, and rendered expectations.

Verification gates (human + TestAgent):
- Check `.tex` compiles in LaTeX.js (via headless test).
- Confirm `tex/index.json` maps to the new file and routing works.

---

### 🧩 NavAgent (Codex + Python)
Goal: Maintain navigation and search indices.

Responsibilities:
- Run `tools/build.py` to regenerate `tex/index.json` and `assets/search.json`.
- Respect alphabetical/grouping logic; keep slugs stable.

Default trigger:
- Label: `navigation`.
- Issue comment: `@codex nav: rebuild manifest`.

Required outputs (PR):
- Updated `tex/index.json`, `assets/search.json`.
- PR description includes a diff summary and a list of discovered `.tex` files.

Verification gates:
- Ensure all `path` entries exist and 200-OK via local server or Pages preview.
- Confirm default slug loads content in browser.

---

### 🧪 TestAgent (Codex)
Goal: Validate site integrity.

Responsibilities:
- Headless render test of `index.html`:
  - Confirm LaTeX.js loads from CDN.
  - Render at least the default slug and one non-default.
  - Capture console errors (fail on CSP/CORS/404).
- Link/layout smoke check:
  - Sidebar builds from `tex/index.json`.
  - Route switch updates active state and content.

Default trigger:
- Label: `test`.
- Issue comment: `@codex test: headless smoke`.

Required outputs (PR or CI log):
- Test script and artifacts (screenshots/logs) attached or linked.
- A pass/fail summary with actionable errors.

Verification gates:
- Maintainer reviews logs and artifacts.
- Re-run locally if needed.

---

### 🐍 PyAgent (Codex)
Goal: Improve Python tooling and CI.

Responsibilities:
- Extend `tools/build.py` (perf, robustness).
- Add linters or pre-commit hooks (optional).

Default trigger:
- Label: `python`.
- Issue comment: `@codex python: enhance build tooling`.

Required outputs:
- Updated scripts and documentation with examples.

Verification gates:
- CI run green; no breaking changes to JSON schema.

---

### 🤝 Maintainers (Human)
- Define tasks/issues precisely.
- Enforce verification before “Done”.
- Merge PRs only when checklists pass.

---

## Task Lifecycle

States:
- `Proposed` → `In Progress` → `PR Open` → `Merged` → `Verified` → `Done`
- On failure: `Blocked` (link to failing step/log).

Tasks registry (machine-readable):
- File: `tasks/tasks.json`
- Schema:

    {
      "tasks": [
        {
          "id": "T-0001",
          "title": "Add DP cheatsheet",
          "labels": ["content"],
          "state": "Verified",
          "issue": 42,
          "pr": 101,
          "outputs": {
            "files": ["tex/dynamic-programming.tex"],
            "manifest_entries": ["dynamic-programming"],
            "screenshots": ["artifacts/dp.png"]
          },
          "verified_at": "2025-10-12T15:30:00Z",
          "verified_by": "maintainer_github_handle"
        }
      ]
    }

Update policy:
- Only Codex (via PR) or maintainers may change `tasks/tasks.json`.
- `state` can move to `Done` **only after** post-merge verification (“Verification Playbook”) and must include `verified_at` and `verified_by`.

---

## Verification Playbook (Post-Merge)

1) Files present
   - Confirm new/changed files exist on `main`:
     - `tex/*.tex` present.
     - `tex/index.json` and `assets/search.json` updated if nav changed.

2) Headless render (local)
   - Serve repo root (e.g., `python -m http.server 8080`) and open:
     - `http://localhost:8080/index.html?file=<default>`
     - Another slug: `... ?file=<other>`
   - Ensure no console errors; content renders.

3) Navigation & Routing
   - Sidebar entries correspond to `tex/index.json`.
   - Active state and URL update correctly.

4) Pages publish check
   - If Pages is enabled: visit the public URL for same checks.

5) Record result
   - Update `tasks/tasks.json` with state `Verified` → `Done` (with timestamp/user).
   - If any step fails: set `Blocked`, open/annotate issue with logs and steps to reproduce.

---

## Codex Command Templates (Issue Comments)

Content (new topic):
- `@codex content: add "Binary Search Tree Guide" with sections: intro, invariants, insert/delete, traversal, complexity table. Produce tex/bst.tex and propose a short summary for search.json. Do not update tasks until PR is merged.`

Navigation rebuild:
- `@codex nav: rebuild manifest and search index via tools/build.py. If changes detected, open PR with a diff summary. Do not change tasks/tasks.json.`

Headless smoke test:
- `@codex test: run headless render of index.html for default and "graphs" slugs; attach screenshots and console logs; fail on any network/CSP/404. No tasks update.`

Python tooling:
- `@codex python: add simple link checker and wire into TestAgent flow; output CI annotations on broken paths. Do not alter tasks/tasks.json.`

Important guardrails for every Codex task:
- Always include changed file list and exact paths in PR description.
- Never update `tasks/tasks.json` in the same PR that adds code/content.
- After merge, create a follow-up PR solely to move tasks to `Verified/Done` with evidence links.

---

## Labels & Branching

Labels:
- `content`, `navigation`, `test`, `python`, `blocked`, `needs-verification`

Branches:
- Feature: `feat/<area>-<slug>`
- Fix: `fix/<area>-<slug>`
- Verification PRs: `verify/<task-id>`

---

## PR Checklist (paste into PR templates)

- [ ] Lists all changed files with full paths.
- [ ] For content: `.tex` renders in LaTeX.js locally (screenshot or log attached).
- [ ] For nav: `tools/build.py` rerun; `tex/index.json` and `assets/search.json` updated.
- [ ] No broken links; no console errors (attach logs).
- [ ] No changes to `tasks/tasks.json` in this PR (unless this is a verification PR).

Verification PR (after merge of feature PR):
- [ ] References merged commit/PR IDs.
- [ ] Confirms checks from “Verification Playbook” passed.
- [ ] Updates `tasks/tasks.json` with `Verified` → `Done`, `verified_at`, `verified_by`.

---

## Minimal File Map

- `index.html` — SPA shell with LaTeX.js web component, sidebar + content pane.
- `assets/site.css` — layout & typography.
- `assets/search.json` — optional simple search index (generated).
- `tex/*.tex` — content sources.
- `tex/index.json` — nav/route manifest (generated).
- `tools/build.py` — Python manifest/search generator.
- `.github/workflows/build.yml` — rebuild manifest on push.
- `tasks/tasks.json` — single source of truth for task states (never optimistic).

---

## Common Hallucinations & Mitigations

Pitfall: Claims that files exist or tests passed without artifacts.
- Mitigation: Require file path list, artifacts, and reproducible steps.

Pitfall: Editing `tasks/tasks.json` before merge.
- Mitigation: Block PRs that change `tasks/tasks.json` unless it’s a verification PR.

Pitfall: Incorrect LaTeX packages or commands unsupported by LaTeX.js.
- Mitigation: Keep LaTeX minimal; maintain a known-good snippet library.

Pitfall: “Updated nav” without running `tools/build.py`.
- Mitigation: CI job compares manifest to directory listing; fails on mismatch.

---

## Human Review Tips
- Skim diffs in `tex/` for clarity and compile-ability.
- Open devtools console during local run; errors = stop the merge.
- Verify routing by clicking multiple sidebar links.
- Defend stable slugs; changing slugs breaks links.

---

Last updated: 2025-10-12
```0