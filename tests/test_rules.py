import pytest

import json

from core.rules import (
    CATEGORIES,
    OTHER_CATEGORY,
    build_lookup,
    get_category,
    get_extension,
    is_ignored,
)


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("photo.jpg", "Изображения"),
        ("report.pdf", "Документы"),
        ("song.mp3", "Аудио"),
        ("archive.zip", "Архивы"),
        ("script.py", "Код"),
        ("installer.exe", "Программы"),
        ("layout.psd", "Дизайн"),
        ("model.fbx", "3D"),
        ("database.sqlite", "Базы данных"),
        ("book.epub", "Книги"),
    ],
)
def test_known_extensions_are_sorted(filename, expected):
    assert get_category(filename) == expected


def test_lookup_ignores_extension_case():
    assert get_category("PHOTO.JPG") == "Изображения"
    assert get_category("Archive.ZIP") == "Архивы"


def test_multi_dot_names_use_the_last_extension():
    assert get_category("backup.tar.gz") == "Архивы"


@pytest.mark.parametrize("filename", ["notes", "installer.bin", ".env"])
def test_unknown_extensions_fall_back_to_other(filename):
    assert get_category(filename) == OTHER_CATEGORY


def test_extension_is_listed_in_only_one_category():
    seen = {}
    for category, extensions in CATEGORIES.items():
        for extension in extensions:
            assert extension not in seen, (
                f"{extension} указан и в «{seen[extension]}», и в «{category}»"
            )
            seen[extension] = category


def test_extension_lowercased():
    assert get_extension("Photo.JPG") == ".jpg"
    assert get_extension("archive.tar.gz") == ".gz"
    assert get_extension("no_extension") == ""
    assert get_extension(".gitignore") == ""


@pytest.mark.parametrize(
    "name",
    ["desktop.ini", "Thumbs.db", "~$report.docx", "video.mp4.crdownload", "data.tmp"],
)
def test_ignored_files(name):
    assert is_ignored(name)


@pytest.mark.parametrize("name", ["photo.jpg", "~notes.txt"])
def test_regular_files_are_not_ignored(name):
    assert not is_ignored(name)


def test_custom_categories_extend_defaults(tmp_path, monkeypatch):
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setenv("FILE_ORGANIZER_DATA_DIR", str(data))
    (data / "categories.json").write_text(
        json.dumps({"Музыка": [".flp"], "Книги": [".cbr"]}), encoding="utf-8"
    )

    lookup = build_lookup()

    assert get_category("beat.flp", lookup) == "Музыка"
    assert get_category("comix.cbr", lookup) == "Книги"
    assert get_category("photo.jpg", lookup) == "Изображения"


def test_custom_categories_can_override_defaults(tmp_path, monkeypatch):
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setenv("FILE_ORGANIZER_DATA_DIR", str(data))
    (data / "categories.json").write_text(
        json.dumps({"Мои картинки": [".jpg", ".png"]}), encoding="utf-8"
    )

    lookup = build_lookup()

    assert get_category("photo.jpg", lookup) == "Мои картинки"


def test_broken_custom_categories_are_ignored(tmp_path, monkeypatch):
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setenv("FILE_ORGANIZER_DATA_DIR", str(data))
    (data / "categories.json").write_text("{ это не json", encoding="utf-8")

    assert get_category("photo.jpg") == "Изображения"
    assert get_category("unknown.xyz") == OTHER_CATEGORY


def test_custom_categories_without_valid_extensions_are_skipped(tmp_path, monkeypatch):
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setenv("FILE_ORGANIZER_DATA_DIR", str(data))
    (data / "categories.json").write_text(
        json.dumps({"Пустые": [], "Мусор": "не список", "Годные": [".zzz"]}),
        encoding="utf-8",
    )

    lookup = build_lookup()

    assert ".zzz" in lookup
    assert "Годные" not in lookup  # карта хранит расширения, а не категории
    assert ".bin" not in lookup
