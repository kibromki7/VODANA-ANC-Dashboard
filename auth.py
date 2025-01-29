import json

def load_credentials():
    with open("credentials.json") as f:
        return json.load(f)["users"]

def authenticate(username, password):
    users = load_credentials()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return user
    return None
