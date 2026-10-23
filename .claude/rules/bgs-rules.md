---
paths:
  - "app/bgs_rules.py"
  - "app/bgs_group_id_keys.py"
  - "app/checkers.py"
  - "app/validation.py"
  - "app/model/schema.py"
---

# Validation rule conventions

## BGS data-validation rules (`app/bgs_rules.py`)

- Each rule is a function `def check_x(tables: dict) -> List[dict]` that takes the dict
  of group name -> DataFrame and returns a list of errors (empty list when it passes).
- Each error is `{"line": ..., "group": ..., "desc": ...}`. `line` is an int line number,
  or `"-"` when the error is not tied to one line (the schema rejects other strings).
- Register the rule in the `BGS_RULES` dict; its key is the rule's display name and is
  added to `VALID_KEYS` automatically. Any other new error key (e.g. a new AGS rule or
  read-error category) must be added to `VALID_KEYS` in `app/model/schema.py`, or
  responses fail validation with "Unknown rule".
- A rule must not raise on missing groups or columns: catch `KeyError` and return `[]`,
  since earlier rules already report missing required groups. An exception in one rule
  turns the whole request into a 500.
- Do not accumulate errors by reassigning a list inside a loop; extend or append to it.
- Load static reference data (boundary GeoJSON in `app/*.geojson`) once at module level
  or with `functools.lru_cache`, not on every call.
- Avoid row-wise `DataFrame.apply` with membership tests against arrays; convert lookup
  values to a `set` first.
- Bump `bgs_rules_version` when rule behaviour changes, and document the rule in
  `docs/bgs_rules.md`.

## Tests

- Add unit tests to `test/unit/test_bgs_rules.py` covering a passing case, a failing
  case and missing groups/columns. Put sample AGS files in `test/files/bgs_rules/`.
