# 🤖 Kraken Futures Trading Bot

Ce projet est un bot de trading orienté objet, conçu pour fonctionner en mode simulation **ou** en mode réel avec Kraken Futures. Il utilise MongoDB pour la persistance, Telegram pour les notifications, et une architecture évolutive avec WebSocket, stratégie Heikin Ashi et décision automatisée.

---

## 🚀 Structure du projet

```
.
├── main.py                  # Mode réel Kraken (live WebSocket + ordres réels)
├── main_debug.py           # Mode simulation (bougies aléatoires)
├── config.py               # Paramètres globaux + .env
├── db/
│   └── mongo_manager.py    # Connexion et accès MongoDB
├── memory/
│   └── position_manager.py # Sauvegarde de position locale (JSON)
├── services/
│   └── websocket_client.py # Connexion WebSocket Kraken + OHLC
├── strategy/
│   └── decision_engine.py  # Logique de scoring technique
├── telegram/
│   └── notify.py           # Notifications PnL via Telegram
├── trading/
│   └── order_executor.py   # Envoi d'ordres réels Kraken Futures
├── .env                    # Clés API et config sensible (non versionné)
└── requirements.txt        # Dépendances Python
```

---

## 🧪 Mode simulation

```bash
python main_debug.py
```

- Bougies générées toutes les 10s aléatoirement
- Logique de décision activée
- Envoi Telegram simulé à chaque clôture
- Données enregistrées en MongoDB pour analyse

---

## 🔴 Mode réel avec Kraken

```bash
python main.py
```

> ⚠️ Active uniquement si tu as renseigné correctement `.env`

- Connexion au WebSocket Kraken
- Détection de signaux d’achat
- Envoi d’ordres réels avec TP/SL
- PnL envoyé via Telegram

---

## 🔐 Exemple de fichier `.env`

```dotenv
KRAKEN_API_KEY=xxx
KRAKEN_API_SECRET=xxx
MONGO_URI=mongodb://localhost:27017
TELEGRAM_TOKEN=xxx
TELEGRAM_CHAT_ID=123456789
```

---

## 📦 Installation

```bash
pip install -r requirements.txt
```

---

## 📬 Exemple de message Telegram

```
📊 Trade clôturé
PNL : +1.25% ✅
```

---

## ✅ À venir

- Analyse des stratégies gagnantes
- Gestion du risque évoluée
- Interface dashboard (Dash ou Flask)
- Support multi-symboles Kraken

---

> Maintenu par genaro-cedric ✌️
