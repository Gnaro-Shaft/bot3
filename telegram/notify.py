import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from utils.logger import setup_logger

logger = setup_logger("Telegram")

class TelegramNotifier:
    def __init__(self, token: str | None = TELEGRAM_TOKEN, chat_id: str | None = TELEGRAM_CHAT_ID):
        if not token or not chat_id:
            raise ValueError("Token Telegram ou chat_id manquant")
        self.token: str = token
        self.chat_id: str = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_message(self, message: str, parse_mode: str = "HTML"):
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        try:
            response = requests.post(self.base_url, data=payload)
            if response.status_code != 200:
                logger.warning(f"Erreur Telegram : {response.text}")
            else:
                logger.info("Message Telegram envoyé avec succès.")
        except Exception as e:
            logger.error(f"Erreur envoi Telegram : {e}")
