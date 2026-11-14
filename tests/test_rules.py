from core.rules import get_category, get_extension, is_ignored


def test_extension_lowercased():
    assert get_extension("Photo.JPG") == ".jpg"
    assert get_extension("archive.tar.gz") == ".gz"
    assert get_extension("no_extension") == ""
    assert get_extension(".gitignore") == ""


def test_category_lookup():
    assert get_category("song.mp3") == "Аудио"
    assert get_category("Movie.MKV") == "Видео"
    assert get_category("report.xlsx") == "Таблицы"
    assert get_category("script.PY") == "Код"
    assert get_category("unknown.xyz") == "Прочее"
    assert get_category("README") == "Прочее"


def test_ignored_files():
    assert is_ignored("desktop.ini")
    assert is_ignored("Thumbs.db")
    assert is_ignored("~$report.docx")
    assert is_ignored("video.mp4.crdownload")
    assert is_ignored("data.tmp")
    assert not is_ignored("photo.jpg")
    assert not is_ignored("~notes.txt")
