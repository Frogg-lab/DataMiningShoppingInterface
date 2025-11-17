import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

# Make sure src/ and project root are on sys.path
current_file = Path(__file__).resolve()
src_dir = current_file.parent         # .../src
project_root = src_dir.parent         # repo root

sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(project_root))

from ui.product_browser import ProductBrowser


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Data Mining Shopping Interface")
        self.geometry("1100x650")
        self._create_widgets()
        self._create_menu()

    def _create_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

    def _create_widgets(self):
        frame = tk.Frame(self, padx=12, pady=12)
        frame.pack(fill=tk.BOTH, expand=True)

        browser = ProductBrowser(frame)
        browser.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="Ready")
        status = tk.Label(
            self,
            textvariable=self.status_var,
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status.pack(side=tk.BOTTOM, fill=tk.X)

    def _show_about(self):
        messagebox.showinfo(
            "About",
            "Data Mining Shopping Interface\n"
            "Browse products, build transactions, "
            "run preprocessing, and explore associations."
        )


def run_app():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    run_app()
