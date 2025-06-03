# memory/position_manager.py

from datetime import datetime

class PositionManager:
    def __init__(self):
        self.position = None

    def open_position(self, symbol, side, entry_price, size, tp_id=None, sl_id=None):
        self.position = {
            "symbol": symbol,
            "side": side,
            "entry_price": entry_price,
            "size": size,
            "open_time": str(datetime.now()),
            "tp_id": tp_id,
            "sl_id": sl_id,
        }
        logger.info(f"Position ouverte : {self.position}")

    def close_position(self):
        logger.info("Position clôturée localement.")
        self.position = None

    def set_tp_sl(self, tp_id, sl_id):
        if self.position:
            self.position["tp_id"] = tp_id
            self.position["sl_id"] = sl_id

    def get_tp_sl_ids(self):
        if self.position:
            return self.position.get("tp_id"), self.position.get("sl_id")
        return None, None

    def get_position(self):
        return self.position
 