import pandas as pd
import logging
from pathlib import Path
import tracemalloc

try:
    import psutil
except Exception:
    psutil = None

import warnings
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

# ----------------------------------------------------------------------
# SETUP LOGGING
# ----------------------------------------------------------------------
log_dir = Path(__file__).parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "preprocessing.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# FIND products.csv ROBUSTLY
# ----------------------------------------------------------------------
def find_products_csv():
    here = Path(__file__).resolve()
    for parent in [here] + list(here.parents):
        candidate = parent / "data" / "products.csv"
        if candidate.exists():
            return candidate
    return None


try:
    products_path = find_products_csv()
    products = pd.read_csv(products_path) if products_path else pd.DataFrame(columns=["product_name"])
except Exception:
    products = pd.DataFrame(columns=["product_name"])


# ----------------------------------------------------------------------
# UTILITY: PRINT ALL TRANSACTIONS
# ----------------------------------------------------------------------
def print_all(data):
    for _, row in data.iterrows():
        print(f"Transaction ID {row['transaction_id']} Items {row['items']}")


# ----------------------------------------------------------------------
# CLEAN DATA
# ----------------------------------------------------------------------
def clean_data(data, return_report: bool = False):
    """
    Clean transaction DataFrame.
    Returns cleaned DataFrame and, optionally, a report dictionary.
    """

    # Start memory tracking
    try:
        tracemalloc.start()
    except Exception:
        pass

    rss_before = None
    proc = None
    if psutil is not None:
        try:
            proc = psutil.Process()
            rss_before = proc.memory_info().rss
        except Exception:
            rss_before = None

    total = int(data.shape[0])
    logger.info("Before Cleaning")
    logger.info("--------------------------------")
    logger.info(f"Number of transactions: {total}")

    # INITIAL CLEANING
    data = data.copy()
    data["items"] = data["items"].astype(str).str.strip()
    before_dropna = data.shape[0]
    data = data.dropna()
    blank_removed = before_dropna - data.shape[0]

    data["items"] = data["items"].str.lower()

    drop_list = set()
    empty_count = 0
    single_count = 0
    dupes = 0
    bad_items = 0

    # DETECT "(empty)" marker and split items
    for index, row in data.iterrows():
        raw = str(row["items"]).strip()

        if raw == "(empty)":
            empty_count += 1
            drop_list.add(index)
            data.at[index, "items"] = []
            continue

        # Split into list
        data.at[index, "items"] = raw.split(",")

    # STRIP SPACES, REMOVE EMPTY STRINGS, FIND SINGLES/EMPTY
    for index, row in data.iterrows():
        if index in drop_list:
            continue

        cleaned_items = [i.strip() for i in row["items"] if i.strip()]
        data.at[index, "items"] = cleaned_items

        if len(cleaned_items) == 0:
            empty_count += 1
            drop_list.add(index)

        elif len(cleaned_items) == 1:
            single_count += 1
            drop_list.add(index)

    logger.info(f"Empty item transactions: {empty_count}")
    logger.info(f"Single-item transactions: {single_count}")

    # INVALID PRODUCT CHECK
    try:
        valid_products = set(
            products["product_name"].astype(str).str.lower().str.strip().values
        )
    except Exception:
        valid_products = set()

    for index, row in data.iterrows():
        if index in drop_list:
            continue

        for item in row["items"]:
            if item not in valid_products:
                bad_items += 1
                drop_list.add(index)
                break

    logger.info(f"Transactions with invalid items: {bad_items}")

    # REMOVE DUPLICATE ITEMS WITHIN A TRANSACTION
    for index, row in data.iterrows():
        items = row["items"]
        seen = set()
        unique_items = []

        for it in items:
            if it not in seen:
                seen.add(it)
                unique_items.append(it)

        dupes += len(items) - len(unique_items)
        data.at[index, "items"] = unique_items

    logger.info(f"Duplicate items removed: {dupes}")

    # DROP BAD TRANSACTIONS
    if drop_list:
        data = data.drop(list(drop_list))

    # FINAL STATS
    logger.info("")
    logger.info("After Cleaning")
    logger.info("--------------------------------")

    valid_transactions = int(data.shape[0])
    logger.info(f"Valid Transactions: {valid_transactions}")

    all_items = [item for row in data["items"] for item in row]
    item_count = len(all_items)
    unique_count = len(set(all_items))

    logger.info(f"Total Items: {item_count}")
    logger.info(f"Unique Items: {unique_count}")

    # MEMORY REPORT
    try:
        current_alloc, peak_alloc = tracemalloc.get_traced_memory()
    except Exception:
        current_alloc, peak_alloc = 0, 0

    try:
        tracemalloc.stop()
    except Exception:
        pass

    rss_after = None
    rss_delta = None

    if proc is not None:
        try:
            rss_after = proc.memory_info().rss
            if rss_before is not None:
                rss_delta = rss_after - rss_before
        except Exception:
            pass

    report = {
        "original_total": total,
        "blank_removed": blank_removed,
        "empty_transactions": empty_count,
        "single_item_removed": single_count,
        "invalid_item_transactions": bad_items,
        "duplicates_removed": dupes,
        "valid_transactions": valid_transactions,
        "total_items": item_count,
        "unique_items": unique_count,
        "memory_peak_tracemalloc_bytes": peak_alloc,
        "memory_current_tracemalloc_bytes": current_alloc,
        "memory_rss_before_bytes": rss_before,
        "memory_rss_after_bytes": rss_after,
        "memory_rss_delta_bytes": rss_delta,
    }

    return (data, report) if return_report else data
