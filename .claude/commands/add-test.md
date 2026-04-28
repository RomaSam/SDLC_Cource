---
description: Create a test skeleton for a given function or file
allowed-tools: Read, Glob, Grep
argument-hint: <file-path or function name>
---

Target: $ARGUMENTS

1. If a file path was given, read it. If a function name was given, search for it with Grep.
2. Identify the testing framework already used in the project (Jest, Vitest, pytest, etc.) by looking for config files or existing test files.
3. Generate a test skeleton that includes:
   - Correct import/require for the target
   - A `describe` block named after the module or class
   - One `it`/`test` block per public function or method
   - Arrange-Act-Assert comments inside each block
   - A placeholder for the happy path and one for an error/edge case

Output the skeleton as a ready-to-save file. Suggest the file path following the project's existing test naming convention (e.g. `foo.test.ts` next to `foo.ts`, or inside a `__tests__` folder).

Do not fill in assertions — leave `expect(...)` calls as `// TODO` so the developer completes the logic.
