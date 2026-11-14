import os

from core.organizer import SortResult, apply_plan, plan_sort, sort_folder, undo_sort


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


def test_plan_groups_files_by_category(tmp_path):
    _write_file(tmp_path, "photo.JPG")
    _write_file(tmp_path, "song.mp3")
    _write_file(tmp_path, "notes.unknown")

    plan = plan_sort(str(tmp_path))

    assert len(plan.moves) == 3
    assert plan.by_category() == {"Изображения": 1, "Аудио": 1, "Прочее": 1}


def test_plan_ignores_service_files(tmp_path):
    _write_file(tmp_path, "video.mp4")
    _write_file(tmp_path, "video.mp4.part")
    _write_file(tmp_path, "desktop.ini")

    plan = plan_sort(str(tmp_path))

    assert len(plan.moves) == 1
    assert plan.ignored == 2


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


def test_sort_is_idempotent(tmp_path):
    _write_file(tmp_path, "photo.png")
    sort_folder(str(tmp_path))

    plan = plan_sort(str(tmp_path))

    assert plan.moves == []


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


def test_undo_keeps_failed_moves_for_retry(tmp_path):
    source = _write_file(tmp_path, "song.mp3")
    result = sort_folder(str(tmp_path))
    _write_file(tmp_path, "song.mp3", "blocker")

    undo = undo_sort(result)

    assert undo.moved == 0
    assert undo.errors
    assert len(result.moved_paths) == 1

    os.remove(source)
    retry = undo_sort(result)

    assert retry.moved == 1
    assert result.moved_paths == []


def test_apply_plan_reports_busy_file(tmp_path, monkeypatch):
    _write_file(tmp_path, "photo.png")
    plan = plan_sort(str(tmp_path))

    def fake_move(*_args, **_kwargs):
        raise PermissionError

    monkeypatch.setattr("core.organizer.shutil.move", fake_move)
    result = apply_plan(plan)

    assert result.moved == 0
    assert "занят" in result.errors[0]


def test_empty_result_has_no_moves():
    result = SortResult()

    assert result.moved == 0
    assert result.errors == []
