import os

from main import main


def _touch(folder, name):
    path = os.path.join(str(folder), name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("x")
    return path


def test_dry_run_does_not_move_files(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("FILE_ORGANIZER_DATA_DIR", str(tmp_path / "data"))
    _touch(tmp_path, "photo.jpg")

    code = main(["--folder", str(tmp_path), "--dry-run"])

    assert code == 0
    assert os.path.isfile(tmp_path / "photo.jpg")
    assert "Изображения" in capsys.readouterr().out


def test_sort_with_yes_moves_files(tmp_path, monkeypatch):
    monkeypatch.setenv("FILE_ORGANIZER_DATA_DIR", str(tmp_path / "data"))
    _touch(tmp_path, "photo.jpg")

    code = main(["--folder", str(tmp_path), "--yes"])

    assert code == 0
    assert os.path.isfile(tmp_path / "Изображения" / "photo.jpg")


def test_sort_asks_for_confirmation(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("FILE_ORGANIZER_DATA_DIR", str(tmp_path / "data"))
    _touch(tmp_path, "photo.jpg")
    monkeypatch.setattr("builtins.input", lambda _prompt: "n")

    code = main(["--folder", str(tmp_path)])

    assert code == 0
    assert os.path.isfile(tmp_path / "photo.jpg")
    assert "Отменено" in capsys.readouterr().out


def test_undo_restores_last_sort(tmp_path, monkeypatch):
    monkeypatch.setenv("FILE_ORGANIZER_DATA_DIR", str(tmp_path / "data"))
    _touch(tmp_path, "photo.jpg")
    main(["--folder", str(tmp_path), "--yes"])

    code = main(["--undo"])

    assert code == 0
    assert os.path.isfile(tmp_path / "photo.jpg")
    assert not os.path.exists(tmp_path / "Изображения")


def test_undo_without_history_returns_error(tmp_path, monkeypatch):
    monkeypatch.setenv("FILE_ORGANIZER_DATA_DIR", str(tmp_path / "data"))

    assert main(["--undo"]) == 1


def test_missing_folder_returns_error(tmp_path, monkeypatch):
    monkeypatch.setenv("FILE_ORGANIZER_DATA_DIR", str(tmp_path / "data"))

    assert main(["--folder", str(tmp_path / "nope")]) == 1


def test_version_flag(capsys):
    try:
        main(["--version"])
    except SystemExit as exc:  # argparse выходит через SystemExit
        assert exc.code == 0
    assert "File Organizer" in capsys.readouterr().out
