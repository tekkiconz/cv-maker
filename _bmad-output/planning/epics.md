---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
workflowStatus: complete
completedAt: '2026-04-18'
inputDocuments: ['_bmad-output/planning/prd.md', '_bmad-output/planning/architecture.md']
---

# CVMaker - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for CVMaker, decomposing the requirements from the PRD and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: User can create a new profile with a name and optional description
FR2: User can view all existing profiles
FR3: User can edit a profile's name, description, and all associated section data
FR4: User can delete a profile
FR5: User can clone an existing profile into a new independent profile
FR6: User can add a Structured section with a predefined field schema (title, organisation, dates, bullet points)
FR7: User can add a Free Text section with a plain text field
FR8: User can edit any section within a profile
FR9: User can delete a section from a profile
FR10: User can toggle individual sections on or off per CV build without deleting them
FR11: The system automatically discovers available LaTeX templates from the templates directory
FR12: The system verifies each discovered template can be compiled before making it selectable
FR13: User can select an active template from the list of verified, discovered templates
FR14: The system excludes invalid templates from selection and reports them at startup
FR15: User can trigger an ephemeral PDF preview of the current profile + template combination
FR16: The system generates a preview PDF without persisting it to storage
FR17: The system renders the preview PDF inline within the workspace
FR18: The system communicates compilation progress to the user
FR19: User can trigger a finalized PDF build of the current profile + template combination
FR20: The system saves the built PDF to the configured output location
FR21: The system makes the built PDF available for immediate download
FR22: User can configure the output location for built PDFs
FR23: The system reports compilation failures to the user with actionable detail
FR24: User can access the full LaTeX error log when compilation fails
FR25: The system sanitizes all user-provided text before passing it to any LaTeX template
FR26: User can edit profile data and view PDF preview simultaneously
FR27: User can select a template and immediately preview its output without losing editing context

**Total FRs: 27**

### NonFunctional Requirements

NFR-P1: Preview compilation completes and renders within 5 seconds for a typical CV on local hardware
NFR-P2: Build compilation completes within 10 seconds for a typical CV
NFR-P3: Page interactions (form edits, section toggles, template selection) respond within 500ms excluding compile time
NFR-P4: LaTeX compilation is async — the UI never blocks or freezes during compile
NFR-S1: All user-provided text is sanitized before LaTeX template injection — hard invariant, not optional
NFR-S2: LaTeX shell execution (\write18, \immediate\write18) is blocked at the sanitization layer
NFR-S3: v1 is accessible on localhost only — no auth required
NFR-S4: No user data is transmitted to external services in v1
NFR-R1: The application remains fully usable after any compilation failure — no crash, no corrupt state
NFR-R2: A compilation failure never produces partial or corrupt output files
NFR-R3: Profile data is persisted reliably — no silent data loss on write
NFR-R4: Tiger Style discipline applies throughout: assertions at every boundary, fail fast and explicitly, never silently

**Total NFRs: 12**

### Additional Requirements

From Architecture — technical requirements that affect implementation:

- **Interfaces first**: All 4 abstraction layer interfaces (DatabaseProtocol, StorageProtocol, LatexCompilerProtocol, TemplateDiscoveryProtocol) must be defined before any feature implementation begins
- **Scaffold**: Manual project scaffold — no CLI starter. Epic 1 Story 1 is Docker Compose + FastAPI health endpoint
- **SQLAlchemy Base**: Single `models/base.py` — ONLY source of Base. All models import from here
- **Alembic**: Schema-first migrations. Each model/table gets its own migration version
- **Section router auto-registration**: `apis/sections/__init__.py` auto-registers all section routers
- **Profile clone**: Service-level deep copy — `profile_service.clone_profile()` reads then inserts. No DB-level COPY
- **Auth middleware stub**: `app/middleware/auth.py` exists as empty stub (TC7) — activatable without business logic changes
- **Loop bounds**: All loops use constants from `constants/limits.py`
- **Dependency injection**: All wiring via FastAPI `Depends()` in `apis/dependencies.py`
- **Docker Compose only**: No direct process execution. TeX Live in container

### UX Design Requirements

No UX design document exists. UI requirements are captured in PRD (FR26-FR27, User Journeys) and Architecture (HTMX + Jinja2 views structure).

Key UI requirements from PRD:
- Split-view workspace: left panel (profile editor), right panel (PDF preview) — FR26
- Template selector dropdown — FR13, FR27
- Compilation progress indicator — FR18
- Error log collapsible panel — FR24
- Section toggle switches — FR10

### FR Coverage Map

