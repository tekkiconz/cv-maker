---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-02b-vision', 'step-02c-executive-summary', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish', 'step-12-complete']
workflowStatus: complete
completedAt: '2026-04-18'
classification:
  projectType: web_app
  domain: general
  complexity: low
  architectureNote: 'Medium architecture discipline — four abstraction layers (DB, storage, LaTeX compiler, frontend) designed for swappability. Tiger Style applies throughout.'
  projectContext: greenfield
inputDocuments: ['_bmad-output/brainstorming/brainstorming-session-20260418-143843.md']
workflowType: 'prd'
---

# Product Requirements Document — CVMaker

**Author:** Huy
**Date:** 2026-04-18

## Executive Summary

CVMaker is a self-hosted personal CV management tool for a single developer-user. It solves the problem of existing CV tools being paywalled, producing low-quality output, or locked into bloated ecosystems (e.g. Microsoft Word). The product compiles professional-grade PDFs from structured profile data via LaTeX templates, served through a lightweight web UI.

**What Makes This Special:** CVMaker combines LaTeX-quality output with a zero-friction web editing experience — no LaTeX knowledge required to edit content, full LaTeX power available for template authoring. The multi-profile architecture powers domain-specific CVs (software engineering, research, freelance) from a single data store without duplication. The tool is personal-first but cloud-ready by design: all major layers (database, file storage, LaTeX compiler, frontend) are abstracted behind swappable interfaces. No subscriptions, no vendor lock-in, no ugly output.

**Classification:** Web application (HTMX + REST API + OpenAPI) · General productivity domain · Low domain complexity, medium architecture discipline · Greenfield

## Success Criteria

### User Success

- Generate a correctly formatted PDF from any profile + template combination without manual LaTeX intervention
- Add or update profile data through the web UI in a single session without friction
- Clone an existing profile and adapt it for a new domain in under 5 minutes
- Zero cost to run — no subscriptions, no external services required in v1

### Technical Success

