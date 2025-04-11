import jwt
import datetime
from app.settings import API_BASE_URL

import requests

SECRET_KEY = "super_secret_key"

def authenticate_user(username, password):

    endPoint = f"{API_BASE_URL}/login"
    headers = {"accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
   
    payload = {"grant_type": "", "username": username, "password": password, "scope": "", "client_id": "", "client_secret": ""}

    rq = requests.post(endPoint, headers=headers, data=payload)
   
    if rq.status_code == 200:
        return rq.json()["access_token"]
    
    return None

def generate_token(username):
    """Generate session token"""
    payload = {"user": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
