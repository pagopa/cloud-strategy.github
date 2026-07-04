# Maintenance Guidance

- Prefer `fixtures/` samples over repeated inline Markdown payloads.
- When the target is tracked source, exclude generated caches such as `graphify-out/`, `.pytest_cache/`, `.venv/`, and `__pycache__/` from broad searches.
- If maintenance work reaches `main.jsonl`, confirm the analyzer contract accepts that file type before running it.
