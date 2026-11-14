import os

from core.organizer import apply_plan, plan_sort, sort_folder, undo_sort


def touch(folder, name, content="x"):
    path = os.path.join(folder, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
    return path


def test_plan_groups_files_by_category(tmp_path):
    touch(tmp_path, "photo.JPG")
    touch(tmp_path, "song.mp3")
    touch(tmp_path, "notes.unknown")

    plan = plan_sort(str(tmp_path))

    assert len(plan.moves) == 3
    assert plan.by_category() == {"Изображения": 1, "Аудио": 1, "Прочее": 1}


def test_plan_ignores_service_files(tmp_path):
    touch(tmp_path, "video.mp4")
    touch(tmp_path, "video.mp4.part")
    touch(tmp_path, "desktop.ini")

    plan = plan_sort(str(tmp_path))

    assert len(plan.moves) == 1
    assert plan.ignored == 2


def test_plan_skips_directories(tmp_path):
    os.makedirs(os.path.join(tmp_path, "subfolder"))
    touch(tmp_path, "file.pdf")

    plan = plan_sort(str(tmp_path))

    assert len(plan.moves) == 1
    assert os.path.basename(plan.moves[0][1]) == "file.pdf"


def test_plan_missing_folder_reports_error(tmp_path):
    plan = plan_sort(str(tmp_path / "missing"))

    assert plan.moves == []
    assert plan.errors


def test_apply_plan_moves_files(tmp_path):
    source = touch(tmp_path, "photo.png")
    result = sort_folder(str(tmp_path))

    assert result.moved == 1
    assert result.errors == []
    assert not os.path.exists(source)
    assert os.path.isfile(os.path.join(tmp_path, "Изображения", "photo.png"))


def test_name_conflict_gets_suffix(tmp_path):
    touch(tmp_path, "photo.png", "first")
    target_dir = os.path.join(tmp_path, "Изображения")
    os.makedirs(target_dir)
    touch(target_dir, "photo.png", "existing")

    result = sort_folder(str(tmp_path))

    assert result.moved == 1
    moved_to = os.path.basename(result.moved_paths[0][1])
    assert moved_to == "photo (1).png"


def test_sort_is_idempotent(tmp_path):
    touch(tmp_path, "photo.png")
    sort_folder(str(tmp_path))

    plan = plan_sort(str(tmp_path))

    assert plan.moves == []


def test_undo_restores_files_and_removes_empty_dirs(tmp_path):
    source = touch(tmp_path, "song.mp3")
    result = sort_folder(str(tmp_path))

    undo = undo_sort(result)

    assert undo.moved == 1
    assert undo.errors == []
    assert os.path.isfile(source)
    assert not os.path.exists(os.path.join(tmp_path, "Аудио"))


def test_undo_keeps_failed_moves_for_retry(tmp_path):
    source = touch(tmp_path, "song.mp3")
    result = sort_folder(str(tmp_path))
    touch(tmp_path, "song.mp3", "blocker")

    undo = undo_sort(result)

    assert undo.moved == 0
    assert undo.errors
    assert len(result.moved_paths) == 1

    os.remove(source)
    retry = undo_sort(result)

    assert retry.moved == 1
    assert result.moved_paths == []


def test_apply_plan_reports_busy_file(tmp_path, monkeypatch):
    touch(tmp_path, "photo.png")
    plan = plan_sort(str(tmp_path))

    def fake_move(*_args, **_kwargs):
        raise PermissionError

    monkeypatch.setattr("core.organizer.shutil.move", fake_move)
    result = apply_plan(plan)

    assert result.moved == 0
    assert "занят" in result.errors[0]
