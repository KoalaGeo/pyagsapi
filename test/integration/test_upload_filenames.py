"""Uploaded filenames are client-controlled and must never be used as a path.

Regression tests for path traversal / arbitrary file write via the multipart
filename (and ZIP member names) in /validate/ and /convert/.
"""
from io import BytesIO
from pathlib import Path
import zipfile

import pytest
from requests_toolbelt.multipart.encoder import MultipartEncoder

import app
from test.fixtures import API_VERSION, TEST_FILE_DIR

ENDPOINTS = [
    ('validate', [('checkers', 'ags'), ('fmt', 'json')]),
    ('convert', []),
]
LANDING_PAGE = Path(app.__file__).parent / 'templates' / 'landing_page.html'
AGS_CONTENT = (TEST_FILE_DIR / 'example_ags.ags').read_bytes()


@pytest.fixture
def landing_page_original():
    """Return the template's content and put it back afterwards.

    If the code under test were vulnerable, the attack would overwrite the real
    template; restore it so a failing test cannot damage the checkout.
    """
    original = LANDING_PAGE.read_bytes()
    yield original
    if LANDING_PAGE.read_bytes() != original:
        LANDING_PAGE.write_bytes(original)


async def post_files(async_client, endpoint, extra_fields, files):
    fields = [('files', file) for file in files] + extra_fields
    mp_encoder = MultipartEncoder(fields=fields)
    async with async_client as ac:
        return await ac.post(
            f'{API_VERSION}/{endpoint}/',
            headers={'Content-Type': mp_encoder.content_type},
            data=mp_encoder.to_string())


@pytest.mark.parametrize('endpoint, extra_fields', ENDPOINTS)
@pytest.mark.asyncio
async def test_absolute_filename_cannot_overwrite_app_template(async_client, landing_page_original,
                                                               endpoint, extra_fields):
    """The reported attack: upload with filename set to the app's own template."""
    response = await post_files(async_client, endpoint, extra_fields,
                                [(str(LANDING_PAGE), AGS_CONTENT, 'text/plain')])

    assert response.status_code == 200
    assert LANDING_PAGE.read_bytes() == landing_page_original


@pytest.mark.parametrize('endpoint, extra_fields', ENDPOINTS)
@pytest.mark.asyncio
async def test_relative_traversal_filename_is_not_written_outside(async_client, tmp_path,
                                                                  endpoint, extra_fields):
    target = tmp_path / 'pwned.ags'
    traversal_name = '../' * 20 + str(target).lstrip('/')

    response = await post_files(async_client, endpoint, extra_fields,
                                [(traversal_name, AGS_CONTENT, 'text/plain')])

    assert response.status_code == 200
    assert not target.exists()


@pytest.mark.parametrize('endpoint, extra_fields', ENDPOINTS)
@pytest.mark.asyncio
async def test_zip_member_names_are_not_written_outside(async_client, tmp_path, landing_page_original,
                                                        endpoint, extra_fields):
    relative_target = tmp_path / 'zip_rel.ags'
    absolute_target = tmp_path / 'zip_abs.ags'
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        archive.writestr('../' * 20 + str(relative_target).lstrip('/'), AGS_CONTENT)
        archive.writestr(str(absolute_target), AGS_CONTENT)
        archive.writestr(str(LANDING_PAGE), AGS_CONTENT)

    response = await post_files(async_client, endpoint, extra_fields,
                                [('bundle.zip', buffer.getvalue(), 'application/zip')])

    assert response.status_code == 200
    assert not relative_target.exists()
    assert not absolute_target.exists()
    assert LANDING_PAGE.read_bytes() == landing_page_original


@pytest.mark.asyncio
async def test_validate_reports_basename_only(async_client, tmp_path):
    target = tmp_path / 'example.ags'

    response = await post_files(async_client, 'validate', ENDPOINTS[0][1],
                                [(str(target), AGS_CONTENT, 'text/plain')])

    assert response.status_code == 200
    assert response.json()['data'][0]['filename'] == 'example.ags'
    assert not target.exists()


@pytest.mark.parametrize('endpoint, extra_fields', ENDPOINTS)
@pytest.mark.parametrize('filename', ['a' * 300 + '.ags', '..', '/tmp/'])
@pytest.mark.asyncio
async def test_unusable_filename_is_rejected_with_422(async_client, endpoint, extra_fields, filename):
    response = await post_files(async_client, endpoint, extra_fields,
                                [(filename, AGS_CONTENT, 'text/plain')])

    assert response.status_code == 422
    assert response.json()['errors'][0]['error'] == 'Invalid filename'
