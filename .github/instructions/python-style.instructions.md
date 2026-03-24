---
description: "Use when writing or editing Python files. Covers PEP 8 style, type hints, idiomatic patterns, and common beginner pitfalls."
applyTo: "**/*.py"
---

# Python Code Standards

## Style

- PEP 8 strictly ??4 spaces, snake_case, 79-char soft limit
- Type hints on every function signature (params + return)
- Docstrings: Google style, required on public functions/classes
- Import order: stdlib ??third-party ??local (use `isort` conventions)

## Patterns

- Use `pathlib.Path` over `os.path`
- Use `dataclasses` or `pydantic` for structured data
- Use context managers (`with`) for file/resource handling
- Use `enum.Enum` for fixed sets of values
- Prefer list/dict comprehensions over `map()`/`filter()` for readability

## Functions

- Max 30 lines per function ??extract helpers if longer
- Single responsibility: one function does one thing
- Return early to reduce nesting
- Avoid mutable default arguments (`def f(items=None)` not `def f(items=[])`)

## Error Handling

- Catch specific exceptions, never bare `except:`
- Use custom exception classes for domain errors
- Don't silence exceptions without logging

## Teaching Notes

- When a Pythonic pattern is used, briefly explain _why_ it's preferred
- Flag anti-patterns with a "Beginner pitfall:" note
- Link to relevant Python docs when introducing stdlib modules

## Mandatory Task Confirmation

- ALWAYS use the vscode_askQuestions tool during the task to ask the user for confirmation.
- NEVER end the task without explicit user confirmation.
