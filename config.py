# config.py

import os
from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv()

# 🔑 Clés API Kraken
KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY", "")
if KRAKEN_API_KEY is None:
    raise ValueError("KRAKEN_API_KEY est requis")
KRAKEN_API_SECRET = os.getenv("KRAKEN_API_SECRET")
if KRAKEN_API_SECRET is None:
    raise ValueError("KRAKEN_API_SECRET est requis", "")
BASE_URL = "https://futures.kraken.com/derivatives/api/v3"


# ⚙️ Paramètres de trading
SYMBOL = "PF_ETHUSD"
LEVERAGE = 10
TRADE_CAPITAL_RATIO = 0.3      # Utiliser 30 % du capital dispo
MAX_CAPITAL_RATIO = 0.6        # Ne jamais dépasser 60 %
MIN_USDC_BALANCE = 10          # Alerte si balance < 10 USDC
MIN_ORDER_SIZE = 0.01          # Taille minimale des ordres (à ajuster selon contrat)

# 📊 Websocket / Data
TIMEFRAME = "1m"
OHLC_INTERVAL_SEC = 10         # Intervalle entre deux bougies
USE_HEIKIN_ASHI = True
TP_PCT = os.getenv("TP_PCT", "0.5")  # Take Profit en pourcentage 
SL_PCT = os.getenv("SL_PCT", "0.5")  # Stop Loss en pourcentage

# 💾 MongoDB
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = "kraken_bot"
TRADE_COLLECTION = "trades"

# 📩 Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if TELEGRAM_TOKEN is None:
    raise ValueError("TELEGRAM_TOKEN est requis")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
if TELEGRAM_CHAT_ID is None:
    raise ValueError("TELEGRAM_CHAT_ID est requis")

# ⏱ Fréquence des boucles principales
LOOP_INTERVAL_SEC = 15


DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() in ("true", "1", "yes")
