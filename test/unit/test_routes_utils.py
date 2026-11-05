"""Tests for the upload filename helpers in app.routes.utils."""
from pathlib import Path

import pytest

from app.routes.utils import MAX_FILENAME_BYTES, contained_path, safe_filename


@pytest.mark.parametrize('filename, expected', [
    # Ordinary names are kept as-is
    ('example.ags', 'example.ags'),
    ('Fenham Barracks - Newcastle upon Tyne.ags', 'Fenham Barracks - Newcastle upon Tyne.ags'),
    ('données.xlsx', 'données.xlsx'),
    # Directory components are stripped (path traversal)
    ('/code/app/templates/landing_page.html', 'landing_page.html'),
    ('../../../../tmp/pwned.ags', 'pwned.ags'),
    ('....//....//tmp/x.ags', 'x.ags'),
    ('folder/example.ags', 'example.ags'),
    # Names that do not refer to a file are rejected
    ('', ''),
    ('.', ''),
    ('..', ''),
    ('/', ''),
    ('folder/', ''),
    ('/tmp/', ''),
    # Control characters are rejected
    ('nul\x00.ags', ''),
    ('new\nline.ags', ''),
    ('carriage\r.ags', ''),
    ('tab\t.ags', ''),
    # Over-long names are rejected
    ('a' * (MAX_FILENAME_BYTES - 4) + '.ags', 'a' * (MAX_FILENAME_BYTES - 4) + '.ags'),
    ('a' * MAX_FILENAME_BYTES + '.ags', ''),
])
def test_safe_filename(filename, expected):
    assert safe_filename(filename) == expected


def test_safe_filename_result_never_contains_a_separator():
    for filename in ['/etc/passwd', '../x', 'a/b/c', '/']:
        assert '/' not in safe_filename(filename)


def test_contained_path_allows_a_plain_name(tmp_path):
    assert contained_path(tmp_path, 'example.ags') == tmp_path / 'example.ags'


@pytest.mark.parametrize('name', [
    '../escape.ags',
    '/etc/passwd',
    'sub/dir.ags',
    '..',
])
def test_contained_path_refuses_names_outside_the_directory(tmp_path, name):
    with pytest.raises(ValueError):
        contained_path(tmp_path, name)


def test_contained_path_refuses_symlink_out_of_directory(tmp_path):
    outside = tmp_path / 'outside'
    outside.mkdir()
    inside = tmp_path / 'inside'
    inside.mkdir()
    (inside / 'link.ags').symlink_to(outside / 'target.ags')

    with pytest.raises(ValueError):
        contained_path(inside, 'link.ags')
    assert not Path(outside / 'target.ags').exists()
