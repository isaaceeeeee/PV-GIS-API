# The Meteorological Year
import csv
import requests
import pandas as pd
from io import StringIO
import json

# !! JSON Output !!
base_url = " https://re.jrc.ec.europa.eu/api/tmy?"
params = {
    "lat": 56.01226316057495,  
    "lon": -3.779039941114147,   
    "peakpower": 256,  
    "loss": 5,
    "pvtechchoice": "crystSi",
    "angle": 15,
    "aspect": 76,  
    "outputformat": "json",
    "browser": 0 
}
response = requests.get(base_url, params=params)
if response.status_code == 200:
    data = response.json()  
    print(json.dumps(data, indent=4))  
else:
    print(f"Error: {response.status_code} - {response.text}")

# !! CSV Output !!s
base_url = " https://re.jrc.ec.europa.eu/api/tmy?"
params = {
    "lat": 56.01226316057495,  
    "lon": -3.779039941114147,   
    "peakpower": 215,  
    "loss": 5,
    "pvtechchoice": "crystSi",
    "angle": 15,
    "aspect": 76,  
    "outputformat": "csv",
    "browser": 0 
}
response = requests.get(base_url, params=params)
if response.status_code == 200:
    print("Raw CSV response:")
    print(response.text)
    csv_data = StringIO(response.text)
    try:
        df = pd.read_csv(csv_data)
        print(df)
    except pd.errors.ParserError as e:
        print("Error parsing CSV data:", e)
else:
    print(f"Error: {response.status_code} - {response.text}")
