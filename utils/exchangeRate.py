import requests
import math


def CNYtoAUDExRate():
    # Set the API endpoint
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    # Set default rate
    ratio = 4.8

    # Send GET request
    response = requests.get(url)
    
    # Check the response status code
    if response.status_code == 200:
        data = response.json()
        
        # Get the rates dictionary
        rates = data['rates']
        
        # Get the CNY and AUD rates
        cny_rate = rates.get('CNY')
        aud_rate = rates.get('AUD')
        
        if cny_rate and aud_rate:
            # Calculate the ratio of CNY to AUD
            ratio = math.ceil(cny_rate / aud_rate * 100) / 100
            # print(f"The CNY to AUD rate ratio is: {ratio}")
    
    return ratio