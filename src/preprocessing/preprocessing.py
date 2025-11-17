import pandas as pd;
import numpy as np;

import warnings
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

products = pd.read_csv('../../data/products.csv')

def print_all(data):
    for index, row in data.iterrows():
        print(f'Transaction ID {row["transaction_id"]} Items {row["items"]}')


#returns cleaned data. Not in place so be sure to reassign


def clean_data(data, return_report: bool = False):

    total = int(data.shape[0])
    singular = 0
    dupes = 0
    bad_items = 0

    print('Before Cleaning')
    print('--------------------------------')
    print(f'Number of transactions: {total}')

    # trim whitespace and drop empty rows
    data['items'] = data['items'].str.strip()
    before_dropna = data.shape[0]
    data = data.dropna()
    blank_removed = int(before_dropna - data.shape[0])

    # lower-case and split into lists
    data['items'] = data['items'].str.lower()
    data['items'] = data['items'].str.split(',')

    # strip spaces inside each list
    for index, row in data.iterrows():
        spaced_items = []
        for item in row['items']:
            spaced_items.append(item.strip())
        data.at[index, 'items'] = spaced_items

    # detect single-item transactions or empty lists
    drop_list = set()
    for index, row in data.iterrows():
        if not isinstance(row['items'], list) or len(row['items']) == 0:
            singular += 1
            drop_list.add(index)
            continue
        if len(row['items']) == 1:
            singular += 1
            drop_list.add(index)
            continue

    print(f'Number of singular item transactions: {singular}')

    # invalid product detection (compare against products.csv normalized)
    prod_values = set(products['product_name'].astype(str).str.lower().str.strip().values)
    for index, row in data.iterrows():
        for item in row['items']:
            if item not in prod_values:
                bad_items += 1
                drop_list.add(index)

    print(f'Number of transactions with bad items: {bad_items}')

    # remove duplicate items within each transaction while preserving order
    for index, row in data.iterrows():
        leng = len(row['items'])
        seen = set()
        unique_items = []
        for it in row['items']:
            if it not in seen:
                seen.add(it)
                unique_items.append(it)
        data.at[index, 'items'] = unique_items
        if leng != len(unique_items):
            dupes += (leng - len(unique_items))

    print(f'Number of duplicate items: {dupes}')

    # drop flagged transactions
    if drop_list:
        data = data.drop(list(drop_list))

    print()
    print('After Cleaning')
    print('--------------------------------')
    valid_transactions = int(data.shape[0])
    print('Valid Transactions: ', valid_transactions)

    item_count = 0
    for index, row in data.iterrows():
        for item in row['items']:
            item_count += 1

    print('Total Items: ', item_count)

    unique_items = []
    for index, row in data.iterrows():
        for item in row['items']:
            unique_items.append(item)

    unique_items = set(unique_items)
    print('Unique Items: ', len(unique_items))
    print()

    report = {
        'original_total': total,
        'blank_removed': blank_removed,
        'single_item_removed': int(singular),
        'invalid_item_transactions': int(bad_items),
        'duplicates_removed': int(dupes),
        'valid_transactions': valid_transactions,
        'total_items': int(item_count),
        'unique_items': int(len(unique_items)),
    }

    if return_report:
        return data, report
    return data








