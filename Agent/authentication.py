import os
from dotenv import load_dotenv
import json
import base64
import requests

# Load environment variables from .env file
load_dotenv('../.env')
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")  # Add the client_secret from your Trimble Cloud Console client here

print(client_id)
url = 'https://id.trimble.com/oauth/token'

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic ' + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
}
data = {
    'grant_type': 'client_credentials',
    'scope': 'trimble-assistant-hackathon'
}

response = requests.post(url=url, headers=headers, data=data)

content = response.json()

print(content['access_token'])

with open('authentication.json', 'w', encoding='utf-8') as f:
    json.dump(content, f, indent=4)
