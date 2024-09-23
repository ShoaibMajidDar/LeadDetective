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
        response = requests.get(f"https://emailvalidation.abstractapi.com/v1/?api_key=d223b20c89d444f1a66fd5f5b411f75e&email={email}")
        return float(json.loads(response.content)["quality_score"])>0.0
    except:
        logging.error("emailvalidation abstractapi limit reached")
        return "False"
    


