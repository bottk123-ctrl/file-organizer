import os

from core.organizer import SortResult, plan_sort, sort_folder, undo_sort


def _write_file(folder, name, text="x"):
    path = os.path.join(str(folder), name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


def test_plan_ignores_subdirectories(tmp_path):
    os.makedirs(tmp_path / "already_sorted")
    _write_file(tmp_path, "photo.jpg")

    plan = plan_sort(str(tmp_path))

    assert [os.path.basename(source) for source, _ in plan.moves] == ["photo.jpg"]


def test_plan_reports_missing_folder(tmp_path):
    plan = plan_sort(str(tmp_path / "nope"))

    assert plan.moves == []
    assert plan.errors


def test_plan_targets_category_subfolders(tmp_path):
    _write_file(tmp_path, "photo.jpg")
    _write_file(tmp_path, "song.mp3")

    plan = plan_sort(str(tmp_path))

    targets = {os.path.basename(os.path.dirname(dst)) for _, dst in plan.moves}
    assert targets == {"Изображения", "Аудио"}


def test_sort_moves_files_into_category_folders(tmp_path):
    _write_file(tmp_path, "photo.jpg")
    _write_file(tmp_path, "notes.txt")

    result = sort_folder(str(tmp_path))

    assert result.moved == 2
    assert os.path.isfile(tmp_path / "Изображения" / "photo.jpg")
    assert os.path.isfile(tmp_path / "Документы" / "notes.txt")


def test_sort_resolves_name_conflicts(tmp_path):
    os.makedirs(tmp_path / "Изображения")
    _write_file(tmp_path, "photo.jpg", "новый")
    _write_file(tmp_path / "Изображения", "photo.jpg", "старый")

    result = sort_folder(str(tmp_path))

    assert result.moved == 1
    assert os.path.isfile(tmp_path / "Изображения" / "photo (1).jpg")
    existing = tmp_path / "Изображения" / "photo.jpg"
    assert existing.read_text(encoding="utf-8") == "старый"


def test_undo_restores_files_and_removes_empty_folders(tmp_path):
    _write_file(tmp_path, "photo.jpg")
    result = sort_folder(str(tmp_path))
    assert os.path.isdir(tmp_path / "Изображения")

    undo = undo_sort(result)

    assert undo.moved == 1
    assert os.path.isfile(tmp_path / "photo.jpg")
    assert not os.path.isdir(tmp_path / "Изображения")


def test_undo_reports_file_that_is_already_gone(tmp_path):
    _write_file(tmp_path, "photo.jpg")
    result = sort_folder(str(tmp_path))
    os.remove(tmp_path / "Изображения" / "photo.jpg")

    undo = undo_sort(result)

    assert undo.moved == 0
    assert undo.errors


def test_empty_result_has_no_moves():
    result = SortResult()

    assert result.moved == 0
    assert result.errors == []
