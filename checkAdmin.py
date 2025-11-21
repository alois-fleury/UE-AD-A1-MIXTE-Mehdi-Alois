import requests
import os
from dotenv import load_dotenv

load_dotenv()

user_service_url = os.getenv("USER_SERVICE_URL","http://127.0.0.1:3203")

def checkAdmin(user_id):
    try:
        resp = requests.get(f"{user_service_url}/users/isadmin/{user_id}?uid={user_id}")
        if resp.status_code == 200:
            return resp.json().get("admin", False)
    except Exception:
        pass
    return False