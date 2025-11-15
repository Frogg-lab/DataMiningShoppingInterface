from itertools import combinations
import pandas as pd

products = pd.read_csv('../../data/products.csv')

#Assotiation Rule Class, -1 means unknown/not calculated
#Try to keep even first and second as lists even if 1 item
class AssociationRule:
    def __init__(self, first, second, data, isVertical = False):
        self.first = first
        self.second = second
        if isVertical == False:
            self.support = support(data, self)
            self.confidence = confidence(data, self)
            self.lift = lift(data, self)
        else:
            self.support = support_vertical(data, self)
            self.confidence = confidence(data, self, True)
            self.lift = lift(data, self, True)

    def __str__(self):
        return f'{self.first} -> {self.second}\n'
    
    def __eq__(self, other):
        return self.first == other.first and self.second == other.second
    
    def __hash__(self):
        return hash((frozenset(self.first), frozenset(self.second)))
    
    def __repr__(self):
        return self.__str__()
    


def confidence(data, rule: AssociationRule, isVertical=False):
    if isVertical == False:
        sup_dividend = support(data, rule)
        sup_divisor = support(data, rule.first)
    else:
        sup_dividend = support_vertical(data, rule)
        sup_divisor = support_vertical(data, rule.first)

    if sup_divisor == 0:
         return 0
    return sup_dividend / sup_divisor


def lift(data, rule: AssociationRule, isVertical=False):
    conf_dividend = confidence(data, rule)
    if isVertical == False:
        sup_divisor = support(data, rule.second)
    else:
        sup_divisor = support_vertical(data, rule.second)


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

#Use only for vertical sets, rules can go to the other one
def support_vertical(data, itemset):
    transaction_count = set()

    if isinstance(itemset, str):
        itemset = [itemset]

    for index, row in data.iterrows():
        for person in row['Customers']:
            transaction_count.add(person)
    
    total = len(transaction_count)

    itemset = list(itemset)
    customer_list = []
    for items in itemset:
        row = data[data['Item'] == items]
        customer_list.append(set(row.iloc[0]['Customers']))
    
    top = set.intersection(*customer_list)
    return len(top)/total

   
        

    


        


def generate_all_rules(itemsets, minimum_confidence, data, isVertical=False):
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
            if isVertical == False:
                possible_rules.add(AssociationRule({a}, {b}, data))
                possible_rules.add(AssociationRule({b}, {a}, data))
            else:
                possible_rules.add(AssociationRule({a}, {b}, data, True))
                possible_rules.add(AssociationRule({b}, {a}, data, True))

        else:

            
            i = 2

            while i < len(sets):
                for combo in combinations(sets, i):
                    first = set(combo)
                    second = set(sets) - first
                    
                    if isVertical == False:
                        possible_rules.add(AssociationRule(first, second, data))
                        possible_rules.add(AssociationRule(second, first, data))
                    else:
                        possible_rules.add(AssociationRule(first, second, data, True))
                        possible_rules.add(AssociationRule(second, first, data, True))
                
                i+=1
            
        for rules in possible_rules:
            if rules.confidence >= minimum_confidence:
                real_rules.add(rules)
        
    return real_rules
