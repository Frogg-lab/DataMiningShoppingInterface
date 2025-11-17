import csv
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from typing import List

# pandas is optional; if not installed we'll fall back to csv parsing and disable preprocessing
pd_available = True
try:
    import pandas as pd
except Exception:
    pd_available = False

# import preprocessing function
try:
    from preprocessing.preprocessing import clean_data
except Exception:
    # best-effort fallback; if import fails we'll disable preprocess button
    clean_data = None


class ProductBrowser(tk.Frame):
    """A product browser and transaction manager.

    Features added:
    - Manual transaction creation via clickable product buttons
    - Transaction list display (before and after preprocessing)
    - CSV import for sample_transactions.csv
    - Basic statistics and status messages
    """

    def __init__(self, parent, products_csv: Path | str = None, transactions_csv: Path | str = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Default paths
        root = Path(__file__).resolve().parents[2]
        if products_csv is None:
            products_csv = root / "data" / "products.csv"
        if transactions_csv is None:
            transactions_csv = root / "data" / "sample_transactions.csv"

        self.products_csv = Path(products_csv)
        self.transactions_csv = Path(transactions_csv)

        # loaded products and transactions
        self.products: List[dict] = []
        self._load_products()

        # UI state
        self.current_transaction: List[str] = []
        self.transactions: List[dict] = []  # each dict: {'transaction_id': int, 'items': list}
        self.next_transaction_id = 1

        # widgets we'll reference
        self.status_var = tk.StringVar(value="Ready")
        self.stats_var = tk.StringVar(value="Transactions: 0 | Unique items: 0")

        self._create_widgets()

    def _load_products(self):
        try:
            with open(self.products_csv, newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                self.products = [row for row in reader]
        except FileNotFoundError:
            messagebox.showwarning("Products file missing", f"Could not find products.csv at: {self.products_csv}\nProduct list will be empty.")
            self.products = []

    def _create_widgets(self):
        # Top: status and controls
        top_frame = tk.Frame(self)
        top_frame.pack(fill=tk.X, pady=4)

        import_btn = tk.Button(top_frame, text="Import CSV", command=self.import_transactions)
        import_btn.pack(side=tk.LEFT, padx=4)

        preprocess_btn = tk.Button(top_frame, text="Preprocess", command=self.run_preprocessing)
        preprocess_btn.pack(side=tk.LEFT, padx=4)
        if clean_data is None:
            preprocess_btn.config(state=tk.DISABLED)

        clear_btn = tk.Button(top_frame, text="Clear All Transactions", command=self.clear_transactions)
        clear_btn.pack(side=tk.LEFT, padx=8)

    # (removed) Show Last Report button

        status_label = tk.Label(top_frame, textvariable=self.status_var, anchor="w")
        status_label.pack(side=tk.RIGHT, padx=6)

        stats_label = tk.Label(self, textvariable=self.stats_var)
        stats_label.pack(fill=tk.X)

        # Main content: left product palette, right transaction views
        main = tk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, pady=6)

        # Left: product buttons (click to add to current transaction)
        left = tk.LabelFrame(main, text="Products (click to add)")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)

        # show at least 10 distinct products (or all if fewer)
        product_names = [p.get("product_name", "") for p in self.products]
        product_names = [n for n in product_names if n]
        display_names = product_names[:max(10, len(product_names))]

        # Scrollable area: canvas + inner frame + vertical scrollbar.
        canvas = tk.Canvas(left, borderwidth=0, highlightthickness=0, width=240)
        vscroll = tk.Scrollbar(left, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        buttons_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=buttons_frame, anchor="nw")

        def _on_frame_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        buttons_frame.bind("<Configure>", _on_frame_config)

        # Mouse-wheel support: enable when cursor is over the canvas
        def _on_mousewheel(event):
            # Windows: event.delta is multiple of 120
            delta = int(-1 * (event.delta / 120)) if event.delta else 0
            canvas.yview_scroll(delta, "units")

        def _bind_mousewheel(_):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(_):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)

        # populate buttons inside buttons_frame
        for i, name in enumerate(display_names):
            btn = tk.Button(buttons_frame, text=name, width=30, anchor="w", command=lambda n=name: self.add_to_current(n))
            btn.pack(fill="x", pady=2, padx=2)

        # Current transaction box and controls
        cur_frame = tk.LabelFrame(main, text="Current Transaction")
        cur_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=6, pady=6)

        self.current_var = tk.StringVar(value="(empty)")
        tk.Label(cur_frame, textvariable=self.current_var, width=40, anchor="w", justify=tk.LEFT, wraplength=300).pack(padx=6, pady=6)

        cur_btns = tk.Frame(cur_frame)
        cur_btns.pack(pady=4)
        tk.Button(cur_btns, text="New Transaction", command=self.new_transaction).pack(side=tk.LEFT, padx=4)
        tk.Button(cur_btns, text="Finalize Transaction", command=self.finalize_transaction).pack(side=tk.LEFT, padx=4)

        # Right: transactions lists (before and after preprocessing)
        right = tk.Frame(main)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6)

        # Raw transactions
        raw_frame = tk.LabelFrame(right, text="Transactions (Raw)")
        raw_frame.pack(fill=tk.BOTH, expand=True, pady=6)
        self.raw_tree = ttk.Treeview(raw_frame, columns=("items",), show="headings", height=8)
        self.raw_tree.heading("items", text="Items")
        self.raw_tree.pack(fill=tk.BOTH, expand=True)

    # (removed) Preprocessed transactions view

        # initial state
        self.new_transaction()
        self._update_stats()

    # ---- Transaction management ----
    def add_to_current(self, product_name: str):
        self.current_transaction.append(product_name)
        self.current_var.set(", ".join(self.current_transaction))
        self.status_var.set(f"Added '{product_name}' to current transaction")

    def new_transaction(self):
        self.current_transaction = []
        self.current_var.set("(empty)")
        self.status_var.set("Started a new transaction")

    def finalize_transaction(self):
        if not self.current_transaction:
            self.status_var.set("Cannot finalize empty transaction")
            return
        tid = self.next_transaction_id
        self.next_transaction_id += 1
        self.transactions.append({"transaction_id": tid, "items": list(self.current_transaction)})
        # add to raw tree
        self.raw_tree.insert("", "end", iid=str(tid), values=(", ".join(self.current_transaction),))
        self.current_transaction = []
        self.current_var.set("(empty)")
        self.status_var.set(f"Finalized transaction {tid}")
        self._update_stats()

    def clear_transactions(self):
        self.transactions = []
        self.raw_tree.delete(*self.raw_tree.get_children())
        self.next_transaction_id = 1
        self.status_var.set("Cleared all transactions")
        self._update_stats()

    # ---- CSV import ----
    def import_transactions(self, path: Path | str = None):
        if path is None:
            path = self.transactions_csv
        loaded = 0
        if pd_available:
            try:
                df = pd.read_csv(path)
            except Exception as e:
                messagebox.showerror("Import Failed", f"Failed to read CSV: {e}")
                self.status_var.set("Import failed")
                return

            # expect columns transaction_id and items
            if "transaction_id" not in df.columns or "items" not in df.columns:
                messagebox.showerror("Invalid Format", "CSV must contain 'transaction_id' and 'items' columns")
                self.status_var.set("Import failed: invalid format")
                return

            for _, row in df.iterrows():
                try:
                    items_raw = row["items"]
                    if pd.isna(items_raw) or str(items_raw).strip() == "":
                        # skip empty transaction
                        continue
                    items = [i.strip() for i in str(items_raw).split(",") if i.strip()]
                    tid = int(row["transaction_id"]) if not pd.isna(row["transaction_id"]) else self.next_transaction_id
                    self.transactions.append({"transaction_id": tid, "items": items})
                    self.raw_tree.insert("", "end", iid=str(tid), values=(", ".join(items),))
                    loaded += 1
                    if tid >= self.next_transaction_id:
                        self.next_transaction_id = tid + 1
                except Exception:
                    # skip malformed row but continue
                    continue
        else:
            # Fallback CSV parsing without pandas
            try:
                with open(path, newline="", encoding="utf-8") as fh:
                    reader = csv.DictReader(fh)
                    for row in reader:
                        try:
                            items_raw = row.get("items", "")
                            if items_raw is None or str(items_raw).strip() == "":
                                continue
                            items = [i.strip() for i in str(items_raw).split(",") if i.strip()]
                            tid_raw = row.get("transaction_id", "")
                            tid = int(tid_raw) if str(tid_raw).strip().isdigit() else self.next_transaction_id
                            self.transactions.append({"transaction_id": tid, "items": items})
                            self.raw_tree.insert("", "end", iid=str(tid), values=(", ".join(items),))
                            loaded += 1
                            if tid >= self.next_transaction_id:
                                self.next_transaction_id = tid + 1
                        except Exception:
                            continue
            except Exception as e:
                messagebox.showerror("Import Failed", f"Failed to read CSV: {e}")
                self.status_var.set("Import failed")
                return

        self.status_var.set(f"Imported {loaded} transactions from {Path(path).name}")
        self._update_stats()

    # ---- Preprocessing integration ----
    def run_preprocessing(self):
        if clean_data is None:
            messagebox.showwarning("Unavailable", "Preprocessing module not available")
            return

        # build a dataframe like preprocessing expects
        df = pd.DataFrame([{"transaction_id": t["transaction_id"], "items": ",".join(t["items"])} for t in self.transactions])
        try:
            result = clean_data(df.copy(), return_report=True)
            if isinstance(result, tuple):
                cleaned, report = result
            else:
                cleaned = result
                report = None
        except Exception as e:
            messagebox.showerror("Preprocess Error", f"Preprocessing failed: {e}")
            self.status_var.set("Preprocessing failed")
            return

        if report:
            # concise status
            self.status_var.set(f"Preprocessing complete: {report['valid_transactions']} valid transactions")

            # formatted report similar to example
            report_text = (
                f"Preprocessing Report:\n"
                f"-------------------\n"
                f"Before Cleaning:\n"
                f"- Total transactions: {report.get('original_total', 0)}\n"
                f"- Empty transactions: {report.get('blank_removed', 0)}\n"
                f"- Single-item transactions: {report.get('single_item_removed', 0)}\n"
                f"- Duplicate items found: {report.get('duplicates_removed', 0)} instances\n"
                f"- Invalid items found: {report.get('invalid_item_transactions', 0)} instances\n"
                f"After Cleaning:\n"
                f"- Valid transactions: {report.get('valid_transactions', 0)}\n"
                f"- Total items: {report.get('total_items', 0)}\n"
                f"- Unique products: {report.get('unique_items', 0)}"
            )
            # show detailed report to user
            try:
                messagebox.showinfo("Preprocessing Report", report_text)
            except Exception:
                # fallback: set status to include numbers if messagebox fails
                self.status_var.set(self.status_var.get() + " (report available)")
        else:
            self.status_var.set(f"Preprocessing complete: {cleaned.shape[0]} valid transactions")
        self._update_stats()

    # ---- Stats ----
    def _update_stats(self):
        tx_count = len(self.transactions)
        unique_items = set()
        for t in self.transactions:
            for i in t["items"]:
                unique_items.add(i.lower())
        self.stats_var.set(f"Transactions: {tx_count} | Unique items: {len(unique_items)}")

    # convenience for tests
    def get_transactions(self):
        return list(self.transactions)

    def show_last_report(self):
        # (removed) show_last_report: button and persistent report removed per user request
        messagebox.showinfo("Preprocessing Report", "This feature has been removed. Run 'Preprocess' to view the latest report.")
