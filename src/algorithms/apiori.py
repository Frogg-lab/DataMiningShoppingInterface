import pandas as pd
import preprocessing
import formulas
from itertools import combinations

products = pd.read_csv('../../data/products.csv')

def apriori(data, minimum_support=0.2, minimum_confidence=0.5):
    found_rules = {}
    supported_sets = {}
    one_sets = []
    product_list = products['product_name'].tolist()
    found_sets_this_cycle = 0
    n_size = 1

    for item in product_list:
        if formulas.support(data, item) >= minimum_support:
            one_sets.append(item)
            found_sets_this_cycle +=1

  
    
    if found_sets_this_cycle == 0:
        return found_rules
    
    supported_sets[n_size] = one_sets
    
    while found_sets_this_cycle != 0:
        found_sets_this_cycle = 0
        n_size+=1
        found_sets = []

        set_candidate = list(combinations(one_sets, n_size))

        for itemset in set_candidate:
            if formulas.support(data, itemset) >= minimum_support:
                found_sets.append(itemset)
                found_sets_this_cycle+= 1
        
        supported_sets[n_size] = found_sets

        found_items = []

        for sets in found_sets:
            for item in sets:
                found_items.append(item)

        one_sets = list(set(found_items))


    return formulas.generate_all_rules_apriori(supported_sets, minimum_confidence, data)




    








        

         
