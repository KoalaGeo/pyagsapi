---
paths:
  - "requirements*.in"
  - "requirements*.txt"
  - "Dockerfile"
  - ".github/workflows/*.yml"
---

# Dependency and build rules

- Edit `requirements.in` / `requirements_dev.in`, then regenerate the pinned
  `requirements.txt` / `requirements_dev.txt` with `pip-compile` (or
  `uv pip compile --python-version 3.11`). Never hand-edit the `.txt` lockfiles.
- Resolve pins for Python 3.11 (CI) so they also install on the Python 3.13 Docker image.
- `python-ags4` is pinned deliberately: validation output and the tests' expected
  responses depend on its exact version. Update it in its own change, together with
  the test fixtures.
- Run `pip-audit -r requirements.txt` after changing dependencies and don't
  introduce packages with known vulnerabilities.
- Never commit an internal package mirror: CI fails if any `requirements*.txt`
  contains an `index-url` pointing at Nexus.
- Keep the Dockerfile running as the non-root `appuser` and the base image pinned to an
  exact Python patch version.
