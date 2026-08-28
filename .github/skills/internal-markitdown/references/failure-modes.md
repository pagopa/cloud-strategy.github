# Failure Modes

Observed environmental failures and their recovery paths. Flags do not fix
these; changing the environment or waiting does.

## Empty transcript body

- Symptom: `xml.etree.ElementTree.ParseError: no element found: line 1, column 0`
  during transcript fetch, with per-attempt retry failures printed.
- Cause: the YouTube timedtext endpoint returned an empty body, typically bot
  detection or throttling. The video page and caption listing still work.
- Recovery: retry later; a CLI attempt may succeed where an API attempt failed
  in the same minute. Do not loop retries beyond the built-in three.

## Rate limiting

- Symptom: HTTP 429 with a Google `Sorry... automated queries` HTML body from
  the timedtext endpoint.
- Recovery: back off and retry in a later session. Adding query parameters or
  headers does not bypass it.

## Unsupported format

- Symptom: `UnsupportedFormatException: Could not convert stream to Markdown.
  No converter attempted a conversion`.
- Cause: no converter accepted the stream. Check the `-x` extension and `-m`
  mimetype hints first. Caption dump formats such as raw VTT or SRV3 XML are
  outputs, not supported inputs.

## Transcript missing while metadata renders

- Symptom: YouTube output contains title, description, and chapters but no
  `### Transcript` section, or fetch fails with a missing-module error.
- Cause: the serving install lacks `youtube-transcript-api`.
- Recovery: `pipx inject markitdown youtube-transcript-api` for the CLI venv, or
  `python3 -m pip install 'markitdown[youtube-transcription]'` for the Python
  API environment.

## Privilege and input safety

Markitdown performs I/O with the privileges of the current process, including
network fetches for URI inputs. Sanitize untrusted paths and URIs before
conversion in shared or hosted contexts; prefer local files over remote URIs
when the source is untrusted.
