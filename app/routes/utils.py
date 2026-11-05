import os
import unicodedata
from pathlib import Path

from fastapi import HTTPException, status

from app.model.schema import Checker
from app.checkers import check_ags, check_bgs
from app.version import API_VERSION
from .errors import error_responses

# Get AGS_API_ENV, defaults to DEVELOP if not set or not recognised.
AGS_API_ENV = os.getenv("AGS_API_ENV", "DEVELOP").upper()

AGS_API_VERSION = f"/v{API_VERSION.split('.')[0]}"

BOREHOLE_EXPORT_LIMIT = 50
BOREHOLE_VIEWER_URL = "https://gwbv.bgs.ac.uk/GWBV/viewborehole?loca_id={bgs_loca_id}"
BOREHOLE_EXPORT_URL = "https://gwbv.bgs.ac.uk/ags_export?loca_ids={bgs_loca_id}"
BOREHOLE_INDEX_URL = (
    "https://ogcapi.bgs.ac.uk/collections/agsboreholeindex/items?f=json"
    "&properties=bgs_loca_id&filter=INTERSECTS(shape,{polygon})&limit={borehole_export_limit}"
)

log_responses = dict(error_responses)
log_responses["200"] = {
    "content": {"application/json": {}, "text/plain": {}},
    "description": "Return a log in json or text",
}

zip_responses = dict(error_responses)
zip_responses["200"] = {
    "content": {"application/x-zip-compressed": {}},
    "description": "Return a zip containing successfully converted files and log file",
}

pdf_responses = dict(error_responses)
pdf_responses["200"] = {
    "content": {"application/pdf": {}},
    "description": "Return a graphical log of AGS data in .PDF format",
}

ags_export_responses = dict(error_responses)
ags_export_responses["200"] = {
    "content": {"application/x-zip-compressed": {}, "application/json": {}},
    "description": (
        "Return a zip containing .ags file and metadata .txt file "
        "or a json response containing the borehole ID count"
    ),
}


checker_functions = {
    Checker.ags: check_ags,
    Checker.bgs: check_bgs,
}


# Longest single path component most filesystems accept, in bytes
MAX_FILENAME_BYTES = 255


def safe_filename(filename: str) -> str:
    """Return a safe basename for an untrusted uploaded or zipped filename.

    The filename is client-controlled.  Only the final path component is kept,
    so an absolute path or a name containing ``..`` cannot be used to write
    outside the intended directory (path traversal / arbitrary file write).
    Returns an empty string for names that cannot be used safely: empty,
    ``.``, ``..``, a directory entry such as ``folder/``, a name containing
    control characters (e.g. NUL or newline) or one longer than
    MAX_FILENAME_BYTES.
    """
    raw = str(filename)
    if raw.endswith("/") or raw.endswith(os.sep):
        # Directory entry (e.g. a folder inside a zip), not a file
        return ""
    name = Path(raw).name
    if name in ("", ".", ".."):
        return ""
    if any(unicodedata.category(char) == "Cc" for char in name):
        return ""
    if len(name.encode("utf-8", errors="replace")) > MAX_FILENAME_BYTES:
        return ""
    return name


def contained_path(directory: Path, name: str) -> Path:
    """Return directory / name, refusing any path that is not directly inside directory.

    safe_filename() already guarantees this; the check makes the guarantee
    explicit so that a future change cannot silently reintroduce a write
    outside the per-request temporary directory.
    """
    path = directory / name
    if path.resolve().parent != directory.resolve():
        raise ValueError(f"Refusing to write {name!r} outside {directory}")
    return path


def invalid_filename_error() -> HTTPException:
    """422 response for an uploaded file whose name cannot be used safely."""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "msg": "Invalid filename",
            "error": "Invalid filename",
            "desc": (
                "Uploaded filenames must not be empty, a directory, contain "
                f"control characters or be longer than {MAX_FILENAME_BYTES} bytes"
            ),
        },
    )


def get_request_url(request):
    """External calls need https to be returned, so check environment."""
    request_url = str(request.url)
    if AGS_API_ENV == "PRODUCTION" and request_url.startswith("http:"):
        request_url = request_url.replace("http:", "https:")

    return request_url
