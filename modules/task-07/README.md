# Task 7 — Code Review & Teaching Assistant

Standalone MVP for static code review and a teaching-assistant entry point.

## Scope

- Search teaching text and code first. Support Markdown and Jupyter notebooks; keep chunking strategies distinct for notes, code, and exercises.
- Provide static correctness/style suggestions and submission diff summaries. Student submissions are stored as assignment files and are never executed.
- Allow the assistant to call only registered, pre-packaged teaching algorithms. Jobs run in isolated processes and may be queued. Arbitrary Python execution is out of scope.
- Image understanding, diagram annotation, and training-curve interpretation are later phases.

## Stack

Python 3.12 / Flask / JWT; Vue 3 / TypeScript; PostgreSQL 16 with pgvector; Redis 7; Docker Compose.

## Safety

Never pass submitted code to `exec`, a shell, or an algorithm worker. Validate allow-listed algorithm tool names and inputs, enforce timeouts, and bound returned output. Keep credentials server-side.
