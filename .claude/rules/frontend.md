---
paths:
  - "app/templates/**/*"
  - "app/static/js/*.js"
---

# Frontend rules (HTML UI)

- Validation results contain text taken from uploaded files (filenames, PROJ/LOCA
  values, error descriptions). Never insert it into the page with `.html()`,
  `.append()` of an HTML string, `innerHTML`, or Leaflet `bindPopup`/`bindTooltip`
  strings without escaping it first. Prefer `.text()` or building elements with
  `document.createElement` and `textContent`.
- Templates are Jinja2 with autoescaping; do not use the `|safe` filter on data that
  can come from a request or an uploaded file.
- Build API URLs from the `api_version_path` global set in `_base.html` rather than
  hard-coding `/v7/...`, so the UI keeps working under a proxy sub-path.
- Third-party scripts from a CDN must be pinned to an exact version with an
  `integrity` (SRI) hash and `crossorigin`, like the existing `leaflet.draw` tags.
- Do not edit vendored libraries in `app/static/js/leaflet/` or
  `jquery-3.7.1.min.js`; replace them with a new upstream version instead.
