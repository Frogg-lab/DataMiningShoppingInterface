import pandas as pd;
import numpy as np;

import warnings
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

products = pd.read_csv('../../data/products.csv')

def print_all(data):
    for index, row in data.iterrows():
        print(f'Transaction ID {row["transaction_id"]} Items {row["items"]}')


#returns cleaned data. Not in place so be sure to reassign
def clean_data(data):

    total = data.shape[0]
    singular = 0
    dupes = 0
    bad_items = 0


    print('Before Cleaning')
    print('--------------------------------')
    print(f'Number of transactions: {total}')


    data['items'] = data['items'].str.strip()
    
    data = data.dropna()



    total = total - data.shape[0]
    
    print(f'Number of blank transactions: {total}')

    drop_list = []

    data['items'] = data['items'].str.lower()

    data['items'] = data['items'].str.split(',')

    for index, row in data.iterrows():
        spaced_items = []
        for item in row['items']:
            spaced_items.append(item.strip())  
        data.at[index, 'items'] = spaced_items          

    for index, row in data.iterrows():
        if len(row['items']) == 1:
            singular += 1
            drop_list.append(index)
            continue

    print(f'Number of singular item transactions: {singular}')
        
    for index, row in data.iterrows():
        for item in row['items']:
            if item not in products['product_name'].values:
                bad_items += 1
                drop_list.append(index)

    print(f'Number of transactions with bad items: {bad_items}')

    for index, row in data.iterrows():
        leng = len(row['items'])
        data.at[index, 'items'] = list(set(row['items']))
        if leng != len(data.at[index, 'items']):
            dupes += (leng - len(data.at[index, 'items']))

    print(f'Number of duplicate items: {dupes}')

    data = data.drop(drop_list)


    print()
    print('After Cleaning')
    print('--------------------------------')
    print('Valid Transactions: ', data.shape[0])

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

    return data








