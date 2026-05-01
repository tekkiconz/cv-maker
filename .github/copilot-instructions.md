> All project guidance lives in [AGENTS.md](../AGENTS.md). That file is the single source of truth shared across AI tools.

## Code Intelligence

Always use Serena tools (`find_symbol`, `get_symbols_overview`, `find_referencing_symbols`, `search_for_pattern`, etc.) when navigating or understanding the codebase. Prefer Serena over grep/glob/bash for any code search or symbol lookup. Call `check_onboarding_performed` at the start of each session.
