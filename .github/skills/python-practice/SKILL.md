---
name: python-practice
description: "Generate Python practice exercises related to the password manager project. Use when the user wants coding challenges, homework, drills, or exercises to practice Python or cryptography concepts."
argument-hint: "Topic or concept to practice, e.g. 'dataclasses', 'file I/O', 'encryption'"
---

# Python Practice Exercises

## When to Use

- User asks for exercises, challenges, or practice problems
- User wants to reinforce a concept they just learned
- User finishes a feature and wants to deepen understanding
- User says "I don't get it" ??an exercise often helps more than re-explaining

## Exercise Difficulty Levels

- **Starter**: Single function, one concept, <20 lines
- **Builder**: Multiple functions/classes, combines concepts, <50 lines
- **Challenge**: Full module, real-world constraints, requires design decisions

## Procedure

1. Identify the concept or topic to practice
2. Choose an appropriate difficulty level
3. Generate an exercise following the format below
4. Provide hints (collapsed) and a solution (collapsed)

## Exercise Format

````markdown
### Exercise: [Title]

**Level**: Starter | Builder | Challenge
**Concepts**: [list of Python/crypto concepts covered]
**Estimated time**: X minutes

**Background**: [Brief context connecting to the password manager]

**Task**: [Clear description of what to build]

**Requirements**:

1. [Specific requirement]
2. [Specific requirement]
3. [Specific requirement]

**Starter code**:
\```python

# starter code here

\```

<details>
<summary>Hint 1</summary>
[First hint ??nudge in the right direction]
</details>

<details>
<summary>Hint 2</summary>
[Second hint ??more specific guidance]
</details>

<details>
<summary>Solution</summary>
\```python
# full solution with comments explaining each choice
\```
</details>
````

## Exercise Bank by Topic

### Python Fundamentals

- Build an `Entry` dataclass with validation
- Write a password strength checker using `re`
- Create a CLI menu using `match/case` (Python 3.10+)

### File I/O & Storage

- Read/write encrypted data to a file using `pathlib`
- Build a simple JSON vault (before adding crypto)
- Implement SQLite CRUD for password entries

### Cryptography

- Derive a key from a password using PBKDF2
- Encrypt and decrypt a string with Fernet
- Implement AES-GCM encryption with proper nonce handling
- Generate secure random passwords with `secrets`
- Build a constant-time comparison function

### OOP & Architecture

- Create a `Vault` class with open/close/lock semantics
- Implement the Repository pattern for entry storage
- Build an `EntryGenerator` with configurable character sets

### Testing

- Write pytest tests for the password generator
- Test encryption round-trips (encrypt ??decrypt = original)
- Test that wrong passwords raise appropriate errors

## Mandatory Task Confirmation

- ALWAYS use the vscode_askQuestions tool during the task to ask the user for confirmation.
- NEVER end the task without explicit user confirmation.
