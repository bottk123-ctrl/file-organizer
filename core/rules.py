CATEGORIES = {
    "Изображения": {".jpg", ".jpeg", ".png"},
    "Документы": {".pdf", ".docx", ".txt"},
    "Видео": {".mp4", ".avi"},
    "Архивы": {".zip", ".rar"},
}


def get_category(filename):
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return None
