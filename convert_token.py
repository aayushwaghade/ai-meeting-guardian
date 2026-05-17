import pickle
import json

with open("token.pkl", "rb") as token:
    creds = pickle.load(token)

token_data = {
    "token": creds.token,
    "refresh_token": creds.refresh_token,
    "token_uri": creds.token_uri,
    "client_id": creds.client_id,
    "client_secret": creds.client_secret,
    "scopes": creds.scopes
}

with open("token.json", "w") as f:
    json.dump(token_data, f, indent=4)

print("✅ token.json created successfully!")