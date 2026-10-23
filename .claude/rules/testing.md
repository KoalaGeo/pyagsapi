---
paths:
  - "test/**/*.py"
---

# Testing rules

- Unit tests go in `test/unit/`, API tests in `test/integration/`. Shared constants
  (`API_VERSION`, `TEST_FILE_DIR`, `FROZEN_TIME`, expected ZIP contents) live in
  `test/fixtures.py`; expected JSON and plain-text responses live in
  `test/fixtures_json.py` and `test/fixtures_plain_text.py`.
- Use the `client` (sync `TestClient`) or `async_client` (`httpx.AsyncClient` with
  `ASGITransport`) fixtures from `test/conftest.py`. Mark async tests with
  `@pytest.mark.asyncio`.
- Build multipart uploads with `requests_toolbelt.MultipartEncoder`, as the existing
  validate/convert tests do.
- Responses include a timestamp; wrap tests that compare full responses in
  `freeze_time(FROZEN_TIME)`.
- Tests that call live BGS services (`gwbv.bgs.ac.uk`, `ogcapi.bgs.ac.uk`) must be
  marked `@pytest.mark.xfail(IN_GITHUB_ACTIONS, reason=...)`. For error paths, prefer
  `monkeypatch` on the route module's URL constant or `requests.get` so the test runs
  offline.
- When monkeypatching a module-level constant, patch the module that reads it at call
  time (e.g. `app.routes.utils`), not a module that imported the value by name.
- Add a regression test with every bug fix, and add any new sample file to
  `test/files/` rather than generating large data inline.
- `pytest` is pinned to 8.0.2 in `requirements_dev.in` because 8.1.0 breaks the suite;
  don't upgrade it without fixing that first.
