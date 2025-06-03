from services.websocket_client import WebSocketClient
from strategy.decision_engine import DecisionEngine
from memory.position_manager import PositionManager
from db.mongo_manager import MongoManager
from telegram.notify import TelegramNotifier
from trading.order_executor import OrderExecutor
from config import SYMBOL, TP_PCT, SL_PCT
import logging
import time

# Logger global
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# Composants
engine = DecisionEngine()
position_manager = PositionManager()
mongo = MongoManager()
notifier = TelegramNotifier()
executor = OrderExecutor()

# Paramètres de trade
MIN_GAIN_POUR_CLOTURE = 0.5  # En %
ORDER_SIZE = 0.02            # À adapter à ta gestion du risque

def on_new_candle(candle: dict):
    logging.info(f"📉 Nouvelle bougie : {candle}")
    engine.update(candle)
    action, score = engine.decide()
    logging.info(f"🎯 Action : {action} | Score : {score}")

    position = position_manager.get_position()
    logging.info(f"[DEBUG] Position courante : {position}")

    entry_price = candle["close"]

    if not position:
        # Ouverture position selon signal
        if action == "buy":
            executor.open_long_market(SYMBOL, ORDER_SIZE)
            position_manager.open_position(SYMBOL, "long", entry_price, ORDER_SIZE)
            notifier.send_message(f"💹 *Achat (LONG) ouvert* {SYMBOL}\nPrix: {entry_price}")
            # Place TP/SL à l’ouverture
            if TP_PCT and SL_PCT:
                tp = entry_price * (1 + float(TP_PCT) / 100)
                sl = entry_price * (1 - float(SL_PCT) / 100)
                executor.place_tp_sl_orders("buy", ORDER_SIZE, tp, sl)
        elif action == "sell":
            executor.open_short_market(SYMBOL, ORDER_SIZE)
            position_manager.open_position(SYMBOL, "short", entry_price, ORDER_SIZE)
            notifier.send_message(f"🔻 *Vente (SHORT) ouverte* {SYMBOL}\nPrix: {entry_price}")
            if TP_PCT and SL_PCT:
                tp = entry_price * (1 + float(TP_PCT) / 100)
                sl = entry_price * (1 - float(SL_PCT) / 100)
                executor.place_tp_sl_orders("sell", ORDER_SIZE, tp, sl)

    else:
        # Fermeture position si signal opposé ou gain suffisant
        entry_price = position["entry_price"]
        current_price = candle["close"]
        side = position["side"]
        size = position["size"]

        # Calcul du PnL
        if side == "long":
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
        elif side == "short":
            pnl_pct = ((entry_price - current_price) / entry_price) * 100
        else:
            pnl_pct = 0

        must_close = False
        if side == "long" and action == "sell":
            must_close = True
        elif side == "short" and action == "buy":
            must_close = True
        elif pnl_pct >= MIN_GAIN_POUR_CLOTURE:
            must_close = True

        if must_close:
            executor.close_position_market(SYMBOL, side, size)
            mongo.save_trade({
                "symbol": SYMBOL,
                "side": side,
                "entry_price": entry_price,
                "exit_price": current_price,
                "pnl_percent": round(pnl_pct, 2),
                "timestamp": candle["timestamp"]
            })
            notifier.send_message(
                f"📊 *Trade clôturé* {SYMBOL}\nType: {side.upper()}\nPnL: *{pnl_pct:.2f}%* ✅"
            )
            position_manager.close_position()
            # Ouvre dans l'autre sens si signal fort (pas "hold")
            if action in ["buy", "sell"]:
                time.sleep(1)  # petite pause pour éviter le double-trigger
                if action == "buy":
                    executor.open_long_market(SYMBOL, ORDER_SIZE)
                    position_manager.open_position(SYMBOL, "long", current_price, ORDER_SIZE)
                    notifier.send_message(f"💹 *Achat (LONG) ouvert* {SYMBOL}\nPrix: {current_price}")
                    if TP_PCT and SL_PCT:
                        tp = current_price * (1 + float(TP_PCT) / 100)
                        sl = current_price * (1 - float(SL_PCT) / 100)
                        executor.place_tp_sl_orders("buy", ORDER_SIZE, tp, sl)
                elif action == "sell":
                    executor.open_short_market(SYMBOL, ORDER_SIZE)
                    position_manager.open_position(SYMBOL, "short", current_price, ORDER_SIZE)
                    notifier.send_message(f"🔻 *Vente (SHORT) ouverte* {SYMBOL}\nPrix: {current_price}")
                    if TP_PCT and SL_PCT:
                        tp = current_price * (1 + float(TP_PCT) / 100)
                        sl = current_price * (1 - float(SL_PCT) / 100)
                        executor.place_tp_sl_orders("sell", ORDER_SIZE, tp, sl)

if __name__ == "__main__":
    client = WebSocketClient(SYMBOL, on_new_candle)
    client.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Arrêt manuel détecté.")
        client.stop()
