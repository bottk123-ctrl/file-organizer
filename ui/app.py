import os

import customtkinter as ctk
from tkinter import filedialog, messagebox

import config
from core.history import clear_history, load_history, save_history
from core.organizer import SortResult, plan_sort, apply_plan, undo_sort


class App(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode(config.APPEARANCE_MODE)
        ctk.set_default_color_theme(config.COLOR_THEME)
        super().__init__()
        self.title(f"{config.APP_NAME} {config.VERSION}")
        self.geometry(config.WINDOW_SIZE)
        self.minsize(820, 560)

        # Отмена доступна и после перезапуска: история последней сортировки хранится на диске.
        saved_pairs = load_history()
        self.last_result = SortResult.from_paths(saved_pairs) if saved_pairs else None
        self._build()

    def _build(self):
        self.label = ctk.CTkLabel(
            self,
            text=config.APP_NAME,
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        self.label.pack(pady=(30, 15))

        self.choose_button = ctk.CTkButton(
            self,
            text="Выбрать папку",
            command=self.choose_folder,
        )
        self.choose_button.pack(pady=10)

        self.path_field = ctk.CTkEntry(
            self,
            width=600,
            placeholder_text="Путь к папке не выбран",
        )
        self.path_field.pack(pady=10)

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=10)

        self.preview_button = ctk.CTkButton(
            self.button_frame,
            text="Предпросмотр",
            command=self.preview_files,
            state="disabled",
        )
        self.preview_button.pack(side="left", padx=5)

        self.sort_button = ctk.CTkButton(
            self.button_frame,
            text="Сортировать файлы",
            command=self.sort_files,
            state="disabled",
        )
        self.sort_button.pack(side="left", padx=5)

        self.undo_button = ctk.CTkButton(
            self.button_frame,
            text="Отменить",
            command=self.undo_files,
            state="normal" if self.last_result else "disabled",
            fg_color="#8a4b1f",
            hover_color="#6d3b18",
        )
        self.undo_button.pack(side="left", padx=5)

        self.open_button = ctk.CTkButton(
            self.button_frame,
            text="Открыть папку",
            command=self.open_folder,
            state="disabled",
            fg_color="transparent",
            border_width=1,
        )
        self.open_button.pack(side="left", padx=5)

        self.preview_box = ctk.CTkTextbox(self, width=760, height=220, activate_scrollbars=True)
        self.preview_box.pack(pady=10)
        self.preview_box.insert("1.0", "Предпросмотр появится здесь.")
        self.preview_box.configure(state="disabled")

        self.status_label = ctk.CTkLabel(self, text="", justify="left")
        self.status_label.pack(pady=10)

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Выберите папку")
        if folder:
            self.path_field.delete(0, "end")
            self.path_field.insert(0, folder)
            self.preview_button.configure(state="normal")
            self.sort_button.configure(state="normal")
            self.open_button.configure(state="normal")
            # Отмена предыдущей сортировки остаётся доступной и для другой папки.
            self.undo_button.configure(state="normal" if self.last_result else "disabled")
            self.status_label.configure(text="")
            self._set_preview("")

    def open_folder(self):
        folder = self.path_field.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning(config.APP_NAME, "Папка не найдена.")
            return
        try:
            os.startfile(folder)  # Windows-специфичный вызов: открывает Проводник
        except AttributeError:
            messagebox.showwarning(config.APP_NAME, "Открытие папки поддерживается только в Windows.")
        except OSError as exc:
            messagebox.showerror(config.APP_NAME, f"Не удалось открыть папку:\n{exc}")

    def _set_preview(self, text):
        self.preview_box.configure(state="normal")
        self.preview_box.delete("1.0", "end")
        self.preview_box.insert("1.0", text)
        self.preview_box.configure(state="disabled")

    def _read_folder(self):
        folder = self.path_field.get().strip()
        if not folder:
            messagebox.showwarning(config.APP_NAME, "Сначала выберите папку.")
            return None
        return folder

    def preview_files(self):
        folder = self._read_folder()
        if folder is None:
            return

        plan = plan_sort(folder)

        if plan.moves:
            preview = "\n".join(
                f"{os.path.basename(src)}  →  {os.path.basename(os.path.dirname(dst))}"
                for src, dst in plan.moves
            )
        else:
            preview = "Нет файлов для перемещения."

        if plan.errors:
            preview += "\n\nОшибки:\n" + "\n".join(plan.errors)

        self._set_preview(preview)
        self.status_label.configure(text=plan.summary())
        self.undo_button.configure(state="normal" if self.last_result else "disabled")

    def sort_files(self):
        folder = self._read_folder()
        if folder is None:
            return

        try:
            plan = plan_sort(folder)
            result = apply_plan(plan)
        except Exception as exc:
            messagebox.showerror(config.APP_NAME, f"Непредвиденная ошибка:\n{exc}")
            return

        self.last_result = result if result.moved_paths else None
        if self.last_result:
            save_history(result.moved_paths)
        self.undo_button.configure(state="normal" if self.last_result else "disabled")

        self._set_preview(self._result_preview(result))
        self.status_label.configure(text=result.summary())
        if result.errors:
            messagebox.showwarning(config.APP_NAME, result.summary())
        else:
            messagebox.showinfo(config.APP_NAME, result.summary())

    def _result_preview(self, result):
        if result.moved_paths:
            return "\n".join(
                f"{os.path.basename(src)}  →  {os.path.basename(os.path.dirname(dst))}"
                for src, dst in result.moved_paths
            )
        return "Нет файлов для перемещения."

    def undo_files(self):
        if not self.last_result:
            return

        try:
            undo = undo_sort(self.last_result)
        except Exception as exc:
            messagebox.showerror(config.APP_NAME, f"Непредвиденная ошибка:\n{exc}")
            return

        # Если часть файлов вернуть не удалось, отмена остаётся доступной для повтора.
        if self.last_result.moved_paths:
            save_history(self.last_result.moved_paths)
            self.undo_button.configure(state="normal")
        else:
            self.last_result = None
            clear_history()
            self.undo_button.configure(state="disabled")

        self._set_preview("")
        self.status_label.configure(text=undo.summary())
        if undo.errors:
            messagebox.showwarning(config.APP_NAME, undo.summary())
        else:
            messagebox.showinfo(config.APP_NAME, undo.summary())
