import json

import pytest

from app import content


def entry(kind, file, version, width=630, height=880):
    return {"kind": kind, "file": file, "version": version, "width": width, "height": height}


@pytest.fixture
def images(tmp_path, monkeypatch):
    files = {
        "cards/to_boldly_go/2GEO01.webp": b"RIFF-geo",
        "cards/captains/soval/2SOV01.webp": b"RIFF-soval",
        "boards/cb-soval-basic.webp": b"RIFF-board",
    }
    for rel, data in files.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_bytes(data)
    (tmp_path / "secret.txt").write_text("not an image")
    manifest = {
        "images": {
            "2GEO01": entry("cards", "cards/to_boldly_go/2GEO01.webp", "abc123"),
            "2SOV01": entry("cards", "cards/captains/soval/2SOV01.webp", "def456"),
            "cb-soval-basic": entry("boards", "boards/cb-soval-basic.webp", "b0a4d1", 1800, 1405),
            "EVIL": entry("cards", "../../etc/passwd", "x"),
        }
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(content, "IMAGES_DIR", tmp_path)
    monkeypatch.setattr(content, "_manifest_cache", None)
    return tmp_path


def test_images_need_login(client, images):
    assert client.get("/api/content/images/2GEO01").status_code == 401
    assert client.get("/api/content/images").status_code == 401


def test_image_list(authed, images):
    listing = authed.get("/api/content/images").json()
    assert listing["2GEO01"] == {
        "url": "/api/content/images/2GEO01?v=abc123", "kind": "cards", "width": 630, "height": 880,
    }
    assert listing["cb-soval-basic"]["width"] == 1800


def test_image_list_filtered_by_kind(authed, images):
    assert set(authed.get("/api/content/images?kind=boards").json()) == {"cb-soval-basic"}


def test_serves_image_with_long_cache_for_current_version(authed, images):
    r = authed.get("/api/content/images/2GEO01?v=abc123")
    assert r.status_code == 200
    assert r.content == b"RIFF-geo"
    assert r.headers["content-type"] == "image/webp"
    assert r.headers["cache-control"] == "private, max-age=31536000, immutable"


def test_serves_nested_folders_and_boards(authed, images):
    assert authed.get("/api/content/images/2SOV01").content == b"RIFF-soval"
    assert authed.get("/api/content/images/cb-soval-basic").content == b"RIFF-board"


def test_old_or_missing_version_is_not_cached_for_long(authed, images):
    r = authed.get("/api/content/images/2GEO01?v=old")
    assert r.headers["cache-control"] == "private, no-cache"


def test_unknown_and_escaping_paths_are_refused(authed, images):
    assert authed.get("/api/content/images/NOPE").status_code == 404
    assert authed.get("/api/content/images/EVIL").status_code == 404
    assert authed.get("/api/content/images/secret.txt").status_code == 404


def test_no_manifest_means_no_images(authed, tmp_path, monkeypatch):
    monkeypatch.setattr(content, "IMAGES_DIR", tmp_path)
    monkeypatch.setattr(content, "_manifest_cache", None)
    assert authed.get("/api/content/images").json() == {}
