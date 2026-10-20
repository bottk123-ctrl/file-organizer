import os
import shutil

from core.rules import get_category


class SortResult:
    def __init__(self):
        self.moved = 0
        self.skipped = 0
        self.errors = []

    def summary(self):
        text = f"Перемещено файлов: {self.moved}\nПропущено: {self.skipped}"
        if self.errors:
            text += "\n\nОшибки:\n" + "\n".join(self.errors)
        return text


def sort_folder(folder):
    result = SortResult()

    if not folder or not os.path.isdir(folder):
        result.errors.append("Папка не найдена.")
        return result

    try:
        entries = os.listdir(folder)
    except OSError as exc:
        result.errors.append(f"Не удалось прочитать папку: {exc}")
        return result

    for name in entries:
        path = os.path.join(folder, name)

        if not os.path.isfile(path):
            continue

        category = get_category(name)
        if category is None:
            result.skipped += 1
            continue

        target_dir = os.path.join(folder, category)
        try:
            os.makedirs(target_dir, exist_ok=True)
            shutil.move(path, os.path.join(target_dir, name))
            result.moved += 1
        except PermissionError:
            result.errors.append(f"{name}: файл занят другим процессом")
        except OSError as exc:
            result.errors.append(f"{name}: {exc}")

    return result
