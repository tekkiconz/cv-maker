---
stepsCompleted: [1, 2, 3, 4]
inputDocuments: []
session_topic: 'Personal CV management tool — web UI, SQLite, LaTeX templates, PDF generation'
session_goals: 'Define the feature set before building'
selected_approach: 'ai-recommended'
techniques_used: ['SCAMPER Method', 'What If Scenarios', 'Reverse Brainstorming']
ideas_generated: [30]
session_active: false
workflow_completed: true
---

# Brainstorming Session Results

**Facilitator:** Huy
**Date:** 2026-04-18 14:38:43

## Session Overview

**Topic:** Personal CV management tool — web UI, SQLite, LaTeX templates, PDF generation
**Goals:** Define the feature set before building

### Session Setup

Fresh session, no prior context file. Focus is practical feature discovery for a personal-use tool.

## Technique Selection

**Approach:** AI-Recommended Techniques
**Analysis Context:** Concrete/familiar domain, casual tone, goal is actionable feature list

**Recommended Techniques:**

- **SCAMPER Method:** Systematic 7-lens feature expansion — covers Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, Reverse
- **What If Scenarios:** Breaks assumptions to surface non-obvious features after SCAMPER establishes the core
- **Reverse Brainstorming:** Stress-tests by generating failure modes, then flipping them into feature requirements

**AI Rationale:** SCAMPER grounds the session in concrete feature thinking; What If expands into creative territory; Reverse Brainstorming catches gaps and edge cases before committing to a build.

## Technique Execution Results

### SCAMPER Method

