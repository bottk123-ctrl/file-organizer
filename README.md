# File Organizer

Десктопное приложение на Python для автоматической сортировки файлов по категориям. Выберите папку — программа разложит файлы по подпапкам.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

## Возможности

- Выбор папки через системный диалог
- Автоматическая сортировка файлов по категориям:
  - **Изображения** — `.jpg`, `.jpeg`, `.png`
  - **Документы** — `.pdf`, `.docx`, `.txt`
  - **Видео** — `.mp4`, `.avi`
  - **Архивы** — `.zip`, `.rar`
- Подпапки создаются автоматически
- Обработка ошибок: занятые файлы и проблемы доступа не «роняют» приложение
- Тёмная тема оформления

## Стек

- Python 3.11
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- PyInstaller (сборка `.exe`)

## Запуск из исходников

```bash
pip install -r requirements.txt
python main.py
```

## Сборка .exe

```bash
build.bat
```

Готовый файл появится в `dist\FileOrganizer.exe`. Сборка выполняется через PyInstaller в режиме `--onefile --windowed`.

## Структура проекта

```
file-organizer/
├── main.py              # точка входа
├── config.py            # настройки приложения
├── build.bat            # сборка .exe
├── requirements.txt
├── requirements-dev.txt
├── ui/
│   └── app.py           # главное окно
└── core/
    ├── organizer.py     # логика сортировки
    └── rules.py         # категории и расширения
```

## Лицензия

MIT
