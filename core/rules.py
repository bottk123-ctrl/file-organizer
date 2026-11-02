import os

CATEGORIES = {
    "Изображения": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico"},
    "Документы": {".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt"},
    "Таблицы": {".xlsx", ".xls", ".csv", ".ods"},
    "Видео": {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".webm"},
    "Аудио": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
    "Архивы": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Код": {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".html", ".css",
        ".java", ".cpp", ".c", ".h", ".cs", ".go", ".rs", ".php", ".xml", ".yml", ".yaml",
    },
    "Шрифты": {".ttf", ".otf", ".woff", ".woff2"},
    "Программы": {".exe", ".msi", ".apk", ".deb", ".dmg"},
    "Дизайн": {".psd", ".ai", ".xd", ".fig", ".sketch"},
    "3D": {".obj", ".fbx", ".stl", ".blend", ".3ds"},
    "Базы данных": {".sql", ".db", ".sqlite", ".sqlite3", ".mdb"},
    "Книги": {".epub", ".mobi", ".fb2", ".djvu"},
}

OTHER_CATEGORY = "Прочее"


def get_category(filename: str) -> str:
    """Вернуть категорию файла по его расширению (без учёта регистра)."""
    extension = os.path.splitext(filename)[1].lower()
    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category
    return OTHER_CATEGORY
