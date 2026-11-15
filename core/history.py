import json
import os

APP_DIRNAME = "FileOrganizer"
HISTORY_FILENAME = "last-sort.json"


def data_dir():
    """Папка для данных приложения (переопределяется переменной окружения)."""
    override = os.environ.get("FILE_ORGANIZER_DATA_DIR")
    if override:
        return override
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return os.path.join(base, APP_DIRNAME)


def history_path():
    return os.path.join(data_dir(), HISTORY_FILENAME)


def save_history(moved_paths):
    """Сохранить последнюю сортировку, чтобы отмена работала после перезапуска."""
    path = history_path()
    pairs = [[source, destination] for source, destination in moved_paths]
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump({"moved": pairs}, handle, ensure_ascii=False, indent=2)
    except OSError:
        # История — вспомогательная функция, её сбой не должен ломать сортировку.
        return False
    return True


def load_history():
    """Вернуть список пар (откуда, куда) последней сортировки."""
    try:
        with open(history_path(), "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return []

    pairs = []
    for item in data.get("moved", []):
        if (
            isinstance(item, list)
            and len(item) == 2
            and all(isinstance(value, str) for value in item)
        ):
            source, destination = item
            # Записи, которых уже нет на месте, отменять бессмысленно.
            if os.path.isfile(destination):
                pairs.append((source, destination))
    return pairs


def clear_history():
    try:
        os.remove(history_path())
    except OSError:
        pass
