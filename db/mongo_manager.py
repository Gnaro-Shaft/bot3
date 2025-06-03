# db/mongo_manager.py

from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, TRADE_COLLECTION
from utils.logger import setup_logger

logger = setup_logger("MongoDB")

class MongoManager:
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_URI)
            self.db = self.client[MONGO_DB]
            self.collection = self.db[TRADE_COLLECTION]
            logger.info("Connexion à MongoDB établie.")
        except Exception as e:
            logger.error(f"Erreur de connexion MongoDB : {e}")
            raise

    def save_trade(self, trade_data: dict):
        """Enregistre un trade dans la base de données."""
        try:
            self.collection.insert_one(trade_data)
            logger.debug(f"Trade enregistré : {trade_data}")
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du trade : {e}")

    def get_all_trades(self):
        """Retourne tous les trades enregistrés."""
        try:
            return list(self.collection.find())
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des trades : {e}")
            return []

    def get_trades_by_symbol(self, symbol: str, limit: int = 100):
        """Retourne les derniers trades pour un symbole donné."""
        try:
            return list(self.collection.find({"symbol": symbol}).sort("timestamp", -1).limit(limit))
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des trades pour {symbol} : {e}")
            return []
