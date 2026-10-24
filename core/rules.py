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
    "Книги": {".epub", ".mobi", ".fb2", ".djvu"},
}

OTHER_CATEGORY = "Прочее"


def get_category(filename):
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return OTHER_CATEGORY
