# pyagsapi

FastAPI service that validates AGS4 geotechnical data files (AGS format rules via
`python-ags4`, plus BGS data rules), converts `.ags` <-> `.xlsx`, and proxies borehole
log / export requests to BGS NGDC services. Serves an HTML UI at `/` and API docs at
`/docs` and `/redoc`.

Topic-specific rules live in `.claude/rules/`; path-scoped ones load only when you
touch matching files.

## Commands

- Install: `pip install -r requirements.txt -r requirements_dev.txt`
- Lint: `flake8 app/ test/` (max line length 120, see `.flake8`)
- Test: `python -m pytest`
- Run locally: `fastapi dev app/main.py` (container uses `fastapi run app/main.py --port 8000`)
- Docs site: `pip install mkdocs-material 'mkdocstrings[python]'` then `mkdocs serve`
  (sources in `docs/`; not in the requirements files, matching `.github/workflows/pages.yml`)

Run lint and the tests before committing. CI (`.github/workflows/lint_and_test.yml`)
runs the same two commands on Python 3.11; the Docker image runs Python 3.13, so do
not use syntax or stdlib features newer than 3.11.

## Layout

- `app/main.py` - app setup, logging, middleware, exception handlers, `/`, `/docs`, `/redoc`
- `app/routes/` - one module per endpoint group; shared constants and helpers in `app/routes/utils.py`
- `app/validation.py`, `app/checkers.py` - run checkers and assemble the validation response
- `app/bgs_rules.py` - BGS data-validation rule functions, registered in `BGS_RULES`
- `app/conversion.py` - `.ags` <-> `.xlsx` conversion
- `app/borehole_map.py` - GeoJSON extraction from the LOCA group
- `app/model/schema.py`, `app/model/queries.py` - Pydantic response models and FastAPI form/query params
- `app/templates/`, `app/static/` - HTML UI (Jinja2 templates, jQuery + Leaflet JS)
- `test/unit/`, `test/integration/` - pytest suites; sample files in `test/files/`

## Conventions

- The API is versioned by path: routes are mounted under `AGS_API_VERSION` (`/v7`),
  derived from `API_VERSION` in `app/version.py`, the single source of truth for the version.
- Error responses use the `ErrorResponse` shape (`msg`, `type`, `self`, `errors[]`); raise
  `HTTPException` with a `detail` dict (`msg`, `error`, `desc`) or `InvalidPayloadError`
  rather than returning ad-hoc JSON.
- Configuration comes from environment variables: `PYAGSAPI_ROOT_PATH` (proxy sub-path)
  and `AGS_API_ENV` (`PRODUCTION` forces `https` in self links).
- Keep `README.md` and `docs/` in step with user-facing changes (endpoints, parameters,
  environment variables, deployment).
