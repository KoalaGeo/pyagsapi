---
paths:
  - "app/routes/**/*.py"
  - "app/main.py"
---

# API route rules

## Async and blocking work

- A route declared `async def` must not run blocking work on the event loop. Wrap
  CPU- or IO-heavy calls (`python-ags4` parsing, pandas/geopandas/shapely work,
  `shutil.make_archive`, large file writes) in
  `await fastapi.concurrency.run_in_threadpool(...)`.
- Routes that only make blocking calls (e.g. `requests.get`) and never `await` should
  be plain `def`, so Starlette runs them in its threadpool.
- One worker serves many requests on Kubernetes; a blocked loop stalls every request on
  that pod and can fail its probes.

## Temporary files

- Create per-request working directories with `tempfile.mkdtemp()` and always clean
  them up. Background tasks only run when a response is returned, so also remove the
  directory in an `except` block before re-raising.
- Keep files a streamed response still needs (e.g. the results ZIP) until a background
  task closes and deletes them after the response is sent.

## Paths and proxies

- The app may be served under a proxy sub-path (`PYAGSAPI_ROOT_PATH`). Never hard-code
  absolute URLs such as `/openapi.json` or `/v7/...` in responses or templates; prefix
  them with `request.scope.get("root_path", "")`.

## Adding or changing an endpoint

- Mount it under `AGS_API_VERSION`, add a `tags`, `summary`, `description` and a
  `responses=` entry built from `error_responses` in `app/routes/utils.py`.
- Define reusable form/query parameters in `app/model/queries.py` and response models
  in `app/model/schema.py`.
- Register the router in `app/main.py` and add the endpoint to
  `test/integration/test_openapi.py` and `docs/routes.md`.
