# REST_API_fetching_customer_data

This Python script uses a REST API to fetch customer data from an internal database for C2B payments made on a particular day. While the default is set to two business days before the current date, the script allows for user input regarding the start and end date (including error handling if the date is entered in the wrong format). 

The script pulls the necessary customer data (order id, name, email address, country, language), in JSON format, converts it first into a pandas dataframe and then into a csv file. The data is sorted by country and language of the customers. 
