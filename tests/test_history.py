import json

from core import history


def _touch(path, text="x"):
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_save_and_load_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("FILE_ORGANIZER_DATA_DIR", str(tmp_path / "data"))
    source = _touch(tmp_path / "photo.jpg")
    (tmp_path / "out").mkdir()
    destination = _touch(tmp_path / "out" / "photo.jpg")

    assert history.save_history([(source, destination)])

    assert history.load_history() == [(source, destination)]


def test_load_history_missing_file_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("FILE_ORGANIZER_DATA_DIR", str(tmp_path / "data"))

    assert history.load_history() == []


def test_load_history_skips_broken_entries(tmp_path, monkeypatch):
    monkeypatch.setenv("FILE_ORGANIZER_DATA_DIR", str(tmp_path / "data"))
    path = tmp_path / "data" / "last-sort.json"
    path.parent.mkdir()
    existing = _touch(tmp_path / "exists.txt")
    path.write_text(
        json.dumps(
            {
                "moved": [
                    ["a", existing],
                    ["b", str(tmp_path / "missing.txt")],
                    ["bad-entry"],
                    "junk",
                ]
            }
        ),
        encoding="utf-8",
    )

    assert history.load_history() == [("a", existing)]


def test_load_history_ignores_corrupted_json(tmp_path, monkeypatch):
    monkeypatch.setenv("FILE_ORGANIZER_DATA_DIR", str(tmp_path / "data"))
    path = tmp_path / "data" / "last-sort.json"
    path.parent.mkdir()
    path.write_text("{not json", encoding="utf-8")

    assert history.load_history() == []


def test_clear_history_removes_file(tmp_path, monkeypatch):
    monkeypatch.setenv("FILE_ORGANIZER_DATA_DIR", str(tmp_path / "data"))
    history.save_history([])
    assert history.history_path()
    assert (tmp_path / "data" / "last-sort.json").exists()

    history.clear_history()

    assert not (tmp_path / "data" / "last-sort.json").exists()
    history.clear_history()  # повторный вызов не падает
