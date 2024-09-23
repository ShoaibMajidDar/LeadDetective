import json
import logging
import os
from dotenv import load_dotenv
import requests
from zerobouncesdk import ZeroBounce

load_dotenv()
api_key = os.getenv("zerobounce_apikey")

def verify_email(email: str):
    try:
        response = requests.get(f"https://emailvalidation.abstractapi.com/v1/?api_key=5222ddf9d74c4621b04415cc005367f0&email={email}")
    except:
        logging.error("emailvalidation abstractapi limit reached")
        return "False"
    
    return float(json.loads(response.content)["quality_score"])>0.0


