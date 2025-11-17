import pandas as pd
from preprocessing import clean_data
import formulas
from itertools import combinations
import time
import math
from memory_profiler import memory_usage





def to_vertical(data):

    one_items = set()
    all_rows = data['items'].tolist()
    new_df = pd.DataFrame(columns=['Item', 'Customers'])
    new_df['Customers'] = new_df['Customers'].astype(object)

    for rows in all_rows:
        for items in rows:
            one_items.add(items)

    one_items = sorted(list(one_items))

    new_df = pd.concat([new_df, pd.DataFrame(list(one_items), columns=['Item'])], ignore_index=True)

                

    counter = 0

    for item in one_items:
        bought = []
        for index, row in data.iterrows():
            if item in row['items']:
                bought.append(row['transaction_id'])
                
        
        new_df.at[counter, 'Customers'] = bought
        counter+=1
    
    return new_df


def eclat(data, minimum_support=0.2, minimum_confidence=0.5):
    start_time = time.time()
    data = to_vertical(data)
    supported_sets = {}
    frequent_items = dict()
    transaction_count = set()
    n_size = 1
    found_sets_this_cycle = 1


    for index, row in data.iterrows():
        for person in row['Customers']:
            transaction_count.add(person)
    
    total = len(transaction_count)
    items_list = data['Item'].tolist()

    minimum = math.ceil(total*minimum_support)
    
    for index, rows in data.iterrows():
        cust = rows['Customers']
        if len(cust) > minimum:
            frequent_items[rows['Item']] = set(rows['Customers'])
          


    if len(frequent_items) == 0:
        return -1
    
    supported_sets.update(frequent_items)

    while found_sets_this_cycle != 0:
        n_size+=1
        found_sets_this_cycle = 0
        set_candidate = list(combinations(frequent_items, n_size))
        found_sets = {}

        for itemset in set_candidate:
            set_pool = []
            for item in itemset:
                set_pool.append(frequent_items[item])
            intersects = set.intersection(*set_pool)
            if len(intersects) >= minimum:

                found_sets[itemset] = intersects
                found_sets_this_cycle+=1

        
        if found_sets_this_cycle!= 0:
            found_items = []
            supported_sets.update(found_sets)
            for sets in found_sets:
                for items in sets:
                    found_items.append(items)
            found_items =  list(set(found_items))
   



    normalized_sets = {}
    for k, v in supported_sets.items():
        if isinstance(k, str):
            normalized_sets[(k,)] = v  # wrap single string in a tuple
        else:
            normalized_sets[k] = v

    supported_sets = normalized_sets  # replace the old dictionary

    ret = formulas.generate_all_rules_eclat(minimum_confidence, supported_sets, total)

    end_time = time.time()
    elapsed_time_ms = (end_time - start_time) * 1000
    print(f'Eclat completed in {elapsed_time_ms} ms')
    return ret


