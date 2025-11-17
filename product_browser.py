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

        clear_btn = tk.Button(top_frame, text="Clear All Transactions", command=self.clear_transactions)
        clear_btn.pack(side=tk.LEFT, padx=8)

        # View report button (disabled until a preprocess run produces a report)
        self.view_report_btn = tk.Button(top_frame, text="View Report", command=self._view_last_report)
        self.view_report_btn.pack(side=tk.LEFT, padx=4)
        self.view_report_btn.config(state=tk.DISABLED)

    # (removed) Show Last Report button

        status_label = tk.Label(top_frame, textvariable=self.status_var, anchor="w")
        status_label.pack(side=tk.RIGHT, padx=6)

        stats_label = tk.Label(self, textvariable=self.stats_var)
        stats_label.pack(fill=tk.X)

    # (recommendation UI removed)

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
        # Allow empty transactions — preprocessing will detect and report them
        tid = self.next_transaction_id
        self.next_transaction_id += 1
        self.transactions.append({"transaction_id": tid, "items": list(self.current_transaction)})
        # add to raw tree
        self.raw_tree.insert("", "end", iid=str(tid), values=(", ".join(self.current_transaction) if self.current_transaction else "(empty)",))
        self.current_transaction = []
        self.current_var.set("(empty)")
        self.status_var.set(f"Finalized transaction {tid}")
        self._update_stats()
        # run a silent preprocessing update so the View Report becomes available without popup
        if clean_data is not None:
            try:
                self.run_preprocessing(silent=True)
            except Exception:
                # don't block finalize on preprocessing errors
                pass
        else:
            # If preprocessing isn't available (missing pandas/import), synthesize a minimal report
            try:
                cleaned = []
                for t in self.transactions:
                    cleaned.append({
                        "transaction_id": t.get("transaction_id"),
                        "items": list(t.get("items", [])),
                    })
                report = {
                    'original_total': len(self.transactions),
                    'blank_removed': 0,
                    'single_item_removed': 0,
                    'invalid_item_transactions': 0,
                    'duplicates_removed': 0,
                    'valid_transactions': len(self.transactions),
                    'total_items': sum(len(t['items']) for t in cleaned),
                    'unique_items': len({it for t in cleaned for it in t['items']}),
                }
                self.last_report = report
                self.last_cleaned = cleaned
                try:
                    self.view_report_btn.config(state=tk.NORMAL)
                except Exception:
                    pass
            except Exception:
                pass

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
    def run_preprocessing(self, silent: bool = False):
        if clean_data is None:
            if not silent:
                messagebox.showwarning("Unavailable", "Preprocessing module not available")
            return

        # build a dataframe like preprocessing expects
        # mark empty transactions as "(empty)" so preprocessing can detect them
        df = pd.DataFrame([{
            "transaction_id": t["transaction_id"], 
            "items": "(empty)" if not t["items"] else ",".join(t["items"])
        } for t in self.transactions])
        try:
            result = clean_data(df.copy(), return_report=True)
            if isinstance(result, tuple):
                cleaned, report = result
            else:
                cleaned = result
                report = None
        except Exception as e:
            # on silent mode, don't show a blocking dialog
            if not silent:
                messagebox.showerror("Preprocess Error", f"Preprocessing failed: {e}")
            self.status_var.set("Preprocessing failed")
            return

        # If clean_data returned a report use it, otherwise synthesize a minimal report
        if report is None:
            try:
                original_total = int(df.shape[0])
            except Exception:
                original_total = 0
            try:
                valid_transactions = int(getattr(cleaned, 'shape', (0,))[0])
            except Exception:
                valid_transactions = 0

            # count items and unique items from cleaned
            total_items = 0
            unique_items = set()
            try:
                for _, row in cleaned.iterrows():
                    items = row.get('items', [])
                    if isinstance(items, (list, tuple)):
                        for it in items:
                            total_items += 1
                            unique_items.add(str(it))
            except Exception:
                pass

            report = {
                'original_total': original_total,
                'blank_removed': max(0, original_total - valid_transactions),
                'single_item_removed': 0,
                'invalid_item_transactions': 0,
                'duplicates_removed': 0,
                'valid_transactions': valid_transactions,
                'total_items': int(total_items),
                'unique_items': int(len(unique_items)),
            }

        # concise status
        try:
            self.status_var.set(f"Preprocessing complete: {report.get('valid_transactions', 0)} valid transactions")
        except Exception:
            self.status_var.set("Preprocessing complete")

        # store last report and cleaned data so the UI can reopen it later
        try:
            self.last_report = report
            self.last_cleaned = cleaned
            self.view_report_btn.config(state=tk.NORMAL)
        except Exception:
            pass

        # formatted report similar to example
        report_text = (
            f"Preprocessing Report:\n"
            f"-------------------\n"
            f"Before Cleaning:\n"
            f"- Total transactions: {report.get('original_total', 0)}\n"
            f"- Empty transactions: {report.get('empty_transactions', 0)}\n"
            f"- Single-item transactions: {report.get('single_item_removed', 0)}\n"
            f"- Duplicate items found: {report.get('duplicates_removed', 0)} instances\n"
            f"- Invalid items found: {report.get('invalid_item_transactions', 0)} instances\n"
            f"After Cleaning:\n"
            f"- Valid transactions: {report.get('valid_transactions', 0)}\n"
            f"- Total items: {report.get('total_items', 0)}\n"
            f"- Unique products: {report.get('unique_items', 0)}\n"
        )

        # append memory summary if available
        try:
            peak = report.get('memory_peak_tracemalloc_bytes')
            current = report.get('memory_current_tracemalloc_bytes')
            rss_before = report.get('memory_rss_before_bytes')
            rss_after = report.get('memory_rss_after_bytes')
            rss_delta = report.get('memory_rss_delta_bytes')
            mem_lines = []
            if peak is not None or current is not None:
                def _mb(x):
                    return f"{(x/1024/1024):.2f} MB" if x is not None else "N/A"
                mem_lines.append("Memory (tracemalloc): peak=" + _mb(peak) + ", current=" + _mb(current))
            if rss_before is not None or rss_after is not None:
                def _mbn(x):
                    return f"{(x/1024/1024):.2f} MB" if x is not None else "N/A"
                mem_lines.append("Memory (RSS): before=" + _mbn(rss_before) + ", after=" + _mbn(rss_after) + (", delta=" + _mbn(rss_delta) if rss_delta is not None else ""))
            if mem_lines:
                report_text += "\n\n" + "\n".join(mem_lines)
        except Exception:
            pass

        # show detailed report unless running silently
        if not silent:
            try:
                self._open_preprocessing_report(cleaned, report)
            except Exception:
                # fallback to simple messagebox
                try:
                    messagebox.showinfo("Preprocessing Report", report_text)
                except Exception:
                    self.status_var.set(self.status_var.get() + " (report available)")
        self._update_stats()

    # ---- Stats ----
    def _update_stats(self):
        tx_count = len(self.transactions)
        unique_items = set()
        for t in self.transactions:
            for i in t["items"]:
                try:
                    unique_items.add(i.lower())
                except Exception:
                    unique_items.add(str(i))
        self.stats_var.set(f"Transactions: {tx_count} | Unique items: {len(unique_items)}")

    # convenience for tests
    def get_transactions(self):
        return list(self.transactions)
    
    def _view_last_report(self):
        """Open the last preprocessing report window without re-running preprocessing."""
        report = getattr(self, 'last_report', None)
        cleaned = getattr(self, 'last_cleaned', None)
        if not report or cleaned is None:
            messagebox.showinfo("Preprocessing Report", "No preprocessing report available. Run 'Preprocess' first.")
            return
        try:
            self._open_preprocessing_report(cleaned, report)
        except Exception as e:
            messagebox.showerror("Report Error", f"Could not open report: {e}")

    def _open_preprocessing_report(self, cleaned, report: dict):
        """Open a Toplevel window displaying the preprocessing report plus before/after data.

        cleaned: pandas DataFrame where 'items' column is a list of cleaned items.
        report: dict with statistics produced by clean_data.
        """
        win = tk.Toplevel(self)
        win.title("Preprocessing Report")
        win.geometry("900x560")

        # Top: summary text
        summary = (
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
            f"- Unique products: {report.get('unique_items', 0)}\n"
        )

        # Append memory diagnostics to the summary if available in the report
        try:
            mem_lines = []
            peak = report.get('memory_peak_tracemalloc_bytes')
            current = report.get('memory_current_tracemalloc_bytes')
            rss_before = report.get('memory_rss_before_bytes')
            rss_after = report.get('memory_rss_after_bytes')
            rss_delta = report.get('memory_rss_delta_bytes')

            def _mb(x):
                return f"{(x/1024/1024):.2f} MB" if x is not None else "N/A"

            if peak is not None or current is not None:
                mem_lines.append("Memory (tracemalloc): peak=" + _mb(peak) + ", current=" + _mb(current))
            if rss_before is not None or rss_after is not None:
                mem_lines.append("Memory (RSS): before=" + _mb(rss_before) + ", after=" + _mb(rss_after) + (", delta=" + _mb(rss_delta) if rss_delta is not None else ""))

            if mem_lines:
                summary = summary + "\n" + "\n".join(mem_lines) + "\n"
        except Exception:
            pass

        txt = tk.Text(win, height=8, wrap=tk.NONE)
        txt.insert("1.0", summary)
        txt.config(state=tk.DISABLED)
        txt.pack(fill=tk.X, padx=6, pady=6)

        # Middle: two panes for before/after
        panes = tk.PanedWindow(win, orient=tk.HORIZONTAL)
        panes.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Left: raw transactions
        left_frame = tk.LabelFrame(panes, text="Before (Raw)")
        left_tree = ttk.Treeview(left_frame, columns=("tid", "items"), show="headings")
        left_tree.heading("tid", text="ID")
        left_tree.heading("items", text="Items")
        left_tree.column("tid", width=60, anchor="center")
        left_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        left_scroll = ttk.Scrollbar(left_frame, orient="vertical", command=left_tree.yview)
        left_tree.configure(yscrollcommand=left_scroll.set)
        left_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # populate raw
        for t in self.transactions:
            left_tree.insert("", "end", values=(t.get("transaction_id"), ", ".join(t.get("items", []))))

        panes.add(left_frame)

        # Right: cleaned transactions
        right_frame = tk.LabelFrame(panes, text="After (Cleaned)")
        right_tree = ttk.Treeview(right_frame, columns=("tid", "items"), show="headings")
        right_tree.heading("tid", text="ID")
        right_tree.heading("items", text="Items")
        right_tree.column("tid", width=60, anchor="center")
        right_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right_scroll = ttk.Scrollbar(right_frame, orient="vertical", command=right_tree.yview)
        right_tree.configure(yscrollcommand=right_scroll.set)
        right_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # populate cleaned: cleaned may be a DataFrame
        try:
            for _, row in cleaned.iterrows():
                tid = row.get("transaction_id", "")
                items = row.get("items", [])
                display = ", ".join(items) if isinstance(items, (list, tuple)) else str(items)
                right_tree.insert("", "end", values=(tid, display))
        except Exception:
            # fallback if cleaned is simple iterable
            try:
                for row in cleaned:
                    right_tree.insert("", "end", values=(row.get("transaction_id", ""), ", ".join(row.get("items", []))))
            except Exception:
                pass

        panes.add(right_frame)

        # Bottom: actions
        btn_frame = tk.Frame(win)
        btn_frame.pack(fill=tk.X, padx=6, pady=6)

        def _export_report():
            from datetime import datetime
            base = Path(__file__).resolve().parents[2]
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_path = base / f"preprocess_raw_{ts}.csv"
            clean_path = base / f"preprocess_cleaned_{ts}.csv"
            try:
                # write raw
                with open(raw_path, "w", newline="", encoding="utf-8") as fh:
                    writer = csv.writer(fh)
                    writer.writerow(["transaction_id", "items"])
                    for t in self.transactions:
                        writer.writerow([t.get("transaction_id"), ", ".join(t.get("items", []))])
                # write cleaned (assume pandas)
                try:
                    cleaned.to_csv(clean_path, index=False)
                except Exception:
                    # fallback: write rows
                    with open(clean_path, "w", newline="", encoding="utf-8") as fh:
                        writer = csv.writer(fh)
                        writer.writerow(["transaction_id", "items"])
                        try:
                            for _, row in cleaned.iterrows():
                                items = row.get("items", [])
                                display = ", ".join(items) if isinstance(items, (list, tuple)) else str(items)
                                writer.writerow([row.get("transaction_id"), display])
                        except Exception:
                            pass

                messagebox.showinfo("Exported", f"Report exported:\n{raw_path}\n{clean_path}")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Could not export report: {e}")

        ttk.Button(btn_frame, text="Export Report (CSV)", command=_export_report).pack(side=tk.RIGHT)
