# Style and Conventions

## Code Style
- Python 3.14, strict mypy, ruff (line-length 100)
- Type hints everywhere (strict mypy)
- No docstrings convention specified — infer from existing code
- Naming: follow PEP8 (ruff N rule enforced)

## Tiger Style (Key Invariants)
- Assertions enforce programmer invariants; exceptions handle expected failures
- Every function: min one input precondition assertion + one output postcondition assertion
- Assertions remain enabled in production (crash on bad state > silent corruption)
- All loop bounds reference named constant from `constants/limits.py` — never inline magic numbers

## Enforcement Rules
- Never read `os.environ` directly — always import from `configs/`
- Never put business logic in `apis/` or `views/`
- Never put HTTP/response logic in `services/`
- Never call LaTeX adapter without sanitizing input first
- Never create `BaseService` or `BaseAdapter` — standalone classes only
- Never swallow exceptions — log and re-raise or convert to structured error
- `HX-Request` check lives only in `controllers/`

## Interface Pattern
- Use `typing.Protocol` (not ABC) for interfaces in `app/interfaces/`
