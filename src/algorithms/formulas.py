from itertools import combinations
import pandas as pd

products = pd.read_csv('../../data/products.csv')

#Assotiation Rule Class, -1 means unknown/not calculated
#Try to keep even first and second as lists even if 1 item
class AssociationRule:
    def __init__(self, first, second, data):
        self.first = first
        self.second = second
        self.support = support(data, self)
        self.confidence = confidence(data, self)
        self.lift = lift(data, self)

    def __str__(self):
        return f'{self.first} -> {self.second}\n'
    
    def __eq__(self, other):
        return self.first == other.first and self.second == other.second
    
    def __hash__(self):
        return hash((frozenset(self.first), frozenset(self.second)))
    
    def __repr__(self):
        return self.__str__()
    


def confidence(data, rule: AssociationRule):
    sup_dividend = support(data, rule)
    sup_divisor = support(data, rule.first)

    if sup_divisor == 0:
         return 0
    return sup_dividend / sup_divisor


def lift(data, rule: AssociationRule):
    conf_dividend = confidence(data, rule)
    sup_divisor = support(data, rule.second)

    if sup_divisor == 0:
        return 0
    return conf_dividend / sup_divisor
          
#Accepts both rules and itemsets
def support(data, itemset):
    amount = 0
    total = data.shape[0]
    not_found = False

    if isinstance(itemset, AssociationRule):
         itemset = list(itemset.first) + list(itemset.second)
    if isinstance(itemset, str):
        itemset = [itemset]

    for index, row in data.iterrows():
        not_found = False
        for item in itemset:
            if item not in row['items']:
                    not_found = True
                    break
        if not not_found:
            amount += 1
    return amount / total


def generate_all_rules_apriori(itemsets, minimum_confidence, data):
    all_sets = set()
    possible_rules = set()
    real_rules = set()
    itemsets[1] = []

    for sets in itemsets.values():
        for isets in sets:
            all_sets.add(isets)

    for sets in all_sets:
        if len(sets) == 2:

            a, b = tuple(sets)
            possible_rules.add(AssociationRule({a}, {b}, data))
            possible_rules.add(AssociationRule({b}, {a}, data))


        else:

            
            i = 2

            while i < len(sets):
                for combo in combinations(sets, i):
                    first = set(combo)
                    second = set(sets) - first

                    possible_rules.add(AssociationRule(first, second, data))
                    possible_rules.add(AssociationRule(second, first, data))
                
                i+=1
        
    for rules in possible_rules:
        if rules.confidence >= minimum_confidence:
            real_rules.add(rules)
    
    return real_rules

            
    
            


            

            





            


    
