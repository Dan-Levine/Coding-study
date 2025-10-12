# agents.md — Codex-Web Automation & Verification

This repo uses **Codex Web** as the primary automation and CI agent.  
Codex is authorized to **create branches, push commits, and open pull requests automatically**.  
Human maintainers review, verify, and merge only after successful validation.

---

## Global Rules

1. **Single source of truth:** `main` branch.  
2. **No direct commits to `main`.**  
   Codex must always use a feature/fix/verify branch and open a PR.  
3. **Task lifecycle:**  
   `Proposed → In Progress → PR Open → Merged → Verified → Done`.  
4. **Verification-first policy:**  
   A task is not “Done” until PR is merged **and** verified per the “Verification Playbook.”  
5. **Anti-hallucination rule:**  
   - PRs must list all affected file paths and diffs.  
   - Codex must verify file existence and repo structure before claiming success.  
   - If verification fails, Codex must set the task to `Blocked` and create a new issue summarizing what failed.

---

## GitHub Permissions & Behavior

- **Required permissions:**  
  - Read/write access to this repository only.  
  - Ability to create branches and pull requests.  
- **Automatic PR behavior:**  
  - Codex Web creates a new branch for each change.  
  - PR title and description are generated from the task metadata.  
  - Maintainers receive the PR ready for review—no manual PR creation required.

---

## Branching & PR Conventions

- **Feature branches:** `feat/<area>-<slug>`  
- **Fix branches:** `fix/<area>-<slug>`  
- **Verification branches:** `verify/<task-id>`  

**PR Title Format**
```
<type>: <concise change summary>
```

**Standard PR Checklist (auto-filled by Codex):**
- [ ] Clear summary and intent  
- [ ] List of all changed file paths  
- [ ] Verification notes or logs  
- [ ] Risks or side effects  
- [ ] Next steps or follow-ups  
- [ ] No direct modification to `tasks/tasks.json` (except in verification PRs)

---

## Agent Roles & Auto-PR Templates

### 🧠 ContentAgent (Codex)
**Goal:** Add or modify `.tex` files for new content.

**Codex Task Template**
```
Repo: <owner>/<repo> (branch: main)
Task: Add or update topic "<title>" as tex/<slug>.tex.
Actions:
1. Create branch feat/content-<slug>.
2. Add tex/<slug>.tex (valid LaTeX.js, minimal packages).
3. Validate file creation and include expected sections.
4. Open PR with:
   - File path summary
   - Render expectations
   - No manifest edits (handled by NavAgent)
```

**Outputs:**
- New `.tex` file(s)
- Screenshots/logs if rendering tested

---

### 🧩 NavAgent (Codex + Python)
**Goal:** Maintain navigation and search index.

**Codex Task Template**
```
Repo: <owner>/<repo>
Task: Regenerate nav/search manifests.
Actions:
1. Create branch feat/nav-rebuild.
2. Run python tools/build.py.
3. Commit tex/index.json and assets/search.json if changed.
4. Open PR "chore: rebuild nav/search" with:
   - Diff summary
   - Added/removed slugs
   - Validation output (manifest keys)
```

**Outputs:**
- Updated `tex/index.json`
- Updated `assets/search.json`
- Log summary

---

### 🧪 TestAgent (Codex)
**Goal:** Validate LaTeX.js rendering and JSON integrity.

**Codex Task Template**
```
Repo: <owner>/<repo>
Task: Perform headless smoke test.
Actions:
1. Create branch feat/test-smoke.
2. Add scripts/smoke.md describing test results.
3. Validate index.html load (default + another slug).
4. Log console errors and screenshot (if supported).
5. Open PR "test: smoke verification" with logs.
```

**Outputs:**
- Test report or markdown file with logs
- PR includes a clear pass/fail summary

---

### 🐍 PyAgent (Codex)
**Goal:** Improve or validate Python automation.

**Codex Task Template**
```
Repo: <owner>/<repo>
Task: Improve Python tooling and CI checks.
Actions:
1. Create branch feat/py-updates.
2. Edit tools/build.py for error handling, validation, etc.
3. Update .github/workflows/build.yml to fail on invalid JSON.
4. Run test build and include logs in PR.
5. Open PR "feat: improve build.py validation".
```

**Outputs:**
- Updated tooling
- Verified CI pipeline logs

---

## Task Registry (`tasks/tasks.json`)

Only **Codex (via verification PR)** or human maintainers may edit this file.

Each entry:
```json
{
  "id": "T-0001",
  "title": "Add Algorithms Section",
  "labels": ["content"],
  "state": "Verified",
  "issue": 7,
  "pr": 12,
  "outputs": {
    "files": ["tex/algorithms.tex"],
    "manifest_entries": ["algorithms"]
  },
  "verified_at": "2025-10-12T15:30:00Z",
  "verified_by": "maintainer_handle"
}
```

---

## Verification Playbook (Mandatory After Merge)

1. **File Presence**
   - Check that all new/edited files exist on `main`.
2. **JSON Validation**
   - Run:
     ```
     python -m json.tool tex/index.json
     python -m json.tool assets/search.json
     ```
3. **Render Sanity**
   - Serve locally (`python -m http.server 8080`)
   - Open:
     - `index.html?file=<default>`
     - `index.html?file=<slug>`
   - Confirm no console errors.
4. **GitHub Pages Test**
   - Confirm same results at live URL.
5. **Verification PR**
   - Codex opens `verify/<task-id>` PR.
   - Updates `tasks/tasks.json` → state “Done” with evidence.

---

## CI Guardrails

- Workflow: `.github/workflows/build.yml`
  - Regenerate `index.json` and `search.json`
  - Validate JSON structure
  - Fail on missing files or schema mismatch
- Future checks:
  - Dead link detection
  - CSP verification
  - Automated smoke render

---

## Codex Web Command Library

**Bootstrap Project**
```
Initialize full LaTeX.js site.
- Create: index.html, assets/site.css, tex/example.tex, tools/build.py, tasks/tasks.json, .github/workflows/build.yml, agents.md
- Ensure python tools/build.py runs and generates tex/index.json + assets/search.json
- Open PR: "feat: bootstrap project"
```

**Add New Topic**
```
Add new LaTeX topic "Dynamic Programming Overview".
- Branch: feat/content-dp
- Generate tex/dynamic-programming.tex
- Open PR: "feat: add DP overview" with checklist and expected render
```

**Rebuild Nav**
```
Regenerate nav/search indexes after new topics.
- Branch: feat/nav-rebuild
- Run python tools/build.py
- Open PR: "chore: rebuild nav"
```

**Verify Task**
```
Verification for T-0001.
- Branch: verify/T-0001
- Confirm merged PR, JSON validity, and rendering
- Update tasks/tasks.json → Done
- Open PR: "verify: T-0001 complete"
```

---

## Hallucination Safeguards

| Risk | Mitigation |
|------|-------------|
| Claimed file creation without evidence | Require file path list + diff in PR |
| Updating tasks prematurely | Block edits to `tasks/tasks.json` except in verification PRs |
| Manifest not regenerated | CI check compares `tex/` vs `tex/index.json` |
| LaTeX incompatibility | Maintain approved LaTeX subset (no heavy packages) |
| Missing logs | Codex must attach or inline logs before PR submission |

---

## Human Maintainer Duties

- Review PRs for:
  - Structural correctness
  - JSON validity
  - Rendered LaTeX sanity
- Merge only verified PRs.
- Oversee Codex’s adherence to branch & PR conventions.
- Approve verification PRs when all checks pass.

---

_Last updated: 2025-10-12_
