import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

# Ensure src/ and project root are importable
current_file = Path(__file__).resolve()
src_dir = current_file.parent
project_root = src_dir.parent

sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(project_root))

from ui.product_browser import ProductBrowser


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Data Mining Shopping Interface")
        self.geometry("950x600")
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
        container = tk.Frame(self, padx=12, pady=12)
        container.pack(fill=tk.BOTH, expand=True)

        browser = ProductBrowser(container)
        browser.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)\
            .pack(side=tk.BOTTOM, fill=tk.X)

    def _show_about(self):
        messagebox.showinfo("About", "Data Mining Shopping Interface\nCreated by Jacob")


def run_app():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    run_app()