FR1:  Epic 1 — Create profile
FR2:  Epic 1 — View all profiles
FR3:  Epic 1 — Edit profile
FR4:  Epic 1 — Delete profile
FR5:  Epic 1 — Clone profile
FR6:  Epic 2 — Add Structured section
FR7:  Epic 2 — Add Free Text section
FR8:  Epic 2 — Edit section
FR9:  Epic 2 — Delete section
FR10: Epic 2 — Toggle section on/off
FR11: Epic 3 — Auto-discover templates
FR12: Epic 3 — Validate templates on load
FR13: Epic 3 — Select active template
FR14: Epic 3 — Exclude invalid templates
FR15: Epic 4 — Trigger preview
FR16: Epic 4 — Ephemeral PDF (no persist)
FR17: Epic 4 — Inline PDF preview
FR18: Epic 4 — Compilation progress
FR19: Epic 4 — Trigger build
FR20: Epic 4 — Save built PDF
FR21: Epic 4 — Download built PDF
FR22: Epic 4 — Configure output location
FR23: Epic 4 — Report compilation failures
FR24: Epic 4 — Access LaTeX error log
FR25: Epic 4 — Sanitize user text (LaTeX injection prevention)
FR26: Epic 4 — Split-view workspace
FR27: Epic 4 — Template switching without context loss

## Epic List

### Epic 1: Project Foundation & Profile Management
Users can set up the application and manage their CV profiles — create, view, edit, delete, clone, and add contact information. This is the foundational epic everything else builds on.
**FRs covered:** FR1, FR2, FR3, FR4, FR5
**Also includes:** Project scaffold, Docker Compose, all 4 abstraction layer interfaces defined, profile contacts

### Epic 2: CV Section Authoring
Users can build out the full content of a CV by adding, editing, and toggling structured sections (experience, education, projects, skills, certifications, languages, publications) and free text sections.
**FRs covered:** FR6, FR7, FR8, FR9, FR10

### Epic 3: Template System
Users can drop LaTeX templates into the filesystem and have them automatically discovered and validated. They can select a template to use for compilation.
**FRs covered:** FR11, FR12, FR13, FR14

### Epic 4: CV Compilation Workspace
Users can preview and build PDFs from any profile + template combination in a split-view workspace, with real-time progress feedback, LaTeX sanitization, error reporting with log access, and PDF download.
**FRs covered:** FR15, FR16, FR17, FR18, FR19, FR20, FR21, FR22, FR23, FR24, FR25, FR26, FR27

---

## Stories

### Epic 1: Project Foundation & Profile Management

#### Story 1.1: Initialize Project Scaffold & Docker Compose

**As a** developer,
**I want** a running Docker Compose environment with a healthy FastAPI app, working SQLite connection, verified LaTeX compilation, and all four abstraction layer interfaces defined,
**so that** every subsequent story can be implemented against a stable, testable foundation.

**Acceptance Criteria:**

1. `docker compose up` starts without errors and `/health` returns `{"status": "ok"}` with HTTP 200.
2. The health endpoint performs a real SQLite query (e.g. `SELECT 1`) and includes `{"db": "ok"}` in the response — no mock.
3. The health endpoint invokes `pdflatex --version` inside the container and includes `{"latex": "ok"}` in the response — proving TeX Live is available.
4. The four interface files exist and are importable with no errors:
   - `app/interfaces/database.py` — `DatabaseProtocol` (Python Protocol)
   - `app/interfaces/storage.py` — `StorageProtocol` (Python Protocol)
   - `app/interfaces/latex_compiler.py` — `LatexCompilerProtocol` (Python Protocol)
   - `app/interfaces/template_discovery.py` — `TemplateDiscoveryProtocol` (Python Protocol)
