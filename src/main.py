#USED CHATGPT TO GENERATE STANDARD TKINTER WINDOW
import tkinter as tk
from tkinter import messagebox


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Data Mining Shopping Interface — Demo Window")
        self.geometry("640x360")
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

        label = tk.Label(frame, text="Welcome to the Data Mining Shopping Interface demo!", font=(None, 14))
        label.pack(pady=(0, 12))

        btn = tk.Button(frame, text="Click me", command=self._on_click)
        btn.pack()

        # Status bar at bottom
        self.status_var = tk.StringVar(value="Ready")
        status = tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status.pack(side=tk.BOTTOM, fill=tk.X)

    def _on_click(self):
        self.status_var.set("Button clicked — showing message")
        messagebox.showinfo("Hello", "This is a standard Tkinter window example.")
        self.status_var.set("Ready")

    def _show_about(self):
        messagebox.showinfo("About", "Data Mining Shopping Interface\nTkinter demo window")


def run_app():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    run_app()
