import pandas as pd
from preprocessing import clean_data
import formulas
from itertools import combinations
import time

products = pd.read_csv('../../data/products.csv')

def apriori(data, minimum_support=0.2, minimum_confidence=0.5):
    start_time = time.time()
    supported_sets = {}
    one_sets = []
    product_list = products['product_name'].tolist()
    found_sets_this_cycle = 0
    n_size = 1

    for item in product_list:
        if formulas.support_apiori(data, item) >= minimum_support:
            one_sets.append(item)
            found_sets_this_cycle +=1

  
    
    if found_sets_this_cycle == 0:
        return -1
    
    supported_sets[n_size] = one_sets
    
    while found_sets_this_cycle != 0:
        found_sets_this_cycle = 0
        n_size+=1
        found_sets = []

        set_candidate = list(combinations(one_sets, n_size))

        for itemset in set_candidate:
            if formulas.support_apiori(data, itemset) >= minimum_support:
                found_sets.append(itemset)
                found_sets_this_cycle+= 1
        
        supported_sets[n_size] = found_sets

        found_items = []

        for sets in found_sets:
            for item in sets:
                found_items.append(item)

        one_sets = list(set(found_items))

 

    ret = formulas.generate_all_rules_apiori(supported_sets, minimum_confidence, data)

    end_time = time.time()
    elapsed_time_ms = (end_time - start_time) * 1000
    print(f'Apiori completed in {elapsed_time_ms} ms')
    return ret




