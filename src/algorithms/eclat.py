import pandas as pd
import preprocessing
import formulas
from itertools import combinations

data = pd.read_csv('../../data/sample_transactions.csv')


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






data = preprocessing.clean_data(data)
data = to_vertical(data)
formulas.support_vertical(data, {'bread', 'butter'})
