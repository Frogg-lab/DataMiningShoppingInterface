import csv
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List

try:
    import pandas as pd
    pd_available = True
except ImportError:
    pd_available = False

try:
    from preprocessing.preprocessing import clean_data
except Exception:
    clean_data = None


# Auto-detect products.csv
def find_products_csv():
    here = Path(__file__).resolve()
    for parent in [here] + list(here.parents):
        candidate = parent / "data" / "products.csv"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not find data/products.csv")


class ProductBrowser(tk.Frame):
    """Product browser GUI"""
    def __init__(self, parent, products_csv=None, transactions_csv=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Locate products CSV
        self.products_csv = Path(products_csv) if products_csv else find_products_csv()
        self.transactions_csv = self.products_csv.parent / "sample_transactions.csv"

        self.products: List[dict] = []
        self.transactions: List[dict] = []
        self.current_transaction: List[str] = []
        self.next_transaction_id = 1

        self.status_var = tk.StringVar(value="Ready")
        self.stats_var = tk.StringVar(value="Transactions: 0 | Unique items: 0")

        self._load_products()
        self._create_widgets()

        self.new_transaction()
        self._update_stats()

    # Load products list
    def _load_products(self):
        try:
            with open(self.products_csv, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.products = [row for row in reader]
        except Exception as e:
            messagebox.showerror("Error", f"Could not load products.csv:\n{e}")
            self.products = []

    # Build UI
    def _create_widgets(self):
        top = tk.Frame(self)
        top.pack(fill=tk.X, pady=4)

        tk.Button(top, text="Import CSV", command=self.import_transactions).pack(side=tk.LEFT, padx=4)
        tk.Button(top, text="Clear All Transactions", command=self.clear_transactions).pack(side=tk.LEFT, padx=4)

        # View Report button starts disabled
        self.view_report_btn = tk.Button(
            top,
            text="View Report",
            command=self._view_last_report,
            state=tk.DISABLED
        )
        self.view_report_btn.pack(side=tk.LEFT, padx=6)

        tk.Label(top, textvariable=self.status_var).pack(side=tk.RIGHT, padx=6)
        tk.Label(self, textvariable=self.stats_var).pack(fill=tk.X)

        main = tk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True)

        # Product list
        left = tk.LabelFrame(main, text="Products (click to add)")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)

        canvas = tk.Canvas(left, width=240)
        scrollbar = tk.Scrollbar(left, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        buttons_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=buttons_frame, anchor="nw")

        buttons_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        for row in self.products:
            name = row.get("product_name", "")
            tk.Button(
                buttons_frame,
                text=name,
                width=25,
                anchor="w",
                command=lambda n=name: self.add_to_current(n)
            ).pack(fill="x", pady=2)

        # Current transaction
        mid = tk.LabelFrame(main, text="Current Transaction")
        mid.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)

        self.current_var = tk.StringVar(value="(empty)")
        tk.Label(mid, textvariable=self.current_var, width=40).pack(padx=6, pady=4)

        bt = tk.Frame(mid)
        bt.pack(pady=4)
        tk.Button(bt, text="New Transaction", command=self.new_transaction).pack(side=tk.LEFT, padx=4)
        tk.Button(bt, text="Finalize Transaction", command=self.finalize_transaction).pack(side=tk.LEFT, padx=4)

        # Raw transactions
        right = tk.LabelFrame(main, text="Transactions (Raw)")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.raw_tree = ttk.Treeview(right, columns=("items",), show="headings", height=12)
        self.raw_tree.heading("items", text="Items")
        self.raw_tree.pack(fill=tk.BOTH, expand=True)

    # Transaction functions
    def add_to_current(self, product_name):
        self.current_transaction.append(product_name)
        self.current_var.set(", ".join(self.current_transaction))
        self.status_var.set(f"Added {product_name}")

    def new_transaction(self):
        self.current_transaction = []
        self.current_var.set("(empty)")
        self.status_var.set("Started new transaction")

    def _add_transaction(self, tid, items):
        self.transactions.append({"transaction_id": tid, "items": items})
        self.raw_tree.insert("", "end", iid=str(tid), values=(", ".join(items) if items else "(empty)",))
        if tid >= self.next_transaction_id:
            self.next_transaction_id = tid + 1

    def finalize_transaction(self):
        tid = self.next_transaction_id
        self._add_transaction(tid, list(self.current_transaction))
        self.current_transaction.clear()
        self.current_var.set("(empty)")
        self.status_var.set(f"Finalized transaction {tid}")
        self._update_stats()

        # RUN PREPROCESSING AFTER EACH TRANSACTION
        self.run_preprocessing(silent=True)

    def clear_transactions(self):
        self.transactions.clear()
        self.raw_tree.delete(*self.raw_tree.get_children())
        self.next_transaction_id = 1
        self._update_stats()
        self.status_var.set("Cleared all transactions")

    # Import CSV
    def import_transactions(self, path=None):
        path = path or self.transactions_csv

        try:
            df = pd.read_csv(path)
            for _, row in df.iterrows():
                items = [s.strip() for s in str(row["items"]).split(",") if s.strip()]
                tid = int(row["transaction_id"])
                self._add_transaction(tid, items)
            self.status_var.set("Imported transactions")
            self._update_stats()
        except Exception as e:
            messagebox.showerror("Error", f"Could not import CSV:\n{e}")

    # Stats
    def _update_stats(self):
        unique_items = {i.lower() for t in self.transactions for i in t["items"]}
        self.stats_var.set(f"Transactions: {len(self.transactions)} | Unique items: {len(unique_items)}")

    # Preprocessing
    def run_preprocessing(self, silent=False):
        if clean_data is None:
            return

        if not self.transactions:
            return

        df = pd.DataFrame([
            {
                "transaction_id": t["transaction_id"],
                "items": ",".join(t["items"]) if t["items"] else "(empty)"
            }
            for t in self.transactions
        ])

        try:
            cleaned, report = clean_data(df, return_report=True)
        except Exception:
            return

        self.last_cleaned = cleaned
        self.last_report = report
        self.view_report_btn.config(state=tk.NORMAL)

    def _view_last_report(self):
        if not hasattr(self, "last_report"):
            messagebox.showinfo("No Report", "Run preprocessing first!")
            return

        self._open_preprocessing_report(self.last_cleaned, self.last_report)

    def _open_preprocessing_report(self, cleaned_df, report):
        win = tk.Toplevel(self)
        win.title("Preprocessing Report")
        win.geometry("900x600")

        summary = tk.Text(win, height=14)
        summary.pack(fill=tk.X, padx=10, pady=10)

        summary.insert("1.0", f"""
PREPROCESSING REPORT
-------------------------------
Original transactions: {report['original_total']}
Blank removed: {report['blank_removed']}
Empty removed: {report['empty_transactions']}
Single-item removed: {report['single_item_removed']}
Invalid transactions: {report['invalid_item_transactions']}
Duplicates removed: {report['duplicates_removed']}

Valid transactions: {report['valid_transactions']}
Total items: {report['total_items']}
Unique items: {report['unique_items']}

Memory Peak: {report['memory_peak_tracemalloc_bytes']}
Memory Current: {report['memory_current_tracemalloc_bytes']}
RSS Before: {report['memory_rss_before_bytes']}
RSS After: {report['memory_rss_after_bytes']}
RSS Delta: {report['memory_rss_delta_bytes']}
""")
        summary.config(state="disabled")

        table_frame = tk.Frame(win)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tree = ttk.Treeview(table_frame, columns=("tid", "items"), show="headings")
        tree.heading("tid", text="Transaction ID")
        tree.heading("items", text="Items")

        tree.pack(fill=tk.BOTH, expand=True)

        for _, row in cleaned_df.iterrows():
            items = row["items"]
            if isinstance(items, list):
                items = ", ".join(items)
            tree.insert("", "end", values=(row["transaction_id"], items))
