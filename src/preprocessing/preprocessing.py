import pandas as pd;
import numpy as np;


def print_all(data):


products = pd.read_csv('../../data/products.csv')
data = pd.read_csv('../../data/sample_transactions.csv')



print(data.head())
products.head()

print_all(data)

print('Hello World')

