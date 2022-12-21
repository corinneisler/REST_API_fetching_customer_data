import json
import csv
import sys
import pandas as pd
import re
import requests
from datetime import datetime, timedelta
from pandas.tseries.offsets import BDay
from requests.auth import HTTPBasicAuth
from api_key import user_prod, key_prod # API key is stored in a separate file (api_key.py)

global_url = 'ENTER URL' # Replace placeholder with the actual url

def get_orders(start_date, end_date):
    # Fetch all orders that were paid on the chosen dates
    url = global_url +  '?order__product__status=P' + \
        '&order__product__modified_date__gte=' + str(start_date) + '&order__product__modified_date__lte=' + str(end_date)

    response = requests.get(url, auth=HTTPBasicAuth(user_prod, key_prod))
    data = response.json()
    output = []
    for element in data['results']:
        customer = element['customer'] # For all customer data
        order =  element['order'] # For order id
        product_set = order['product_set'] # For order status, price and date of payment

        for e in product_set:
            status = e['status']
            locked_price = e['locked_price']
            confirmed_price = e['confirmed_price']
            timestamp = e['modified_date']
            date_paid = timestamp[0:10] #Timestamp is a string, not datetime
        id = order['id']
        dict = {'order_id': order['id'], 'first_name': customer['first_name'], 'last_name': customer['last_name'], 'email': customer['email'], \
                'country': customer['country'], 'language': customer['language'], 'status': status, \
                'price_est': locked_price, 'price_conf': confirmed_price, 'date_paid': date_paid}
        output.append(dict)
    return output

today = datetime.today().date()
two_bdays_ago = (today - BDay(2)).date() #Calculate date: 2 business days ago from current date

# User input
start_str = input('Enter start date (yyyy-mm-dd): ') or str(two_bdays_ago) # Default: 2 business days before current date
end_str = input('Enter end date (yyyy-mm-dd): ') or str(two_bdays_ago) # Same default as above

try:
    start = datetime.strptime(start_str,'%Y-%m-%d').date() # Convert string into date
    end_excl = datetime.strptime(end_str,'%Y-%m-%d').date() # End date is exclusive
    day = timedelta(1)
    end = (end_excl + day) # Now end date is inclusive
    print('Start date:', start)
    print('End date:', end_excl) # More intutitive for the user to use end_excl here
except:
    print('Wrong date format! Enter date in format yyyy-mm-dd, please.')
    sys.exit(1)

# Create dataframe from returned list of dictionaries and export to csv
df = pd.DataFrame(get_orders(start, end))
df['full_name']=df[['first_name', 'last_name']].apply(lambda x: re.sub(' +', ' ', ' '.join(x)), axis=1) # TrustPilot requests one name field
df = df[['order_id', 'full_name', 'email', 'country', 'language', 'status', 'price_est', 'price_conf', 'date_paid']] # Select only necessary columns (no first and last name), in correct order
df = df.sort_values(['country', 'language'])
df = df[['order_id', 'full_name', 'email','country', 'language']] # Remove prices from final output and date
outfile = 'customer_data.csv'
df.to_csv(outfile, header=False, index=False)
