from itertools import combinations
import pandas as pd


products = pd.read_csv('../../data/products.csv')

#Assotiation Rule Class, -1 means unknown/not calculated
#Try to keep even first and second as lists even if 1 item
class AssociationRule:
    def __init__(self, first, second, data=0, isVertical = False, total = 0):
        
        if isinstance(first, str):
            self.first = {first}
        else:
            self.first = set(first)
        
        if isinstance(second, str):
            self.second = {second}
        else:
            self.second = set(second)
        
        if isVertical == False:
            self.support = support_apiori(data, self)
            self.confidence = confidence_apiori(data, self)
            self.lift = lift_apiori(data, self)
        else:
            self.support = support_eclat(self, data, total)
            self.confidence = confidence_eclat(self, data, total)
            self.lift = lift_eclat(self, data, total)

    def __str__(self):
        return f'{self.first} -> {self.second}'
    
    def __eq__(self, other):
        return self.first == other.first and self.second == other.second
    
    def __hash__(self):
        return hash((frozenset(self.first), frozenset(self.second)))
    
    def __repr__(self):
        return self.__str__()
    
    
    


def confidence_apiori(data, rule: AssociationRule):

    sup_dividend = support_apiori(data, rule)
    sup_divisor = support_apiori(data, rule.first)

    if sup_divisor == 0:
         return 0
    return sup_dividend / sup_divisor


def lift_apiori(data, rule: AssociationRule):


    conf_dividend = confidence_apiori(data, rule)
    sup_divisor = support_apiori(data, rule.second)


    if sup_divisor == 0:
        return 0
    return conf_dividend / sup_divisor
          
#Accepts both rules and itemsets
def support_apiori(data, itemset):
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


def support_eclat(itemset: tuple, found_sets: dict, total: int ) -> float:
    if isinstance(itemset, AssociationRule):
        itemset = tuple(itemset.first | itemset.second)
    else:
        itemset = tuple(itemset)

    itemset = tuple(sorted(itemset))
    dividend = len(found_sets[itemset])
    
    return dividend/total

def confidence_eclat(rule: AssociationRule, found_sets: dict, total: int) -> float:
    dividend = rule.support
    divisor = support_eclat(rule.first, found_sets, total)
    
    if divisor == 0:
        return 0
    else:
        return dividend / divisor

def lift_eclat(rule: AssociationRule, found_sets: dict, total: int) -> float:

    dividend = rule.confidence
    divisor = support_eclat(rule.second, found_sets, total)

    if divisor == 0:
        return 0

    return dividend/divisor




def generate_all_rules_apiori(itemsets, minimum_confidence, data):
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

def generate_all_rules_eclat(minimum_confidence, found_sets, total):
    real_rules = set()
    possible_rules = set()

    for sets in found_sets:
        possible_rules = set()
        if len(sets) == 2:
        
            possible_rules.add(AssociationRule(sets[0], sets[1], isVertical=True, total=total, data=found_sets))
            possible_rules.add(AssociationRule({sets[1]}, {sets[0]}, isVertical=True, total=total, data=found_sets))
        elif len(sets) > 2:
            i = 2
            while i < len(sets):
                for combo in combinations(sets, i):
                    first = set(combo)
                    second = set(sets) - first
                
                    possible_rules.add(AssociationRule(first, second, isVertical=True, total=total, data=found_sets))
                    possible_rules.add(AssociationRule(second, first, isVertical=True, total=total, data=found_sets))
                i+=1

        for rules in possible_rules:
            if rules.confidence >= minimum_confidence:
                real_rules.add(rules)
    
    return real_rules
