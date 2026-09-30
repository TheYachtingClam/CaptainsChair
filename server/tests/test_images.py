import json

import pytest

from app import content


@pytest.fixture
def images(tmp_path, monkeypatch):
    (tmp_path / "to_boldly_go").mkdir()
    (tmp_path / "to_boldly_go" / "2GEO01.webp").write_bytes(b"RIFF-fake-webp")
    (tmp_path / "captains" / "soval").mkdir(parents=True)
    (tmp_path / "captains" / "soval" / "2SOV01.webp").write_bytes(b"RIFF-soval")
    (tmp_path / "secret.txt").write_text("not an image")
    manifest = {
        "cards": {
            "2GEO01": {"set": "to_boldly_go", "file": "to_boldly_go/2GEO01.webp", "version": "abc123"},
            "2SOV01": {"folder": "captains/soval", "file": "captains/soval/2SOV01.webp", "version": "def456"},
            "EVIL": {"set": "x", "file": "../../etc/passwd", "version": "x"},
        }
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(content, "IMAGES_DIR", tmp_path)
    monkeypatch.setattr(content, "_manifest_cache", None)
    return tmp_path


def test_images_need_login(client, images):
    assert client.get("/api/content/cards/2GEO01/image").status_code == 401
    assert client.get("/api/content/images").status_code == 401


def test_image_list_has_versioned_urls(authed, images):
    urls = authed.get("/api/content/images").json()
    assert urls["2GEO01"] == "/api/content/cards/2GEO01/image?v=abc123"


def test_serves_image_with_long_cache_for_current_version(authed, images):
    r = authed.get("/api/content/cards/2GEO01/image?v=abc123")
    assert r.status_code == 200
    assert r.content == b"RIFF-fake-webp"
    assert r.headers["content-type"] == "image/webp"
    assert r.headers["cache-control"] == "private, max-age=31536000, immutable"


def test_old_or_missing_version_is_not_cached_for_long(authed, images):
    r = authed.get("/api/content/cards/2GEO01/image?v=old")
    assert r.headers["cache-control"] == "private, no-cache"


def test_unknown_card_and_escaping_paths_are_refused(authed, images):
    assert authed.get("/api/content/cards/NOPE/image").status_code == 404
    assert authed.get("/api/content/cards/EVIL/image").status_code == 404
    assert authed.get("/api/content/cards/secret.txt/image").status_code == 404


def test_no_manifest_means_no_images(authed, tmp_path, monkeypatch):
    monkeypatch.setattr(content, "IMAGES_DIR", tmp_path)
    monkeypatch.setattr(content, "_manifest_cache", None)
    assert authed.get("/api/content/images").json() == {}


def test_serves_images_from_nested_folders(authed, images):
    r = authed.get("/api/content/cards/2SOV01/image?v=def456")
    assert r.status_code == 200
    assert r.content == b"RIFF-soval"
