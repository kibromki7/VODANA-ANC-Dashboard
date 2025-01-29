import requests
import pandas as pd

REDCAP_API_URL = "https://redcap.dhicenter.com:8443/api/"

def fetch_data(api_token):
    payload = {
        "token": api_token,
        "content": "record",
        "format": "json",
        "type": "flat",
        "rawOrLabel": "label",
        "rawOrLabelHeaders": "raw",
        "exportDataAccessGroups": "true"
    }
    response = requests.post(REDCAP_API_URL, data=payload)
    response.raise_for_status()
    data = response.json()
    return pd.DataFrame(data)