5. `app/models/base.py` exists and is the sole source of `Base = declarative_base()`.
6. `app/middleware/auth.py` exists as an empty stub (no logic, no imports beyond what's needed to mount it).
7. `app/constants/limits.py` exists with at least one placeholder constant (e.g. `MAX_PROFILES = 1000`).
8. `app/constants/enums.py` exists with `ContactType` enum (`email`, `phone`, `github`, `linkedin`, `website`, `twitter`).
9. `app/configs/settings.py` exists and uses Pydantic Settings to read `DATABASE_URL`, `STORAGE_PATH`, `OUTPUT_PATH`, `TEMPLATES_PATH` from environment.
10. `pyproject.toml` is present with dependencies, pytest configured, and ruff configured.
11. `.env.example` documents all required environment variables.
12. `apis/dependencies.py` exists (may be mostly empty stubs at this stage).
13. Tiger Style: health endpoint contains at minimum one input assertion (method is GET) and one output assertion (response status is 200 before returning).

**Notes:**
- Interfaces use Python `Protocol` (structural typing), NOT `ABC`.
- No business logic in this story — scaffold only.
- All four adapters (`sqlite_database.py`, `local_storage.py`, `pdflatex_compiler.py`, `filesystem_template_discovery.py`) may be stubbed (raise `NotImplementedError`) — they are wired up in later stories.

---

#### Story 1.2: Create and List Profiles

**As a** user,
**I want** to create a new CV profile with a name and optional description, and see all my existing profiles listed,
**so that** I can start organizing my CV data.

**FRs:** FR1, FR2

**Acceptance Criteria:**

1. `POST /api/profiles` with `{"name": "...", "description": "..."}` creates a profile and returns the created profile with its generated `id`, `name`, `description`, `created_at`, `updated_at`.
2. `POST /api/profiles` with `description` omitted also succeeds — description is optional.
3. `POST /api/profiles` with a missing or empty `name` returns HTTP 422 with a validation error.
4. `GET /api/profiles` returns a list of all profiles (may be empty list `[]`).
5. The `Profile` SQLAlchemy model is defined in `app/models/profile.py` and imports `Base` from `app/models/base.py`.
6. An Alembic migration version exists that creates the `profiles` table.
7. The `ProfileService` in `app/services/profile_service.py` implements `create_profile()` and `list_profiles()` against the `DatabaseProtocol` interface.
8. `app/schemas/profile.py` defines `ProfileCreate`, `ProfileRead`, and `ProfileList` Pydantic models.
9. The profile router (`app/apis/profiles.py`) uses `Depends()` from `apis/dependencies.py` for service injection — no direct instantiation in the router.
10. A unit test file `app/services/profile_service.test.py` exists with tests for `create_profile` and `list_profiles` using a test-double database.
11. Tiger Style: `create_profile()` asserts that the input name is non-empty before any DB call, and asserts the returned profile has a non-None `id` after insert.

**Notes:**
- The `sqlite_database.py` adapter must be functional for this story (not just a stub).
- The Alembic migration for `profiles` is the first migration version.

---

#### Story 1.3: Edit Profile Details

**As a** user,
**I want** to update a profile's name and description,
**so that** I can rename or re-describe a profile as my needs evolve.

**FRs:** FR3 (partial — profile-level fields only; section data editing is in Epic 2)

**Acceptance Criteria:**

1. `PATCH /api/profiles/{profile_id}` with `{"name": "new name"}` updates the profile name and returns the updated profile.
2. `PATCH /api/profiles/{profile_id}` with `{"description": "new description"}` updates only the description.
3. `PATCH /api/profiles/{profile_id}` with both fields updates both.
4. `PATCH /api/profiles/{profile_id}` for a non-existent `profile_id` returns HTTP 404.
5. `GET /api/profiles/{profile_id}` returns a single profile by ID with HTTP 200, or HTTP 404 if not found.
6. `updated_at` is updated on every successful PATCH.
7. `ProfileService.update_profile()` is implemented and tested in `profile_service.test.py`.
8. Tiger Style: `update_profile()` asserts `profile_id` is a positive integer on input, and asserts the returned profile's `updated_at` is strictly greater than its `created_at` after update.

**Notes:**
- Partial update (PATCH semantics): only fields present in the request body are updated.

---

#### Story 1.4: Delete Profile

**As a** user,
**I want** to delete a profile,
**so that** I can remove profiles I no longer need.

**FRs:** FR4

**Acceptance Criteria:**

1. `DELETE /api/profiles/{profile_id}` deletes the profile and returns HTTP 204 (No Content).
2. `DELETE /api/profiles/{profile_id}` for a non-existent `profile_id` returns HTTP 404.
3. Deleting a profile cascades — all sections belonging to the profile are also deleted (verified by attempting to fetch sections after delete).
4. `ProfileService.delete_profile()` is implemented and tested.
5. Tiger Style: `delete_profile()` asserts `profile_id` is a positive integer on input, and asserts the profile no longer exists in the DB after the delete operation completes.

**Notes:**
- Cascade delete is enforced at the SQLAlchemy relationship level (`cascade="all, delete-orphan"`), not application logic.
- At this point in Epic 1, no sections tables exist yet — the cascade test can be a documented TODO verified in Epic 2 Story 2.1.

---

#### Story 1.5: Manage Profile Contacts

**As a** user,
**I want** to add, update, and remove contact information on a profile (email, phone, GitHub, LinkedIn, website, Twitter),
**so that** my CV can include my contact details through the standard profile structure.

**Acceptance Criteria:**

1. `POST /api/profiles/{profile_id}/contacts` with `{"type": "email", "value": "huy@example.com"}` creates a contact linked to the profile and returns the created contact with its `id`, `type`, `value`.
2. `GET /api/profiles/{profile_id}/contacts` returns all contacts for the profile.
3. `PATCH /api/profiles/{profile_id}/contacts/{contact_id}` with `{"value": "new@example.com"}` updates the contact value and returns the updated contact.
4. `DELETE /api/profiles/{profile_id}/contacts/{contact_id}` removes the contact and returns HTTP 204.
5. `POST` with an invalid `type` (not in `ContactType` enum) returns HTTP 422.
6. `POST` with a missing `value` returns HTTP 422.
7. Operations on a non-existent `profile_id` return HTTP 404.
8. The `ProfileContact` SQLAlchemy model is defined in `app/models/profile.py` (alongside `Profile`), with a foreign key to `profiles.id` and `cascade="all, delete-orphan"` on the relationship.
9. An Alembic migration version exists that creates the `profile_contacts` table (separate migration from `profiles`).
10. `ContactType` enum is used from `app/constants/enums.py`.
11. Contact CRUD is implemented in `ProfileService` (or a dedicated `ContactService` — developer's choice) and unit-tested.
12. Tiger Style: contact creation asserts `type` is a valid `ContactType` member on input, and asserts the returned contact's `profile_id` matches the request's `profile_id`.

**Notes:**
- Contacts are a sub-resource of profiles (`/api/profiles/{id}/contacts`), not a standalone resource.
- The `ContactType` enum was defined in Story 1.1's `enums.py` — import from there.
- Maximum contacts per profile: use a `MAX_CONTACTS_PER_PROFILE` constant from `constants/limits.py`.

---

### Epic 2: CV Section Authoring

#### Story 2.1: Experience Section CRUD

**As a** user,
**I want** to add, view, edit, delete, and toggle experience entries on a profile,
**so that** I can capture my work history in a structured, LaTeX-ready format.

**FRs:** FR6, FR8, FR9, FR10 (for experience section type)

**Acceptance Criteria:**

1. `POST /api/profiles/{profile_id}/sections/experience` creates an experience section record and returns it with `id`, `profile_id`, `title`, `organisation`, `start_date`, `end_date`, `is_enabled`, `display_order`.
2. `GET /api/profiles/{profile_id}/sections/experience` returns all experience sections for the profile (ordered by `display_order`).
3. `GET /api/profiles/{profile_id}/sections/experience/{section_id}` returns a single experience section including its bullet-point entries.
4. `PATCH /api/profiles/{profile_id}/sections/experience/{section_id}` updates any combination of `title`, `organisation`, `start_date`, `end_date`, `is_enabled`, `display_order`.
5. `DELETE /api/profiles/{profile_id}/sections/experience/{section_id}` removes the section and all its entries. Returns HTTP 204.
6. Entry sub-resource: `POST /api/profiles/{profile_id}/sections/experience/{section_id}/entries` adds a bullet point (`{"content": "..."}`) and returns the entry.
7. Entry sub-resource: `PATCH .../entries/{entry_id}` and `DELETE .../entries/{entry_id}` update and remove individual bullet points.
8. Toggle: `PATCH` with `{"is_enabled": false}` disables the section without deleting it. Toggling back with `{"is_enabled": true}` re-enables it.
9. New sections default to `is_enabled: true`.
10. `ExperienceSection` and `ExperienceEntry` SQLAlchemy models exist in `app/models/sections/experience.py`, with `Base` imported from `app/models/base.py`.
11. An Alembic migration creates `experience_sections` and `experience_entries` tables (one migration version for both).
12. `ExperienceSectionService` in `app/services/sections/experience_service.py` implements all CRUD operations.
13. The router `app/apis/sections/experience.py` is auto-registered via `app/apis/sections/__init__.py`.
14. Unit tests in `app/services/sections/experience_service.test.py`.
15. Tiger Style: all service methods assert `profile_id` > 0 on input. `create_experience_section()` asserts the returned section's `profile_id` matches input. Entry count per section must not exceed `MAX_ENTRIES_PER_SECTION` from `constants/limits.py`.
16. The cascade delete from Story 1.4 (deleting a profile deletes its sections) is now verifiable — add an integration test confirming this.

**Notes:**
- `experience_sections` columns: `id`, `profile_id` (FK), `title`, `organisation`, `start_date` (text), `end_date` (text, nullable for "present"), `is_enabled` (bool), `display_order` (int), `created_at`, `updated_at`.
- `experience_entries` columns: `id`, `section_id` (FK), `content`, `display_order`.

---

#### Story 2.2: Education Section CRUD

**As a** user,
**I want** to add, view, edit, delete, and toggle education entries on a profile,
**so that** I can capture my academic background in a structured format.

**FRs:** FR6, FR8, FR9, FR10 (for education section type)

**Acceptance Criteria:**

1. Full CRUD for education sections via `POST/GET/PATCH/DELETE /api/profiles/{profile_id}/sections/education` and `/{section_id}`.
2. Entry sub-resource for bullet points: `POST/PATCH/DELETE .../education/{section_id}/entries`.
3. `is_enabled` toggle works (PATCH with `{"is_enabled": false/true}`).
4. `EducationSection` and `EducationEntry` models in `app/models/sections/education.py`.
5. Alembic migration creates `education_sections` and `education_entries` tables.
6. `EducationSectionService` in `app/services/sections/education_service.py` with unit tests in `education_service.test.py`.
7. Router `app/apis/sections/education.py` auto-registered.
8. Tiger Style assertions mirroring Story 2.1 pattern.

**Notes:**
- `education_sections` columns mirror experience: `id`, `profile_id`, `title` (degree), `organisation` (institution), `start_date`, `end_date`, `is_enabled`, `display_order`, `created_at`, `updated_at`.
- `education_entries` columns: `id`, `section_id`, `content`, `display_order`.

---

#### Story 2.3: Projects Section CRUD

**As a** user,
**I want** to add, view, edit, delete, and toggle project entries on a profile,
**so that** I can showcase my personal and professional projects.

**FRs:** FR6, FR8, FR9, FR10 (for projects section type)

**Acceptance Criteria:**

1. Full CRUD via `POST/GET/PATCH/DELETE /api/profiles/{profile_id}/sections/projects` and `/{section_id}`.
2. Entry sub-resource for bullet points.
3. `is_enabled` toggle works.
4. `ProjectSection` and `ProjectEntry` models in `app/models/sections/projects.py`.
5. Alembic migration creates `project_sections` and `project_entries` tables.
6. `ProjectSectionService` in `app/services/sections/projects_service.py` with unit tests.
7. Router auto-registered.
8. Tiger Style assertions mirroring Story 2.1 pattern.

**Notes:**
- `project_sections` columns: `id`, `profile_id`, `title` (project name), `organisation` (optional, e.g. company or "Personal"), `start_date`, `end_date`, `is_enabled`, `display_order`, `created_at`, `updated_at`.

---

#### Story 2.4: Skills Section CRUD

**As a** user,
**I want** to add, view, edit, delete, and toggle skill groups on a profile,
**so that** I can list my technical and other skills grouped by category.

**FRs:** FR6, FR8, FR9, FR10 (for skills section type)

**Acceptance Criteria:**

1. Full CRUD via `POST/GET/PATCH/DELETE /api/profiles/{profile_id}/sections/skills` and `/{section_id}`.
2. Entry sub-resource for individual skill items (entries = skill items within a group).
3. `is_enabled` toggle works.
4. `SkillSection` and `SkillEntry` models in `app/models/sections/skills.py`.
5. Alembic migration creates `skill_sections` and `skill_entries` tables.
6. `SkillSectionService` in `app/services/sections/skills_service.py` with unit tests.
7. Router auto-registered.
8. Tiger Style assertions mirroring Story 2.1 pattern.

**Notes:**
- `skill_sections` columns: `id`, `profile_id`, `title` (category name, e.g. "Languages"), `is_enabled`, `display_order`, `created_at`, `updated_at`. No `organisation`, `start_date`, `end_date` — skills are not time-bounded.
- `skill_entries` columns: `id`, `section_id`, `content` (skill name), `display_order`.

---

#### Story 2.5: Certifications Section CRUD

**As a** user,
**I want** to add, view, edit, delete, and toggle certifications on a profile,
**so that** I can list professional certifications with issuer and date information.

**FRs:** FR6, FR8, FR9, FR10 (for certifications section type)

**Acceptance Criteria:**

1. Full CRUD via `POST/GET/PATCH/DELETE /api/profiles/{profile_id}/sections/certifications` and `/{section_id}`.
2. No entry sub-resource — certifications are single records (no bullet points).
3. `is_enabled` toggle works.
4. `CertificationSection` model in `app/models/sections/certifications.py`.
5. Alembic migration creates `certification_sections` table.
6. `CertificationSectionService` with unit tests.
7. Router auto-registered.
8. Tiger Style assertions.

**Notes:**
- `certification_sections` columns: `id`, `profile_id`, `title` (certification name), `organisation` (issuer), `start_date` (issue date), `end_date` (expiry, nullable), `is_enabled`, `display_order`, `created_at`, `updated_at`.
- No `*_entries` table for certifications — the section record itself is the atomic item.

---

#### Story 2.6: Languages Section CRUD

**As a** user,
**I want** to add, view, edit, delete, and toggle language proficiency entries on a profile,
**so that** I can list spoken languages and their proficiency levels.

**FRs:** FR6, FR8, FR9, FR10 (for languages section type)

**Acceptance Criteria:**

1. Full CRUD via `POST/GET/PATCH/DELETE /api/profiles/{profile_id}/sections/languages` and `/{section_id}`.
2. No entry sub-resource — language records are atomic.
3. `is_enabled` toggle works.
4. `LanguageSection` model in `app/models/sections/languages.py`.
5. Alembic migration creates `language_sections` table.
6. `LanguageSectionService` with unit tests.
7. Router auto-registered.
8. Tiger Style assertions.

**Notes:**
- `language_sections` columns: `id`, `profile_id`, `title` (language name, e.g. "Vietnamese"), `organisation` (proficiency level, e.g. "Native" — reusing `organisation` column per the unified schema), `is_enabled`, `display_order`, `created_at`, `updated_at`.
- No dates, no entries.

---

#### Story 2.7: Publications Section CRUD

**As a** user,
**I want** to add, view, edit, delete, and toggle publication records on a profile,
**so that** I can list academic papers, articles, or other published works.

**FRs:** FR6, FR8, FR9, FR10 (for publications section type)

**Acceptance Criteria:**

1. Full CRUD via `POST/GET/PATCH/DELETE /api/profiles/{profile_id}/sections/publications` and `/{section_id}`.
2. Entry sub-resource for co-authors or notes (bullet points below the publication record).
3. `is_enabled` toggle works.
4. `PublicationSection` and `PublicationEntry` models in `app/models/sections/publications.py`.
5. Alembic migration creates `publication_sections` and `publication_entries` tables.
6. `PublicationSectionService` with unit tests.
7. Router auto-registered.
8. Tiger Style assertions.

**Notes:**
- `publication_sections` columns: `id`, `profile_id`, `title` (paper/article title), `organisation` (venue/journal), `start_date` (publication date), `end_date` (nullable), `is_enabled`, `display_order`, `created_at`, `updated_at`.

---

#### Story 2.8: Free Text Section CRUD

**As a** user,
**I want** to add, view, edit, delete, and toggle free text sections on a profile,
**so that** I can include unstructured content (e.g. a personal summary, objective statement) that doesn't fit the structured schema.

**FRs:** FR7, FR8, FR9, FR10 (for free text section type)

**Acceptance Criteria:**

1. Full CRUD via `POST/GET/PATCH/DELETE /api/profiles/{profile_id}/sections/free_text` and `/{section_id}`.
2. No entry sub-resource — free text sections have a single `content` field.
3. `is_enabled` toggle works.
4. `FreeTextSection` model in `app/models/sections/free_text.py`.
5. Alembic migration creates `free_text_sections` table.
6. `FreeTextSectionService` with unit tests.
7. Router auto-registered via `app/apis/sections/__init__.py`.
8. Tiger Style assertions.

**Notes:**
- `free_text_sections` columns: `id`, `profile_id`, `title` (section heading), `content` (plain text body), `is_enabled`, `display_order`, `created_at`, `updated_at`.
- No `organisation`, no dates, no entries table.

---

#### Story 2.9: Clone Profile

**As a** user,
**I want** to clone an existing profile into a new independent profile,
**so that** I can create domain-specific CVs (e.g. "Software Engineering v2") based on an existing profile without starting from scratch.

**FRs:** FR5

**Acceptance Criteria:**

1. `POST /api/profiles/{profile_id}/clone` with `{"name": "New Profile Name"}` creates a new profile that is a deep copy of the source.
2. The cloned profile has a new `id`, the provided `name`, and a fresh `created_at` / `updated_at`.
3. All sections of all 8 types from the source profile are deep-copied into the new profile — each with a new `id` and the new `profile_id`.
4. All section entries (bullet points) are also deep-copied with new `ids`.
5. All profile contacts from the source are deep-copied with new `ids`.
6. After clone, modifying the cloned profile's data does not affect the source profile (verified by editing a section in the clone and checking the source is unchanged).
7. Cloning a non-existent `profile_id` returns HTTP 404.
8. `ProfileService.clone_profile()` is implemented as a service-level deep read + insert — NOT a DB-level COPY command.
9. Unit tests cover: successful clone verifies all section types are present in the clone; clone independence (modifying clone doesn't affect source).
10. Tiger Style: `clone_profile()` asserts `profile_id` > 0 on input and asserts the cloned profile's `id` differs from the source `profile_id` on output.

**Notes:**
- This story depends on all 8 section types existing (Stories 2.1–2.8).
- Clone is implemented entirely in `ProfileService` — no new service or adapter needed.
- Maximum sections per profile (across all types combined) is bounded by `MAX_SECTIONS_PER_PROFILE` from `constants/limits.py`.

---

### Epic 3: Template System

#### Story 3.1: Filesystem Template Discovery

**As a** user,
**I want** the system to automatically discover `.tex` files from the `assets/templates/` directory at startup,
**so that** I can add new templates by simply dropping files into the directory without any configuration changes.

**FRs:** FR11, FR14

**Acceptance Criteria:**

1. On application startup, the system scans `assets/templates/` for all `.tex` files.
2. Discovered template names (filenames without extension) are available via `GET /api/templates` which returns `[{"name": "...", "status": "discovered"}, ...]`.
3. Templates in subdirectories are not discovered — only root-level `.tex` files in `assets/templates/`.
4. If `assets/templates/` is empty or does not exist, `GET /api/templates` returns `[]` with no error.
5. `FilesystemTemplateDiscovery` adapter in `app/adapters/filesystem_template_discovery.py` implements `TemplateDiscoveryProtocol`.
6. `TemplateService` in `app/services/template_service.py` uses `TemplateDiscoveryProtocol` via `Depends()`.
7. Unit tests in `app/services/template_service.test.py` for discovery with a test-double adapter.
8. Tiger Style: discovery loop uses `MAX_TEMPLATES` from `constants/limits.py` and asserts the result is a list (not None) before returning.

**Notes:**
- Discovery happens at startup (or on-demand when `GET /api/templates` is called — developer's choice, but results must be fresh if templates dir changes between requests in v1).

---

#### Story 3.2: Template Validation

**As a** user,
**I want** the system to verify that each discovered template can actually be compiled before making it selectable,
**so that** I never try to build a CV with a broken template.

**FRs:** FR12, FR14

**Acceptance Criteria:**

1. For each discovered `.tex` file, the system attempts a test compilation (via `LatexCompilerProtocol`) using a minimal dummy data payload.
2. Templates that compile successfully are marked `"status": "valid"` in `GET /api/templates`.
3. Templates that fail compilation are marked `"status": "invalid"` with an `"error"` field containing a brief reason.
4. Invalid templates do not appear as selectable options in the template dropdown (filtered out by `GET /api/templates?valid_only=true`).
5. Template validation runs at startup and the results are cached in memory — no re-validation per request.
6. Startup logs report which templates are valid and which are invalid with brief reasons.
7. `PdflatexCompilerAdapter` in `app/adapters/pdflatex_compiler.py` implements `LatexCompilerProtocol`.
8. Unit tests mock the compiler to test valid/invalid branching logic in `TemplateService`.
9. Tiger Style: the validation loop is bounded by `MAX_TEMPLATES`. The cached results list asserts `len(results) == len(discovered_templates)` — every discovered template has a validation result.

---

#### Story 3.3: Template Selection

**As a** user,
**I want** to select an active template from the list of validated templates,
**so that** subsequent Preview and Build operations use my chosen template.

**FRs:** FR13, FR27

**Acceptance Criteria:**

1. `PUT /api/templates/active` with `{"name": "template_name"}` sets the active template.
2. Setting an invalid or unknown template name returns HTTP 400 with a clear error message.
3. `GET /api/templates/active` returns the currently active template name, or `null` if none selected.
4. The active template is stored in memory (not persisted to DB) — restarting the app clears the selection.
5. The workspace UI template dropdown lists only valid templates and reflects the active selection.
6. Selecting a template in the dropdown triggers an HTMX update of the right panel (preview pane) — consistent with FR27, no context loss in the left panel.
7. `TemplateService.set_active_template()` and `get_active_template()` are implemented and tested.
8. Tiger Style: `set_active_template()` asserts the template name is non-empty and exists in the validated templates list before setting.

---

#### Story 3.4: Create Starter LaTeX Template (Huy-driven)

**As** Huy,
**I want** to create the first LaTeX template for CVMaker with guidance on what variables and structure the system expects,
**so that** the template system has a real, working template to validate against and I understand how to author templates going forward.

**FRs:** FR11, FR12 (prerequisite validation)

**Acceptance Criteria:**

1. At least one `.tex` file exists in `assets/templates/` (e.g. `simple.tex`).
2. The template compiles successfully against a sample data payload (verified by running Story 3.2's validation).
3. The template uses Jinja2-style variable substitution (or the chosen template rendering approach) for all profile fields: profile name, contact items, and at least one section type.
4. The template renders a readable single-column CV layout — does not need to be beautiful, but must be legible.
5. Template authoring conventions are documented in a comment block at the top of the `.tex` file (what variables are available, how sections are conditionally included).
6. Story 3.2's validation passes: `GET /api/templates?valid_only=true` includes this template as `"status": "valid"`.

**Notes:**
- This story is **Huy-driven** — the developer/user creates the template file directly in their editor. The assistant's role is to provide the variable contract and a minimal working starter, not to generate the final template autonomously.
- Timing: this story must complete before Epic 4 begins, as compilation stories require at least one valid template.

---

### Epic 4: CV Compilation Workspace

#### Story 4.1: Split-View Workspace Shell

**As a** user,
**I want** a split-view workspace page with a profile editor panel on the left and a PDF preview panel on the right,
**so that** I can edit my CV content and see the preview at the same time.

**FRs:** FR26

**Acceptance Criteria:**

1. `GET /workspace` renders the split-view workspace HTML page.
2. The left panel contains a profile selector dropdown (populated via `GET /api/profiles`).
3. The right panel is initially empty (placeholder: "Select a profile and hit Preview").
4. The template selector dropdown is visible in the workspace (populated via `GET /api/templates?valid_only=true`).
5. A "Preview" button and a "Build" button are present.
6. Selecting a profile in the dropdown updates the left panel to show that profile's sections via HTMX partial swap — the right panel is not affected.
7. Page layout is desktop-first, two-column split. No mobile breakpoints.
8. `WorkspaceController` in `app/controllers/workspace_controller.py` handles the `/workspace` route and HX-Request header detection.
9. Jinja2 templates for the workspace live in `app/views/workspace/`.

---

#### Story 4.2: LaTeX Input Sanitization

**As a** system,
**I want** all user-provided text to be sanitized before being passed to any LaTeX template,
**so that** no user input can inject malicious LaTeX commands or break compilation.

**FRs:** FR25; **NFRs:** NFR-S1, NFR-S2

**Acceptance Criteria:**

1. `app/utils/sanitizer.py` implements `sanitize_for_latex(text: str) -> str`.
2. The sanitizer escapes all LaTeX special characters: `& % $ # _ { } ~ ^ \`.
3. The sanitizer blocks `\write18` and `\immediate\write18` — raises a `ValueError` (not silently strips) if detected.
4. The sanitizer is called in the `PdflatexCompilerAdapter` before injecting any user data into the template — this is the hard invariant location.
5. No other location in the codebase calls pdflatex with unsanitized data.
6. Unit tests in `sanitizer.test.py` (co-located in `app/utils/`) cover: normal text passthrough, each special character escaped correctly, shell execution blocked with `ValueError`, empty string in → empty string out.
7. Tiger Style: `sanitize_for_latex()` asserts input is a `str` (not None) on entry, and asserts output contains no unescaped `&` characters on exit.

---

#### Story 4.3: PDF Preview (Ephemeral)

**As a** user,
**I want** to trigger a PDF preview of my current profile + template combination and see it rendered inline in the workspace,
**so that** I can check how my CV looks without saving a file.

**FRs:** FR15, FR16, FR17, FR18

**Acceptance Criteria:**

1. Clicking "Preview" in the workspace sends a POST to `POST /api/compilation/preview` with `{"profile_id": ..., "template_name": "..."}`.
2. The response streams back the compiled PDF bytes inline — no file is saved to disk.
3. The right panel renders the PDF inline using a `<embed>` or `<iframe>` pointing to a `/compilation/preview-data` data endpoint, or via a blob URL.
4. A compilation progress indicator ("Compiling…") is shown in the right panel while compilation is in progress (HTMX polling or SSE).
5. Compilation is async — the UI does not freeze during compile (NFR-P4).
6. On success, the progress indicator is replaced by the inline PDF view.
7. Preview compilation completes within 5 seconds for a typical CV (NFR-P1) — logged if exceeded.
8. `CompilationService.preview()` in `app/services/compilation_service.py` uses `LatexCompilerProtocol` and `StorageProtocol` (ephemeral temp storage, auto-cleaned).
9. `CompilationController` handles HX-Request detection and returns HTMX partial for the right panel.
10. Tiger Style: `preview()` asserts `profile_id` > 0 and `template_name` is non-empty on input. Asserts returned bytes length > 0 on success.

---

#### Story 4.4: PDF Build (Persistent + Download)

**As a** user,
**I want** to trigger a finalized PDF build that saves the file and lets me download it,
**so that** I have a permanent copy of my CV ready to submit.

**FRs:** FR19, FR20, FR21, FR22

**Acceptance Criteria:**

1. Clicking "Build" sends `POST /api/compilation/build` with `{"profile_id": ..., "template_name": "..."}`.
2. The compiled PDF is saved to the configured output location (`OUTPUT_PATH` from settings).
3. On success, the response triggers a file download in the browser.
4. Build compilation completes within 10 seconds for a typical CV (NFR-P2) — logged if exceeded.
5. `GET /api/settings/output-path` returns the current configured output path.
6. `PUT /api/settings/output-path` with `{"path": "..."}` updates the output path (persisted to `.env` or config — developer's choice; in-memory is acceptable for v1).
7. A compilation failure during build does not produce a partial file at the output path (NFR-R2) — verified by checking output path is empty/unchanged after a forced failure.
8. `CompilationService.build()` implements the persistent build path.
9. Tiger Style: `build()` asserts the output file exists and has size > 0 after a successful write. Asserts the output path does not contain the partial file if compilation fails.

---

#### Story 4.5: Compilation Error Reporting

**As a** user,
**I want** to see a clear error message when compilation fails, and be able to expand the full LaTeX log,
**so that** I can diagnose and fix template or data issues without the app crashing.

**FRs:** FR23, FR24; **NFRs:** NFR-R1

**Acceptance Criteria:**

1. When preview or build compilation fails, the right panel shows an error summary (not a crash page).
2. The error summary includes the LaTeX exit code and first relevant error line extracted from the log.
3. An "Expand log" toggle reveals the full raw LaTeX log output in a scrollable panel.
4. The workspace remains fully interactive after a compilation failure — the left panel is unaffected (NFR-R1).
5. The profile selector, template selector, and all form inputs retain their state after a failure.
6. `CompilationService` captures and returns the full stderr/stdout log from pdflatex on failure.
7. `CompilationController` returns an HTMX partial that renders the error UI in the right panel.
8. Tiger Style: the error handler asserts the log string is non-empty when a compilation failure is reported (a failure with no log is itself a bug — fail explicitly).

**Notes:**
- The application must never show an unhandled 500 error to the user for a compilation failure — all LaTeX errors are caught at the adapter level and surfaced as structured `CompilationError` objects.

---

That completes all 4 epics. Updating epics.md frontmatter to reflect stories complete.
