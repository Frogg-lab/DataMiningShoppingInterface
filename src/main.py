#USED CHATGPT TO GENERATE STANDARD TKINTER WINDOW
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

# Add src directory to path so we can import from it
sys.path.insert(0, str(Path(__file__).parent))

from ui.product_browser import ProductBrowser


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Data Mining Shopping Interface")
        self.geometry("800x560")
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
        # Main content frame
        frame = tk.Frame(self, padx=12, pady=12)
        frame.pack(fill=tk.BOTH, expand=True)

        # Embed the modular ProductBrowser frame
        browser = ProductBrowser(frame)
        browser.pack(fill=tk.BOTH, expand=True)

        # Status bar at bottom
        self.status_var = tk.StringVar(value="Ready")
        status = tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status.pack(side=tk.BOTTOM, fill=tk.X)

    def _show_about(self):
        messagebox.showinfo("About", "Data Mining Shopping Interface\nProduct browser demo window")


def run_app():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    run_app()
