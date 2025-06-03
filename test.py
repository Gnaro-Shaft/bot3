import requests
import uuid
import time
import hmac
import base64
import hashlib
import json

API_KEY = 'AiDFo8lR/Su23UpFCo/69r/D9Ow/NcYrLzWhxgTrvi3bbX6VNJ/Ats7/'
API_SECRET = 'ZQpSmpaOEbQQxHwSIWNUhuE2I5cFiAJ+4OT+NcHx/aEQNSZnC5TI8JTyhHHyQuU/wDrmaGzKU3HF9p32cbTnNzhY'
BASE_URL = 'https://futures.kraken.com/derivatives/api/v3'

def get_headers(payload):
    nonce = str(int(time.time() * 1000))
    payload_str = json.dumps(payload)
    message = nonce + payload_str
    signature = hmac.new(
        base64.b64decode(API_SECRET),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    signature_b64 = base64.b64encode(signature).decode()
    return {
        "APIKey": API_KEY,
        "Nonce": nonce,
        "Authent": signature_b64,
        "Content-Type": "application/json"
    }

order = body = {
         "orderType": "post",
         "symbol": "PF_XBTUSD",
         "side": "buy",
         "size": "1",
         "limitPrice": "1",
      }

headers = get_headers(order)
print(f"Payload: {order}")
print(f"Headers: {headers}")
response = requests.post(BASE_URL + "/sendorder", headers=headers, json=order)
print(response.status_code, response.text)
