import json
import threading
import time
import websocket
from collections import deque
from utils.logger import setup_logger
from config import SYMBOL, OHLC_INTERVAL_SEC, USE_HEIKIN_ASHI

logger = setup_logger("WebSocket")

class WebSocketClient:
    def __init__(self, symbol: str, on_new_candle_callback):
        self.symbol = symbol
        self.ws = None
        self.running = False
        self.candle_data = deque()
        self.current_candle = None
        self.candle_start_time = None
        self.on_new_candle_callback = on_new_candle_callback
        self.lock = threading.Lock()

    def start(self):
        self.running = True
        self.ws = websocket.WebSocketApp(
            "wss://futures.kraken.com/ws/v1",
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        threading.Thread(target=self.ws.run_forever, daemon=True).start()
        logger.info("WebSocket client démarré.")
        threading.Thread(target=self._candle_loop, daemon=True).start()

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()

    def on_open(self, ws):
        logger.info("Connexion ouverte au WebSocket Kraken.")
        logger.info(f"Abonnement au flux Kraken pour {self.symbol}")
        payload = {
            "event": "subscribe",
            "feed": "trade",
            "product_ids": [self.symbol]
        }
        ws.send(json.dumps(payload))

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
        except Exception as e:
            logger.error(f"[WS] Erreur parsing JSON : {e} | Message : {message}")
            return

        # Events système : info, subscribed, etc.
        if "event" in data:
            #logger.debug(f"[WS RAW EVENT] {data}")
            return

        # Selon le type de flux Kraken :
        if data.get("feed") == "trade_snapshot":
            trades = data.get("trades", [])
        elif data.get("feed") == "trade":
            trades = [data]
        else:
            # Autre type de message
            #logger.debug(f"[WS RAW OTHER] {data}")
            return

        for trade in trades:
            try:
                price = float(trade["price"])
                qty = float(trade["qty"])
                ts = int(trade["time"] // 1000)
                self._update_candle(price, qty, ts)
            except Exception as e:
                logger.error(f"[WS] Erreur parsing trade : {e} | Trade : {trade}")

    def on_error(self, ws, error):
        logger.error(f"WebSocket error : {error}")

    def on_close(self, ws, close_status_code, close_msg):
        logger.warning("Connexion WebSocket fermée.")

    def _update_candle(self, price, volume, timestamp):
        with self.lock:
            if not self.current_candle:
                logger.info(f"[WS] Premier trade reçu - Initialisation bougie à {price}")
                self.current_candle = {
                    "symbol": self.symbol,
                    "timestamp": int(timestamp // OHLC_INTERVAL_SEC * OHLC_INTERVAL_SEC),
                    "open": price,
                    "high": price,
                    "low": price,
                    "close": price,
                    "volume": volume,
                }
                return

            candle_ts = self.current_candle["timestamp"]
            if timestamp < candle_ts + OHLC_INTERVAL_SEC:
                self.current_candle["close"] = price
                self.current_candle["high"] = max(self.current_candle["high"], price)
                self.current_candle["low"] = min(self.current_candle["low"], price)
                self.current_candle["volume"] += volume
                #logger.debug(f"[WS] Mise à jour bougie : {self.current_candle}")
            else:
                finalized = self.current_candle.copy()
                if USE_HEIKIN_ASHI:
                    finalized = self._to_heikin_ashi(finalized)
                self.candle_data.append(finalized)
                logger.info(f"[WS] Bougie finalisée : {finalized}")
                # Envoi du callback pour stockage ou stratégie
                self.on_new_candle_callback(finalized)
                self.current_candle = {
                    "symbol": self.symbol,
                    "timestamp": int(timestamp // OHLC_INTERVAL_SEC * OHLC_INTERVAL_SEC),
                    "open": price,
                    "high": price,
                    "low": price,
                    "close": price,
                    "volume": volume,
                }

    def _candle_loop(self):
        while self.running:
            #logger.debug("[WS] Boucle _candle_loop en cours...")
            time.sleep(OHLC_INTERVAL_SEC + 1)
            with self.lock:
                if self.current_candle:
                    now = int(time.time())
                    if now > self.current_candle["timestamp"] + OHLC_INTERVAL_SEC:
                        finalized = self.current_candle.copy()
                        if USE_HEIKIN_ASHI:
                            finalized = self._to_heikin_ashi(finalized)
                        self.candle_data.append(finalized)
                        logger.info(f"[WS] Bougie générée par timeout : {finalized}")
                        self.on_new_candle_callback(finalized)
                        self.current_candle = None

    def _to_heikin_ashi(self, candle):
        if not self.candle_data:
            ha_open = (candle["open"] + candle["close"]) / 2
        else:
            ha_open = (self.candle_data[-1]["open"] + self.candle_data[-1]["close"]) / 2

        ha_close = (candle["open"] + candle["high"] + candle["low"] + candle["close"]) / 4
        ha_high = max(candle["high"], ha_open, ha_close)
        ha_low = min(candle["low"], ha_open, ha_close)

        return {
            "symbol": candle["symbol"],
            "timestamp": candle["timestamp"],
            "open": ha_open,
            "high": ha_high,
            "low": ha_low,
            "close": ha_close,
            "volume": candle["volume"],
        }