- Every build failure surfaces a clear error with the LaTeX log — no silent failures
- Data persists reliably across sessions — no silent data loss
- Swapping any abstraction layer requires only config/adapter changes — no business logic rewrites
- Template renders consistently regardless of which profile data is fed in (template correctness is the template author's responsibility)
- All four abstraction layer interfaces are defined before the first feature is implemented

## Product Scope

### MVP (Phase 1)

Profile CRUD + clone, typed section management (Structured + Free Text), section toggle per export, template auto-discovery and validation, split-view workspace, Preview (ephemeral PDF), Build (persistent PDF + download), LaTeX input sanitization, compilation error feedback, Docker Compose runtime, basic README.

### Growth (Phase 2)

Cloud deployment, S3 storage adapter, auth middleware activated, Postgres DB adapter.

### Vision (Phase 3)

Public multi-user deployment if needed. No marketplace planned.

### Explicit v1 Exclusions

Rich text or markdown input · Drag-and-drop section ordering · Template variable customization via UI · Data backup/export · i18n (English only) · Mobile layout · Clickable PDF navigation · Profile metadata beyond name + description · User authentication

## User Journeys

### Journey 1: Huy the Job Applicant — Happy Path

Huy has a software engineering role to apply for. He opens CVMaker, selects his "Software Engineering" profile, and picks the clean single-column LaTeX template from the dropdown. The split-view workspace shows his current data on the left and the PDF preview on the right. He notices his "Projects" section needs a new entry — he adds it through the structured form, hits Preview, and watches the right panel refresh with the compiled PDF. The project renders exactly as expected. He toggles off the "Freelance Work" section (not relevant for this role), hits Preview again, and confirms the one-page layout still holds. Satisfied, he hits Build — the app compiles, saves the PDF to the output folder, and triggers a download.

**Capabilities revealed:** Profile selection, template dropdown, split-view workspace, section toggle per export, Preview (ephemeral), Build (persistent download), structured section editing.

### Journey 2: Huy the Job Applicant — Error Recovery

Huy is updating his "Research" profile for an academic application. He adds a publications section with a paper title containing an ampersand (`&`). He hits Preview — the panel shows a compilation failure with actionable detail. He expands the error log and sees a LaTeX error pointing to the unescaped `&`. The sanitization layer should have caught this — he notes it as a test case, manually escapes it as `\&` for now, and Preview succeeds.

**Capabilities revealed:** Compilation error reporting, LaTeX error log access, graceful failure (app stays usable), input sanitization layer (gap surfaced as a test case).

### Journey 3: Huy the Operator — Setup and Maintenance

Six months after first deploy, Huy wants to add a minimalist two-column LaTeX template he found online. He copies the `.tex` file into the `/templates` directory. On next app start, the template appears in the dropdown — no config changes needed. He selects it, hits Preview with his "Software Engineering" profile, and sees the new layout render. He spots a spacing issue, edits the `.tex` file directly in his editor, reloads, and Previews again. The fix holds.

**Capabilities revealed:** Filesystem-based template auto-discovery, template validation on load, no-UI template management, direct `.tex` file editing as the intended template workflow.

### Journey Requirements Summary

| Capability | Journeys |
|---|---|
| Profile CRUD + selection | 1, 2 |
| Template dropdown + auto-discovery | 1, 3 |
| Split-view workspace | 1 |
| Section toggle per export | 1 |
| Preview (ephemeral) + Build (download) | 1 |
| Structured + free-text section editing | 1, 2 |
| Compilation error reporting + log access | 2 |
| Input sanitization | 2 |
| Graceful failure — app stays usable | 2 |
| Template filesystem drop-in | 3 |
| Template validation on load | 3 |

## Web Application Requirements

CVMaker is a server-rendered MPA built with HTMX. The frontend is a thin consumer of the REST API — no SPA framework, no build toolchain. The backend serves HTML partials and JSON.

**Browser Support:** Modern evergreen browsers — Chrome, Firefox, Safari, Edge (latest stable). No legacy browser support in v1.

**Responsive Design:** Desktop-first. The split-view workspace is not viable on mobile. No mobile breakpoints in v1.

**SEO:** Not applicable — no public-facing pages.

## Functional Requirements

### Profile Management

- **FR1:** User can create a new profile with a name and optional description
- **FR2:** User can view all existing profiles
- **FR3:** User can edit a profile's name, description, and all associated section data
- **FR4:** User can delete a profile
- **FR5:** User can clone an existing profile into a new independent profile

### Section Management

- **FR6:** User can add a Structured section with a predefined field schema (title, organisation, dates, bullet points)
- **FR7:** User can add a Free Text section with a plain text field
- **FR8:** User can edit any section within a profile
- **FR9:** User can delete a section from a profile
- **FR10:** User can toggle individual sections on or off per CV build without deleting them

### Template Management

- **FR11:** The system automatically discovers available LaTeX templates from the templates directory
- **FR12:** The system verifies each discovered template can be compiled before making it selectable
- **FR13:** User can select an active template from the list of verified, discovered templates
- **FR14:** The system excludes invalid templates from selection and reports them at startup

### CV Compilation — Preview

- **FR15:** User can trigger an ephemeral PDF preview of the current profile + template combination
- **FR16:** The system generates a preview PDF without persisting it to storage
- **FR17:** The system renders the preview PDF inline within the workspace
- **FR18:** The system communicates compilation progress to the user

### CV Compilation — Build

- **FR19:** User can trigger a finalized PDF build of the current profile + template combination
- **FR20:** The system saves the built PDF to the configured output location
- **FR21:** The system makes the built PDF available for immediate download
- **FR22:** User can configure the output location for built PDFs

### Error Handling & Security

- **FR23:** The system reports compilation failures to the user with actionable detail
- **FR24:** User can access the full LaTeX error log when compilation fails
- **FR25:** The system sanitizes all user-provided text before passing it to any LaTeX template

### Workspace

- **FR26:** User can edit profile data and view PDF preview simultaneously
- **FR27:** User can select a template and immediately preview its output without losing editing context

## Non-Functional Requirements

### Performance

- Preview compilation completes and renders within 5 seconds for a typical CV on local hardware
- Build compilation completes within 10 seconds for a typical CV
- Page interactions (form edits, section toggles, template selection) respond within 500ms excluding compile time
- LaTeX compilation is async — the UI never blocks or freezes during compile

### Security

- All user-provided text is sanitized before LaTeX template injection — hard invariant, not optional
- LaTeX shell execution (`\write18`, `\immediate\write18`) is blocked at the sanitization layer
- v1 is accessible on localhost only — no auth required
- No user data is transmitted to external services in v1

### Reliability

- The application remains fully usable after any compilation failure — no crash, no corrupt state
- A compilation failure never produces partial or corrupt output files
- Profile data is persisted reliably — no silent data loss on write
- Tiger Style discipline applies throughout: assertions at every boundary, fail fast and explicitly, never silently

### Technical Constraints

- Database access is mediated through an abstract interface; SQLite is the default adapter
- File storage is mediated through an abstract interface; local filesystem is the default adapter
- LaTeX compilation is mediated through an abstract interface; `pdflatex` is the default adapter
- The REST API is the sole entry point for all functionality; OpenAPI spec is auto-generated
- The frontend is a replaceable consumer of the REST API; no business logic lives in frontend templates
- The application runs exclusively via Docker Compose — no direct process execution
- Authentication is activatable via middleware configuration without modifying business logic
