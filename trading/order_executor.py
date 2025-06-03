import time
import uuid
import requests
import hmac
import base64
import hashlib
import json
from config import KRAKEN_API_KEY, KRAKEN_API_SECRET, SYMBOL, BASE_URL
from utils.logger import setup_logger

logger = setup_logger("OrderExecutor")

class OrderExecutor:
    def __init__(self):
        self.api_key = KRAKEN_API_KEY
        self.api_secret = KRAKEN_API_SECRET
        self.session = requests.Session()
        self.base_url = BASE_URL

    def open_long_market(self, symbol: str, size: float):
        payload = {
            "orderType": "mkt",
            "symbol": symbol,
            "side": "buy",
            "size": float(size),
            "cliOrdId": str(uuid.uuid4())
        }
        self._send_order(payload)

    def open_short_market(self, symbol: str, size: float):
        payload = {
            "orderType": "mkt",
            "symbol": symbol,
            "side": "sell",
            "size": float(size),
            "cliOrdId": str(uuid.uuid4())
        }
        self._send_order(payload)

    def close_position_market(self, symbol: str, side: str, size: float):
        close_side = "sell" if side == "long" else "buy"
        payload = {
            "orderType": "mkt",
            "symbol": symbol,
            "side": close_side,
            "size": float(size),
            "reduceOnly": True,
            "cliOrdId": str(uuid.uuid4())
        }
        self._send_order(payload)

    def _get_auth_headers(self, payload: dict) -> dict:
        nonce = str(int(time.time() * 1000))
        payload_str = json.dumps(payload)
        message = nonce + payload_str
        signature = hmac.new(
            base64.b64decode(self.api_secret),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.b64encode(signature).decode()

        return {
            "APIKey": self.api_key,
            "Nonce": nonce,
            "Authent": signature_b64,
            "Content-Type": "application/json"
        }

    def _send_order(self, payload: dict):
        url = f"{self.base_url}/sendorder"
        headers = self._get_auth_headers(payload)
        logger.info(f"[DEBUG] Payload envoyé à Kraken : {payload}")
        logger.info(f"[DEBUG] Headers envoyés : {headers}")
        try:
            response = self.session.post(url, headers=headers, json=payload)
            logger.info(f"[DEBUG] Réponse Kraken : {response.status_code} - {response.text}")
            data = response.json()
            if isinstance(data, dict) and "error" in data.get("result", "").lower():
                logger.error(f"Erreur ordre : {data}")
            elif "error" in data:
                logger.error(f"Erreur ordre : {data}")
            else:
                logger.info(f"ORDRE ENVOYÉ : {data}")
        except Exception as e:
            logger.error(f"Échec envoi ordre : {e}")
