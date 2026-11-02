import pytest

from core.rules import CATEGORIES, OTHER_CATEGORY, get_category


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("photo.jpg", "Изображения"),
        ("report.pdf", "Документы"),
        ("song.mp3", "Аудио"),
        ("archive.zip", "Архивы"),
        ("script.py", "Код"),
        ("installer.exe", "Программы"),
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
