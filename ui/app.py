import customtkinter as ctk
from tkinter import filedialog, messagebox

import config
from core.organizer import sort_folder


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(config.APP_NAME)
        self.geometry(config.WINDOW_SIZE)

        self._build()

    def _build(self):
        self.label = ctk.CTkLabel(
            self,
            text=config.APP_NAME,
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        self.label.pack(pady=(40, 20))

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

        self.sort_button = ctk.CTkButton(
            self,
            text="Сортировать файлы",
            command=self.sort_files,
            state="disabled",
        )
        self.sort_button.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.pack(pady=10)

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Выберите папку")
        if folder:
            self.path_field.delete(0, "end")
            self.path_field.insert(0, folder)
            self.sort_button.configure(state="normal")
            self.status_label.configure(text="")

    def sort_files(self):
        folder = self.path_field.get().strip()
        if not folder:
            messagebox.showwarning(config.APP_NAME, "Сначала выберите папку.")
            return

        try:
            result = sort_folder(folder)
        except Exception as exc:
            messagebox.showerror(config.APP_NAME, f"Непредвиденная ошибка:\n{exc}")
            return

        self.status_label.configure(text=result.summary())
        if result.errors:
            messagebox.showwarning(config.APP_NAME, result.summary())
        else:
            messagebox.showinfo(config.APP_NAME, result.summary())


if __name__ == "__main__":
    App().mainloop()
