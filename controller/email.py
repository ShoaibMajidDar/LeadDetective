import os
from dotenv import load_dotenv
from zerobouncesdk import ZeroBounce

load_dotenv()
api_key = os.getenv("zerobounce_apikey")

def verify_email(email):
    domain_name = email.split("@")[1]
    return True, domain_name
    zero_bounce = ZeroBounce(api_key)
    response = zero_bounce.validate(email)
    return response.status.value == "valid"

