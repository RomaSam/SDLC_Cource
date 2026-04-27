---
name: git-commit
description: Generate a conventional commit message based on staged changes
allowed-tools: Bash(git *)
---

Run `git diff --cached` to see all staged changes. Then run `git log --oneline -5` to understand the commit style used in this repo.

Based on the staged diff, generate a commit message following the Conventional Commits format:

```
<type>(<scope>): <short summary>

<optional body>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `style`

Rules:
- Subject line: max 72 characters, imperative mood ("add" not "added")
- Scope: the module or area affected (optional but helpful)
- Body: only if the why is non-obvious; wrap at 72 chars
- No period at end of subject line

After showing the message, ask the user if they want to run `git commit -m "..."` with it.
