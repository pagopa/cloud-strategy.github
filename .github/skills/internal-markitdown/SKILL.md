---
name: internal-markitdown
description: Use when converting any file, URL, or YouTube video to Markdown with markitdown, when a YouTube transcript is requested, or when markitdown extras or plugins are mentioned.
---

# Internal Markitdown

## When to use

- Any request to convert a document, page, or media source to Markdown with markitdown.
- YouTube transcript extraction through markitdown.
- Choosing between the markitdown CLI, the Python API, and plugins.

## When not to use

- Markdown structure, fence, or link review: that is `internal-markdown`.
- Workbook or tabular data integrity: that is `internal-excel`.
- Summarizing or rewriting a transcript after conversion; the contract ends at Markdown output.

## Environment map

Two installs coexist; name the install target before debugging.

- CLI: `markitdown` from pipx (`~/.local/bin/markitdown`, isolated venv). Install
  missing extras into that venv with `pipx inject markitdown <package>`. Inject
  the dependency package directly (for example `youtube-transcript-api`), not an
  extra-spec string.
- Python API: `from markitdown import MarkItDown` resolves against the global
  `python3` environment; install its extras there with
  `python3 -m pip install 'markitdown[<extra>]'`.
- A missing extra in one install is not a missing feature; verify the serving
  install first.

## Direct playbook

- File: `markitdown FILE -o OUT.md`.
- URL: `markitdown 'URL' -o OUT.md`. For YouTube use the canonical form
  `https://www.youtube.com/watch?v=<ID>`; transcript output requires the
  `youtube-transcription` extra in the serving install. Transcripts are
  auto-generated captions joined as plain text, without timestamps.
- Stream without a usable filename: pipe stdin and pass `-x <extension>`; add
  `-m <mimetype>` or `-c <charset>` when the hint changes detection.
- Plugins: `--list-plugins` to enumerate, `-p` to enable.
- Always save with `-o`; do not rely on truncated console output as evidence.

## Boundary

- Use the smallest command that yields the artifact; do not re-read the source.
- Prefer the CLI for one-shot conversions and file outputs; prefer the Python
  API when the result feeds code: `from markitdown import MarkItDown;
  MarkItDown().convert(source, **kwargs).text_content`, where source is a path,
  URI, or stream and kwargs include `youtube_transcript_languages`.
- On a conversion error, read `references/failure-modes.md` before retrying;
  most observed failures are environmental and flags will not fix them.

## Validation

- Confirm the output file exists and contains the expected section anchors
  (for YouTube: `### Transcript`).
