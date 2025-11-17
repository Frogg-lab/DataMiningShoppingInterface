import csv
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Tuple

# Optional pandas support
try:
    import pandas as pd
    pd_available = True
except ImportError:
    pd_available = False

# Preprocessing function
try:
    from preprocessing.preprocessing import clean_data
except Exception:
    clean_data = None


# ----------------------------------------------------------------------
# FIND products.csv ROBUSTLY
# ----------------------------------------------------------------------
def find_products_csv() -> Path:
    """
    Walk upward from this file until we find data/products.csv.
    Works in VS Code, PyCharm, IntelliJ, and plain terminal.
    """
    here = Path(__file__).resolve()
    for parent in [here] + list(here.parents):
        candidate = parent / "data" / "products.csv"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not locate data/products.csv")


# ----------------------------------------------------------------------
# MAIN GUI
# ----------------------------------------------------------------------
class ProductBrowser(tk.Frame):
    """Main GUI for browsing products and constructing transactions."""

    def __init__(self, parent, products_csv: Path | None = None,
                 transactions_csv: Path | None = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Locate data files
        self.products_csv = Path(products_csv) if products_csv else find_products_csv()
        self.transactions_csv = Path(transactions_csv) if transactions_csv else \
            self.products_csv.parent / "sample_transactions.csv"

        # Data containers
        self.products: List[dict] = []
        self.transactions: List[dict] = []
        self.current_transaction: List[str] = []
        self.next_transaction_id: int = 1

        # Mining stats (built from cleaned transactions)
        self.item_support: Dict[str, float] = {}
        self.pair_confidence: Dict[Tuple[str, str], float] = {}

        # UI state
        self.status_var = tk.StringVar(value="Ready")
        self.stats_var = tk.StringVar(value="Transactions: 0 | Unique items: 0")
        self.mining_method = tk.StringVar(value="eclat")  # default method

        # Load products & build UI
        self._load_products()
        self._create_widgets()

        self.new_transaction()
        self._update_stats()

    # ------------------------------------------------------------------
    # DATA LOADING
    # ------------------------------------------------------------------
    def _load_products(self):
        try:
            with open(self.products_csv, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.products = [row for row in reader]
        except Exception as e:
            messagebox.showerror("Error", f"Could not load products.csv:\n{e}")
            self.products = []

    # ------------------------------------------------------------------
    # UI CONSTRUCTION
    # ------------------------------------------------------------------
    def _create_widgets(self):
        # ----- TOP BAR -----
        top = tk.Frame(self)
        top.pack(fill=tk.X, pady=4)

        tk.Button(top, text="Import CSV", command=self.import_transactions)\
            .pack(side=tk.LEFT, padx=4)
        tk.Button(top, text="Clear All Transactions", command=self.clear_transactions)\
            .pack(side=tk.LEFT, padx=4)

        # View report button
        self.view_report_btn = tk.Button(
            top,
            text="View Report",
            command=self._view_last_report,
            state=tk.DISABLED
        )
        self.view_report_btn.pack(side=tk.LEFT, padx=6)

        # Algorithm selection
        alg_frame = tk.Frame(top)
        alg_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(alg_frame, text="Mining Method:").pack(side=tk.LEFT)
        tk.Radiobutton(alg_frame, text="Eclat",
                       variable=self.mining_method, value="eclat").pack(side=tk.LEFT)
        tk.Radiobutton(alg_frame, text="Apriori",
                       variable=self.mining_method, value="apriori").pack(side=tk.LEFT)

        tk.Label(top, textvariable=self.status_var).pack(side=tk.RIGHT, padx=6)
        tk.Label(self, textvariable=self.stats_var).pack(fill=tk.X)

        # ----- MAIN PANES -----
        main = tk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True)

        # ----- PRODUCTS LIST -----
        left = tk.LabelFrame(main, text="Products (click to add)")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)

        canvas = tk.Canvas(left, width=220, borderwidth=0, highlightthickness=0)
        scroll = tk.Scrollbar(left, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=btn_frame, anchor="nw")

        def _on_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        btn_frame.bind("<Configure>", _on_config)

        for row in self.products:
            name = row.get("product_name", "").strip()
            if not name:
                continue
            tk.Button(
                btn_frame,
                text=name,
                width=22,
                anchor="w",
                command=lambda n=name: self.add_to_current(n)
            ).pack(fill="x", pady=1)

        # ----- CURRENT TRANSACTION -----
        mid = tk.LabelFrame(main, text="Current Transaction")
        mid.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)

        self.current_var = tk.StringVar(value="(empty)")
        tk.Label(mid, textvariable=self.current_var, width=40, anchor="w",
                 wraplength=260, justify=tk.LEFT).pack(padx=6, pady=4)

        mid_btns = tk.Frame(mid)
        mid_btns.pack(pady=4)
        tk.Button(mid_btns, text="New Transaction", command=self.new_transaction)\
            .pack(side=tk.LEFT, padx=4)
        tk.Button(mid_btns, text="Finalize Transaction", command=self.finalize_transaction)\
            .pack(side=tk.LEFT, padx=4)

        # ----- RAW TRANSACTIONS -----
        right = tk.LabelFrame(main, text="Transactions (Raw)")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.raw_tree = ttk.Treeview(right, columns=("items",), show="headings", height=12)
        self.raw_tree.heading("items", text="Items")
        self.raw_tree.column("items", width=320, anchor="w")
        self.raw_tree.pack(fill=tk.BOTH, expand=True)

        # ----- PRODUCT INSIGHTS PANEL -----
        insights = tk.LabelFrame(main, text="Product Insights")
        insights.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)

        tk.Label(insights, text="Select a product:").pack(anchor="w")

        product_names = [p.get("product_name", "") for p in self.products]
        self.query_var = tk.StringVar()
        self.query_box = ttk.Combobox(
            insights,
            textvariable=self.query_var,
            values=product_names,
            state="normal"
        )
        self.query_box.pack(fill=tk.X, pady=4)

        tk.Button(insights, text="Find Associations",
                  command=self.query_associations).pack(pady=4)

        self.query_results = tk.Text(insights, height=14, wrap="word")
        self.query_results.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # TRANSACTION MANAGEMENT
    # ------------------------------------------------------------------
    def add_to_current(self, product_name: str):
        self.current_transaction.append(product_name)
        self.current_var.set(", ".join(self.current_transaction))
        self.status_var.set(f"Added {product_name}")

    def new_transaction(self):
        self.current_transaction = []
        self.current_var.set("(empty)")
        self.status_var.set("Started a new transaction")

    def _add_transaction(self, tid: int, items: List[str]):
        self.transactions.append({"transaction_id": tid, "items": items})
        display = ", ".join(items) if items else "(empty)"
        self.raw_tree.insert("", "end", iid=str(tid), values=(display,))
        if tid >= self.next_transaction_id:
            self.next_transaction_id = tid + 1

    def finalize_transaction(self):
        tid = self.next_transaction_id
        self._add_transaction(tid, list(self.current_transaction))
        self.current_transaction = []
        self.current_var.set("(empty)")
        self.status_var.set(f"Finalized transaction {tid}")
        self._update_stats()

        # Run preprocessing silently so View Report + insights are kept up to date
        self.run_preprocessing(silent=True)

    def clear_transactions(self):
        self.transactions.clear()
        self.raw_tree.delete(*self.raw_tree.get_children())
        self.next_transaction_id = 1
        self._update_stats()
        self.status_var.set("Cleared all transactions")

    # ------------------------------------------------------------------
    # IMPORT CSV
    # ------------------------------------------------------------------
    def import_transactions(self, path: Path | None = None):
        if path is None:
            path = self.transactions_csv

        loaded = 0
        try:
            if pd_available:
                df = pd.read_csv(path)
                if "transaction_id" not in df.columns or "items" not in df.columns:
                    raise ValueError("CSV must contain 'transaction_id' and 'items' columns")
                for _, row in df.iterrows():
                    items_raw = row["items"]
                    if pd.isna(items_raw) or not str(items_raw).strip():
                        continue
                    items = [s.strip() for s in str(items_raw).split(",") if s.strip()]
                    tid = int(row["transaction_id"])
                    self._add_transaction(tid, items)
                    loaded += 1
            else:
                with open(path, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        items_raw = row.get("items", "")
                        if not str(items_raw).strip():
                            continue
                        items = [s.strip() for s in str(items_raw).split(",") if s.strip()]
                        tid = int(row.get("transaction_id", self.next_transaction_id))
                        self._add_transaction(tid, items)
                        loaded += 1

            self.status_var.set(f"Imported {loaded} transactions")
            self._update_stats()
            self.run_preprocessing(silent=True)

        except Exception as e:
            messagebox.showerror("Import Failed", f"Could not import CSV:\n{e}")

    # ------------------------------------------------------------------
    # STATS
    # ------------------------------------------------------------------
    def _update_stats(self):
        unique_items = {i.lower() for t in self.transactions for i in t["items"]}
        self.stats_var.set(
            f"Transactions: {len(self.transactions)} | Unique items: {len(unique_items)}"
        )

    # ------------------------------------------------------------------
    # PREPROCESSING + ASSOCIATION STATS
    # ------------------------------------------------------------------
    def run_preprocessing(self, silent: bool = False):
        if clean_data is None:
            if not silent:
                messagebox.showerror("Unavailable", "Preprocessing module missing.")
            return

        if not self.transactions:
            if not silent:
                messagebox.showinfo("Preprocessing", "No transactions to preprocess.")
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
        except Exception as e:
            if not silent:
                messagebox.showerror("Error", f"Preprocessing failed:\n{e}")
            return

        self.last_cleaned = cleaned
        self.last_report = report
        self.view_report_btn.config(state=tk.NORMAL)

        # Build pairwise association stats for query tool
        self._build_association_stats(cleaned)

        if not silent:
            self._open_preprocessing_report(cleaned, report)

    def _build_association_stats(self, cleaned_df: "pd.DataFrame"):
        """
        From cleaned transactions, compute:
        - item_support[item] = support in [0,1]
        - pair_confidence[(a,b)] = P(b|a)
        """
        item_counts: Dict[str, int] = {}
        pair_counts: Dict[Tuple[str, str], int] = {}

        # Count supports
        for _, row in cleaned_df.iterrows():
            items = row.get("items", [])
            if not isinstance(items, list):
                continue
            # Deduplicate within transaction just in case
            unique_items = list(dict.fromkeys([str(i).lower() for i in items]))
            for a in unique_items:
                item_counts[a] = item_counts.get(a, 0) + 1
            # Ordered pairs for confidence
            for i in range(len(unique_items)):
                for j in range(len(unique_items)):
                    if i == j:
                        continue
                    a = unique_items[i]
                    b = unique_items[j]
                    pair_counts[(a, b)] = pair_counts.get((a, b), 0) + 1

        n_tx = int(cleaned_df.shape[0]) or 1

        self.item_support = {item: cnt / n_tx for item, cnt in item_counts.items()}
        self.pair_confidence = {}
        for (a, b), cnt in pair_counts.items():
            base = item_counts.get(a, 1)
            self.pair_confidence[(a, b)] = cnt / base

    # ------------------------------------------------------------------
    # VIEW REPORT
    # ------------------------------------------------------------------
    def _view_last_report(self):
        if not hasattr(self, "last_report"):
            messagebox.showinfo("Report", "No preprocessing report available yet.")
            return

        try:
            self._open_preprocessing_report(self.last_cleaned, self.last_report)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open report:\n{e}")

    def _open_preprocessing_report(self, cleaned_df, report: dict):
        win = tk.Toplevel(self)
        win.title("Preprocessing Report")
        win.geometry("900x600")

        # Summary text
        summary = tk.Text(win, height=14, wrap="word")
        summary.pack(fill=tk.X, padx=10, pady=10)

        txt = (
            "PREPROCESSING REPORT\n"
            "-------------------------------------\n"
            f"Original transactions: {report.get('original_total')}\n"
            f"Blank removed: {report.get('blank_removed')}\n"
            f"Empty removed: {report.get('empty_transactions')}\n"
            f"Single-item removed: {report.get('single_item_removed')}\n"
            f"Invalid transactions: {report.get('invalid_item_transactions')}\n"
            f"Duplicates removed: {report.get('duplicates_removed')}\n\n"
            f"Valid transactions: {report.get('valid_transactions')}\n"
            f"Total items: {report.get('total_items')}\n"
            f"Unique items: {report.get('unique_items')}\n\n"
            "MEMORY USAGE\n"
            f"Peak: {report.get('memory_peak_tracemalloc_bytes')} bytes\n"
            f"Current: {report.get('memory_current_tracemalloc_bytes')} bytes\n"
            f"RSS Before: {report.get('memory_rss_before_bytes')}\n"
            f"RSS After: {report.get('memory_rss_after_bytes')}\n"
            f"RSS Delta: {report.get('memory_rss_delta_bytes')}\n"
        )

        summary.insert("1.0", txt)
        summary.config(state="disabled")

        # Cleaned data table
        table_frame = tk.Frame(win)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tree = ttk.Treeview(table_frame, columns=("tid", "items"), show="headings")
        tree.heading("tid", text="Transaction ID")
        tree.heading("items", text="Items")
        tree.column("tid", width=120, anchor="center")
        tree.column("items", width=650, anchor="w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        for _, row in cleaned_df.iterrows():
            tid = row.get("transaction_id")
            items = row.get("items")
            if isinstance(items, list):
                items = ", ".join(items)
            tree.insert("", "end", values=(tid, items))

    # ------------------------------------------------------------------
    # INTERACTIVE QUERY
    # ------------------------------------------------------------------
    def query_associations(self):
        product = self.query_var.get().strip().lower()
        if not product:
            messagebox.showinfo("Query", "Please select a product.")
            return

        if not self.pair_confidence:
            self.query_results.delete("1.0", tk.END)
            self.query_results.insert(
                "1.0",
                "No association data yet.\n"
                "Build and finalize some transactions first."
            )
            return

        associations = self._get_associations_for(product)

        self.query_results.delete("1.0", tk.END)

        if not associations:
            self.query_results.insert(
                "1.0",
                f"No strong associations found for '{product}'."
            )
            return

        method = self.mining_method.get().capitalize()
        result_text = (
            f"{method} Associations for '{product}':\n\n"
        )
        for item, pct in associations:
            result_text += f" • {item} — {pct:.1f}%\n"

        best_item, best_pct = associations[0]
        result_text += (
            "\nBusiness Recommendation:\n"
            f"Customers who buy **{product}** also often buy **{best_item}** "
            f"({best_pct:.1f}%).\n"
            f"Consider placing **{product}** near **{best_item}** in the store."
        )

        self.query_results.insert("1.0", result_text)

    def _get_associations_for(self, product: str, min_conf: float = 0.05):
        """
        Return a list of (other_item, confidence_percent) for the given product,
        sorted by confidence descending.
        """
        scores: Dict[str, float] = {}
        for (a, b), conf in self.pair_confidence.items():
            if a == product and conf >= min_conf:
                scores[b] = max(scores.get(b, 0.0), conf)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [(item, conf * 100.0) for item, conf in ranked]
