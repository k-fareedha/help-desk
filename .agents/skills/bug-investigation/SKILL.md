---
name: bug-investigation
description: Investigate and fix reproducible bugs in the Texol AI Support Hub with focused evidence, a small correction, and regression validation.
---

# Bug investigation workflow

Use this skill when the user reports a failure, regression, or unexpected behavior.

1. Read `AGENTS.md` and the relevant architecture notes; inspect the affected code and tests.
2. Reproduce the failure when safe. Capture the exact error, command or user steps, and observed result without exposing secrets.
3. Trace the owning code path and identify the root cause from evidence. If uncertain, distinguish likely causes from confirmed facts.
4. Make the smallest appropriate fix after the cause is clear. Ask before destructive data or schema operations.
5. Add a regression test and run the relevant documented checks. Report failed and unrun checks honestly.
6. Record a verified incident and resolution in `docs/CHALLENGES.md` when the issue is material.
