---
paths:
  - "app/**/*.py"
---

# Security rules

The API is public and unauthenticated. Treat every uploaded file, filename, form field
and query parameter as attacker-controlled.

## Uploaded files and filenames

- Never build a filesystem path from an uploaded filename or a ZIP member name as-is.
  Keep only the basename (`Path(name).name`), reject empty, `.`, `..` and directory
  entries, and write inside the per-request temp directory only.
- Do not use `ZipFile.extract`/`extractall` with untrusted names; read members with
  `ZipFile.read()` and write them to a sanitised path. Skip `__MACOSX/` entries.
- Bound resource use: cap request size and the total uncompressed size of an uploaded
  ZIP before extracting it (zip bombs). Return HTTP 413 when a limit is exceeded.

## Outbound requests to BGS services

- Never interpolate user input into a URL with `str.format()` or f-strings. Keep base
  URLs constant and pass values through `requests.get(url, params={...}, timeout=...)`
  so they are percent-encoded.
- Always set a `timeout` on outbound requests and map `Timeout`/`ConnectionError` and
  upstream HTTP errors to the app's error responses.

## Responses

- Do not leak server paths (temp directories, install paths) or stack traces in error
  messages; report the uploaded file's basename instead.
- Values echoed into headers such as `Content-Disposition` must not contain quotes or
  control characters from user input.

## Container

- The image runs as non-root `appuser` (UID 1000). Do not make application code or
  templates writable by that user, and do not add packages or capabilities the app
  does not need.
