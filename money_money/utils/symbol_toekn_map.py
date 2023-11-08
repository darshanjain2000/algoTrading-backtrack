import requests
import json

# Define the URL
url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON data
    data = json.loads(response.text)

    # Create a dictionary to store the symbol and token mapping
    symbol_token_map = {}

    # Iterate through the data and extract the token and symbol
    for item in data:
        token = item.get("token")
        symbol = item.get("symbol")
        if token and symbol:
            symbol_token_map[symbol] = token

    # Print the symbol and token mapping
    print(symbol_token_map)

else:
    print("Failed to retrieve data from the URL")