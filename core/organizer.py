import os
import shutil
from collections import Counter

from core.rules import get_category, is_ignored


class SortPlan:
    def __init__(self):
        self.moves = []
        self.skipped = 0
        self.ignored = 0
        self.errors = []

    def by_category(self):
        """Сколько файлов уйдёт в каждую категорию."""
        counter = Counter(os.path.basename(os.path.dirname(dst)) for _, dst in self.moves)
        return dict(counter.most_common())

    def summary(self):
        text = f"К перемещению: {len(self.moves)}\nПропущено: {self.skipped}"
        if self.ignored:
            text += f"\nСлужебных файлов пропущено: {self.ignored}"
        categories = self.by_category()
        if categories:
            text += "\n" + ", ".join(f"{name}: {count}" for name, count in categories.items())
        if self.errors:
            text += "\n\nОшибки:\n" + "\n".join(self.errors)
        return text


class SortResult:
    def __init__(self):
        self.moved = 0
        self.skipped = 0
        self.ignored = 0
        self.errors = []
        self.moved_paths = []

    def summary(self):
        text = f"Перемещено файлов: {self.moved}\nПропущено: {self.skipped}"
        if self.ignored:
            text += f"\nСлужебных файлов пропущено: {self.ignored}"
        if self.errors:
            text += "\n\nОшибки:\n" + "\n".join(self.errors)
        return text


def unique_destination(target_dir, name):
    destination = os.path.join(target_dir, name)
    if not os.path.exists(destination):
        return destination

    base, ext = os.path.splitext(name)
    counter = 1
    while True:
        candidate = os.path.join(target_dir, f"{base} ({counter}){ext}")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def plan_sort(folder):
    plan = SortPlan()

    if not folder or not os.path.isdir(folder):
        plan.errors.append("Папка не найдена.")
        return plan

    try:
        with os.scandir(folder) as entries:
            names = [entry.name for entry in entries if entry.is_file()]
    except OSError as exc:
        plan.errors.append(f"Не удалось прочитать папку: {exc}")
        return plan

    for name in sorted(names, key=str.lower):
        if is_ignored(name):
            plan.ignored += 1
            continue

        path = os.path.join(folder, name)
        category = get_category(name)
        target_dir = os.path.join(folder, category)

        destination = unique_destination(target_dir, name)
        plan.moves.append((path, destination))

    return plan


def apply_plan(plan):
    result = SortResult()
    result.skipped = plan.skipped
    result.ignored = plan.ignored
    result.errors.extend(plan.errors)

    for source, destination in plan.moves:
        target_dir = os.path.dirname(destination)
        try:
            os.makedirs(target_dir, exist_ok=True)
            shutil.move(source, destination)
            result.moved += 1
            result.moved_paths.append((source, destination))
        except PermissionError:
            result.errors.append(f"{os.path.basename(source)}: файл занят другим процессом")
        except OSError as exc:
            result.errors.append(f"{os.path.basename(source)}: {exc}")

    return result


def sort_folder(folder):
    return apply_plan(plan_sort(folder))


def undo_sort(result):
    undo = SortResult()
    restored = []

    for source, destination in reversed(result.moved_paths):
        try:
            if not os.path.exists(destination):
                undo.errors.append(f"{os.path.basename(destination)}: файл не найден, пропущен")
                continue
            if os.path.exists(source):
                undo.errors.append(f"{os.path.basename(source)}: на исходном месте уже есть файл")
                continue
            os.makedirs(os.path.dirname(source), exist_ok=True)
            shutil.move(destination, source)
            undo.moved += 1
            restored.append((source, destination))
        except PermissionError:
            undo.errors.append(f"{os.path.basename(destination)}: файл занят другим процессом")
        except OSError as exc:
            undo.errors.append(f"{os.path.basename(destination)}: {exc}")

    _remove_empty_dirs(restored)
    # Файлы, которые вернуть не удалось, остаются доступными для повторной отмены.
    failed = [pair for pair in result.moved_paths if pair not in restored]
    result.moved_paths = failed
    return undo


def _remove_empty_dirs(moved_paths):
    dirs = {os.path.dirname(destination) for _, destination in moved_paths}
    for directory in sorted(dirs, key=len, reverse=True):
        try:
            if os.path.isdir(directory) and not os.listdir(directory):
                os.rmdir(directory)
        except OSError:
            pass
