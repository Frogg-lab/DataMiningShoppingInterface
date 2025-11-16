import csv
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


class ProductBrowser(tk.Frame):
    """A self-contained product browser frame.

    - Loads products from data/products.csv (relative to project root)
    - Shows category filter, search box, product combobox and a cart listbox
    - Methods are instance methods to avoid global variables and name collisions
    """

    def __init__(self, parent, products_csv: Path | str = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Default path: project_root/data/products.csv
        if products_csv is None:
            products_csv = Path(__file__).resolve().parents[2] / "data" / "products.csv"
        self.products_csv = Path(products_csv)

        self.products = []
        self._load_products()

        # derived lists
        self.all_product_names = [p["product_name"] for p in self.products] if self.products else []
        self.all_categories = sorted(list({p["category"] for p in self.products})) if self.products else []

        # ui state
        self.category_var = tk.StringVar(value="All")
        self.search_var = tk.StringVar(value="")
        self.product_var = tk.StringVar(value="")

        self._create_widgets()
        self.update_product_dropdown()

    def _load_products(self):
        try:
            with open(self.products_csv, newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                self.products = [row for row in reader]
        except FileNotFoundError:
            messagebox.showwarning(
                "Products file missing",
                f"Could not find products.csv at: {self.products_csv}\n\nProduct list will be empty.",
            )
            self.products = []

    def _create_widgets(self):
        # Category label + combobox
        lbl = tk.Label(self, text="Filter by Category:", font=(None, 12))
        lbl.pack(pady=5, anchor="w")

        self.category_dropdown = ttk.Combobox(
            self,
            textvariable=self.category_var,
            values=["All"] + self.all_categories,
            state="readonly",
            width=30,
        )
        self.category_dropdown.pack(pady=2, anchor="w")
        self.category_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_product_dropdown())

        # Search
        tk.Label(self, text="Search:", font=(None, 12)).pack(pady=5, anchor="w")
        search_entry = tk.Entry(self, textvariable=self.search_var, width=33)
        search_entry.pack(pady=2, anchor="w")
        search_entry.bind("<KeyRelease>", lambda e: self.update_product_dropdown())

        # Product dropdown
        tk.Label(self, text="Select Product:", font=(None, 12)).pack(pady=5, anchor="w")
        self.product_dropdown = ttk.Combobox(
            self,
            textvariable=self.product_var,
            values=self.all_product_names,
            state="readonly",
            width=30,
        )
        self.product_dropdown.pack(pady=2, anchor="w")
        if self.all_product_names:
            self.product_var.set(self.all_product_names[0])

        # Cart listbox
        tk.Label(self, text="Your Cart:", font=(None, 14)).pack(pady=10, anchor="w")
        self.cart_listbox = tk.Listbox(self, width=40, height=10)
        self.cart_listbox.pack(pady=2)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=6)

        tk.Button(btn_frame, text="Add to Cart", command=self.add_to_cart, width=15).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Remove Selected", command=self.remove_selected, width=15).pack(side="left", padx=4)
        # Checkout button shows a list of all items currently in the cart
        tk.Button(btn_frame, text="Checkout", command=self.checkout, width=12).pack(side="left", padx=6)

    def update_product_dropdown(self):
        """Updates dropdown based on category + search text."""
        search_text = self.search_var.get().lower()
        category = self.category_var.get()

        filtered = []

        for p in self.products:
            name = p["product_name"].lower()

            # Filter by category (if not All)
            if category != "All" and p.get("category") != category:
                continue

            # Filter by search text
            if search_text and search_text not in name:
                continue

            filtered.append(p["product_name"])

        # Update dropdown options
        self.product_dropdown["values"] = filtered

        # Auto-select first item (optional)
        if filtered:
            self.product_var.set(filtered[0])
        else:
            self.product_var.set("")

    def add_to_cart(self):
        item = self.product_var.get()
        if item:
            self.cart_listbox.insert(tk.END, item)

    def remove_selected(self):
        selection = self.cart_listbox.curselection()
        for idx in reversed(selection):
            self.cart_listbox.delete(idx)

    def get_cart_items(self):
        return list(self.cart_listbox.get(0, tk.END))

    def checkout(self):
        """Display the items currently in the cart to the user.

        Simple implementation: show a messagebox with each item on a new line.
        """
        items = self.get_cart_items()
        if not items:
            messagebox.showinfo("Checkout", "Your cart is empty.")
            return

        # Format the items list for display
        body = "Items in your cart:\n\n" + "\n".join(items)
        # If the list is long, messagebox may not be ideal; this is a simple implementation
        messagebox.showinfo("Checkout", body)