**S — Substitute:**
- [SCAMPER-S #1] LaTeX Lock-In (Intentional) — Deliberately stick with LaTeX over HTML/Markdown for print-fidelity and template richness. Renderer is pdflatex, not a browser.
- [SCAMPER-S #2] Database Abstraction Layer — Data access behind an interface from day one. SQLite today, cloud DB tomorrow via config change.
- [SCAMPER-S #3] Web Form as Source of Truth — UI is the primary editing interface. Form shapes what data exists; forces data model to be designed through a UX lens.

**C — Combine:**
- [SCAMPER-C #4] Unified Template-Preview Workspace — Template picker and PDF preview on same page. Select template → preview renders inline. Tweak template → preview hot-reloads.
- [SCAMPER-C #5] Section Toggle Per Export — Each CV section has on/off switch. Different exports include different sections without duplicating data.
- [SCAMPER-C #6] Multi-Profile Architecture — Profile is top-level entity owning a full dataset optimized for one domain (e.g. "Software Engineering", "Research"). CVs built from profile + template + section selection.
- [SCAMPER-C #7] Ephemeral Preview vs. Finalized Export — Preview compiles to in-memory PDF (Python tempfile, served as blob), never written to disk. Build writes named timestamped PDF to output folder.
- [SCAMPER-C #8] Lightweight Profile Identity — Profile has name + optional description only. No tags, metadata, or search. Deliberate restraint for a 5-6 profile use case.

**A — Adapt:**
- [SCAMPER-A #9] Clone Profile Feature — "Duplicate this profile" creates full copy of all CV data under new name. Starting point for new domain variant.
- [SCAMPER-A #10] Template Owns the Layout — Section ordering and visual structure live in the LaTeX template, not the UI. Form supplies data; template decides presentation.
- [SCAMPER-A #11] IDE Split-View Layout — Main workspace is two panels: left is data form for active profile, right is live PDF preview. Editing triggers recompile and preview refresh.

**M — Modify:**
- [SCAMPER-M #12] Preview vs. Build Split — "Preview" button: compile → stream to browser as blob, no save. "Build" button: compile → save to configured output location → trigger download.
- [SCAMPER-M #13] File Storage Abstraction — PDF output through storage interface (strategy + factory). LocalStorage adapter today, S3Adapter tomorrow. Swapping is a config change.
- [SCAMPER-M #14] Typed Section Schema — Two types: Structured (Experience, Education, Projects — fixed fields: title, org, dates, bullets) and Free Text (Summary etc. — plain text only, no markup). LaTeX template renders both.

**P — Put to Other Uses:**
- [SCAMPER-P #15] Multi-Template from One Profile — Template selected via dropdown. Same profile data, different LaTeX template = different CV format. First-class feature.

**E — Eliminate:**
- [SCAMPER-E #16] Auth-Ready but Auth-Free — No authentication in v1. Request handling routed through middleware hooks where auth could slot in later. No user-session assumptions in business logic.
- [SCAMPER-E #17] Deliberate Feature Exclusions (v1) — Explicitly out of scope: rich text/markdown input, drag-and-drop ordering, template variable UI, backup/export.

**R — Reverse:**
- [SCAMPER-R #18] Clickable Preview Navigation (Future Idea) — Clicking section in PDF preview jumps to that section's form fields. Too complex for HTMX v1; parked for future.

### What If Scenarios

- [WHAT-IF #19] Basic README/Doc — Minimal doc covering how to run, add templates, configure storage backend. For future-you after 6 months away.
- [WHAT-IF #20] Layered Compilation Error Feedback — On failure: toast with short summary + collapsible panel with full LaTeX error log. Treats user as a developer.
- [WHAT-IF #21] LaTeX Input Sanitization Layer — All user text escaped before template injection (&, %, $, #, _, {, }, ~, ^, \). Hard pipeline requirement. Closes LaTeX injection vector (\write18 shell execution).
- [WHAT-IF #22] Docker Compose as Primary Runtime — `docker compose up` is the canonical way to run the app. TeX Live lives in the container. Makes deployment to any host trivial.
- [WHAT-IF #23] LaTeX Compiler Abstraction — Compilation through a LatexCompiler interface. LocalPdflatex adapter today, CloudLatexAdapter later. Same strategy/factory pattern as storage and DB.
- [WHAT-IF #24] Template Registration via Filesystem Convention — Drop a .tex file into /templates, app auto-discovers it and adds to dropdown. No UI or config file needed.
- [WHAT-IF #25] English Only (v1) — No i18n, no multilingual support. Explicit cut.

### Reverse Brainstorming

- [REVERSE #26] Graceful Build Failure — Build/preview failures never crash silently. Always return clear error state to UI with LaTeX log. App stays usable after failed compile.
- [REVERSE #27] Template Validation on Load — Validate .tex file is parseable when app starts or new template is dropped in. Broken template never reaches the UI.
- [REVERSE #28] Input Sanitization as Hard Requirement — Sanitization is a required pipeline step before any user data touches a LaTeX template. Architectural constraint, not a bolt-on.

### Development Philosophy

- [DEV-PRINCIPLE #29] Tiger Style Development — Safety > Performance > Developer Experience. Assertions at every function boundary, fail fast explicitly, zero technical debt, simple explicit control flow.

### Additional (Post-Session)

- [ARCH #30] API-First, Client-Agnostic Design — Backend exposes clean REST API with OpenAPI spec auto-generated (FastAPI). HTMX consumes it today; any frontend framework slots in tomorrow. No HTML templating in business logic.

---

## Idea Organization and Prioritization

### Theme 1: Core Architecture & Stack
*The foundational technical decisions that everything else sits on.*

- LaTeX as renderer — stays, for print fidelity and template power
- Database abstraction layer — SQLite today, cloud DB tomorrow
- File storage abstraction — LocalStorage adapter now, S3 adapter later
- LaTeX compiler abstraction — pdflatex in container today, cloud API later
- Docker Compose as primary runtime
- API-first with OpenAPI generation — frontend is a consumer, not a dependency
- Tiger Style — assertions everywhere, fail fast, zero technical debt

**Abstraction layer summary:**

| Layer | Today | Tomorrow |
|---|---|---|
| Database | SQLite | Postgres / cloud |
| File storage | Local disk | S3 |
| LaTeX compiler | pdflatex | Cloud LaTeX API |
| Frontend | HTMX | React / anything |

### Theme 2: Profile & Data Model
*How CV data is structured and managed.*

- Multi-profile architecture — Profile owns full dataset per domain
- Lightweight profile identity — name + optional description only
- Clone profile — duplicate full profile as starting point
- Web form as source of truth
- Typed section schema — Structured (fixed fields) + Free Text (plain text only)

### Theme 3: Template System
*How LaTeX templates are managed and selected.*

- Template owns the layout — ordering and structure in .tex, not UI
- Multi-template from one profile — dropdown selection
- Filesystem auto-discovery — drop .tex into /templates, appears in dropdown
- Template validation on load — fail fast before hitting UI

### Theme 4: Preview & Build Workflow
*The core user interaction loop.*

- IDE split-view layout — left: form, right: PDF preview
- Unified template+preview page — no file switching
- Preview button — ephemeral, in-memory blob, never saved
- Build button — saves to output location, triggers download
- Section toggle per export — per-export on/off switches

### Theme 5: Security & Reliability
*Keeping the tool trustworthy and debuggable.*

- LaTeX input sanitization — hard pipeline requirement, not optional
- No LaTeX injection — \write18 and shell execution closed
- Layered compilation error feedback — toast + collapsible log
- Graceful build failure — app stays usable after failed compile
- Template validation on load

### Theme 6: Deployment & Future-Proofing
*Decisions that keep options open without over-engineering now.*

- Auth-ready but auth-free — middleware hooks exist, no auth v1
- API-first, client-agnostic — OpenAPI spec generated
- Docker Compose as primary runtime
- Basic README
- English only (v1 explicit cut)

### Explicit v1 Exclusions

- No rich text / markdown input
- No drag-and-drop section reordering
- No template variable customization via UI
- No backup / data export
- No i18n
- No clickable PDF navigation (future)
- No profile metadata beyond name + description
- No user authentication (but hooks ready)

---

## Session Summary and Insights

**Total Ideas Generated:** 30 across 3 techniques + 1 architecture addition
**Themes Identified:** 6 themes + explicit exclusions list

**Key Achievements:**
- Complete feature set defined before a single line of code
- Consistent abstraction philosophy across all layers (DB, storage, LaTeX, frontend)
- Clear v1 scope with deliberate exclusions — no scope creep risk
- Security requirements (sanitization) elevated to architectural constraints
- Tiger Style adopted as development philosophy

**Breakthrough Moments:**
- Multi-profile architecture as the top-level data entity shapes the entire schema
- Ephemeral preview vs. finalized build as a first-class UX distinction
- Realizing multi-template was already solved by the profile+template+dropdown combo
- API-first design extending the abstraction philosophy to the frontend layer

**Your Next Steps:**
1. Run `bmad-create-prd` — turn this feature set into a structured PRD
2. Run `bmad-create-architecture` — define DB schema, API contracts, and system design
3. Start with the data model (Profile, Section types) as it anchors everything else
