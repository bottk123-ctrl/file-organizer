CATEGORIES = {
    "Изображения": {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico",
        ".tif", ".tiff", ".heic", ".avif", ".raw", ".psd",
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
        ".php", ".rb", ".swift", ".kt", ".sql", ".sh", ".ps1", ".bat",
        ".xml", ".yml", ".yaml", ".toml", ".ini",
    },
    "Шрифты": {".ttf", ".otf", ".woff", ".woff2"},
    "Программы": {".exe", ".msi", ".apk", ".deb", ".dmg", ".appx"},
    "Книги": {".epub", ".mobi", ".fb2", ".djvu", ".azw3"},
}

OTHER_CATEGORY = "Прочее"

# Служебные файлы, которые сортировать бессмысленно.
IGNORED_NAMES = {"desktop.ini", "thumbs.db", ".ds_store"}
IGNORED_PREFIXES = ("~$",)
IGNORED_SUFFIXES = (".tmp", ".temp", ".crdownload", ".part", ".partial")


def get_extension(filename):
    """Возвращает расширение в нижнем регистре, включая точку ('' если его нет)."""
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


def get_category(filename):
    ext = get_extension(filename)
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return OTHER_CATEGORY
