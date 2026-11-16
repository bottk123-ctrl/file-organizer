import json
import os

from core.history import data_dir

CATEGORIES = {
    "Изображения": {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico",
        ".tif", ".tiff", ".heic", ".avif", ".raw",
    },
    "Документы": {
        ".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".md", ".pages",
        ".tex",
    },
    "Таблицы": {".xlsx", ".xls", ".csv", ".ods", ".tsv", ".numbers"},
    "Презентации": {".pptx", ".ppt", ".odp", ".key"},
    "Видео": {
        ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".webm", ".flv", ".m4v",
    },
    "Аудио": {
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".opus",
    },
    "Архивы": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
    "Код": {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".html", ".css",
        ".scss", ".java", ".cpp", ".c", ".h", ".hpp", ".cs", ".go", ".rs",
        ".php", ".rb", ".swift", ".kt", ".sh", ".ps1", ".bat",
        ".xml", ".yml", ".yaml", ".toml", ".ini",
    },
    "Шрифты": {".ttf", ".otf", ".woff", ".woff2"},
    "Программы": {".exe", ".msi", ".apk", ".deb", ".dmg", ".appx"},
    "Дизайн": {".psd", ".ai", ".xd", ".fig", ".sketch"},
    "3D": {".obj", ".fbx", ".stl", ".blend", ".3ds"},
    "Базы данных": {".sql", ".db", ".sqlite", ".sqlite3", ".mdb"},
    "Книги": {".epub", ".mobi", ".fb2", ".djvu", ".azw3"},
}

OTHER_CATEGORY = "Прочее"

CUSTOM_RULES_FILENAME = "categories.json"

# Служебные файлы, которые сортировать бессмысленно.
IGNORED_NAMES = {"desktop.ini", "thumbs.db", ".ds_store"}
IGNORED_PREFIXES = ("~$",)
IGNORED_SUFFIXES = (".tmp", ".temp", ".crdownload", ".part", ".partial")


def get_extension(filename):
    """Вернуть расширение в нижнем регистре, включая точку ('' если его нет)."""
    base = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    stem, dot, ext = base.rpartition(".")
    # Для .gitignore расширения нет: точка в начале имени не считается.
    if not dot or not stem:
        return ""
    return "." + ext.lower()


def is_ignored(filename):
    """Служебные и временные файлы, которые не нужно перемещать."""
    name = filename.lower()
    if name in IGNORED_NAMES:
        return True
    if name.startswith(IGNORED_PREFIXES):
        return True
    return name.endswith(IGNORED_SUFFIXES)


def load_custom_categories(path=None):
    """Прочитать пользовательские категории: {"Категория": [".ext", ...]}.

    Файл лежит рядом с историей (categories.json). Битый или пустой файл —
    просто работаем со стандартными правилами, без ошибок.
    """
    if path is None:
        path = os.path.join(data_dir(), CUSTOM_RULES_FILENAME)
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}

    custom = {}
    for category, extensions in data.items():
        if not isinstance(category, str) or not isinstance(extensions, list):
            continue
        exts = {str(ext).lower() for ext in extensions if isinstance(ext, str)}
        if category and exts:
            custom[category] = exts
    return custom


def build_lookup():
    """Карта «расширение -> категория» с учётом пользовательских правил.

    Пользовательские правила применяются после стандартных и могут
    переопределять стандартные категории.
    """
    lookup = {}
    for category, extensions in CATEGORIES.items():
        for extension in extensions:
            lookup[extension] = category
    for category, extensions in load_custom_categories().items():
        for extension in extensions:
            lookup[extension] = category
    return lookup


def get_category(filename, lookup=None):
    """Вернуть категорию файла по его расширению (без учёта регистра)."""
    if lookup is None:
        lookup = build_lookup()
    return lookup.get(get_extension(filename), OTHER_CATEGORY)
