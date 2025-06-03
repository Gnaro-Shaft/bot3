from typing import Tuple
import pandas as pd
from utils.logger import setup_logger

logger = setup_logger("DecisionEngine")

class DecisionEngine:
    def __init__(self, rsi_period=14, score_threshold=60):
        self.rsi_period = rsi_period
        self.score_threshold = score_threshold
        self.df = pd.DataFrame()

    def update(self, new_candle: dict):
        """Ajoute une bougie et maintient un historique limité."""
        self.df = pd.concat([self.df, pd.DataFrame([new_candle])], ignore_index=True)
        self.df = self.df.tail(100)  # Garde les 100 dernières bougies

    def compute_rsi(self):
        if len(self.df) < self.rsi_period + 1:
            self.df["rsi"] = 50  # Valeur neutre par défaut si pas assez de données
            return

        delta = self.df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(self.rsi_period, min_periods=1).mean()
        avg_loss = loss.rolling(self.rsi_period, min_periods=1).mean()

        rs = avg_gain / (avg_loss + 1e-9)  # éviter la division par zéro
        rsi = 100 - (100 / (1 + rs))
        self.df["rsi"] = rsi

    def compute_score(self):
        """Retourne un score positif pour achat, négatif pour vente."""
        if len(self.df) < self.rsi_period + 1:
            return 0  # Pas assez de données

        self.compute_rsi()
        latest = self.df.iloc[-1]
        previous = self.df.iloc[-2]
        score = 0

        # ---- Signaux d'achat (score positif) ----
        # Heikin Ashi ou bougies classiques haussières
        if latest["close"] > latest["open"] and previous["close"] > previous["open"]:
            score += 30

        # RSI bas = possible rebond (achat)
        if latest["rsi"] < 35:
            score += 30
        # Bougie verte forte (achat)
        if latest["close"] - latest["open"] > (latest["high"] - latest["low"]) * 0.6:
            score += 20

        # ---- Signaux de vente (score négatif) ----
        # Heikin Ashi ou bougies baissières
        if latest["close"] < latest["open"] and previous["close"] < previous["open"]:
            score -= 30

        # RSI haut = surachat (vente)
        if latest["rsi"] > 65:
            score -= 30
        # Bougie rouge forte (vente)
        if latest["open"] - latest["close"] > (latest["high"] - latest["low"]) * 0.6:
            score -= 20

        # Volume supérieur à la moyenne (appuie la force du mouvement)
        if len(self.df) >= 10:
            avg_vol = self.df["volume"].rolling(10, min_periods=1).mean().iloc[-1]
        else:
            avg_vol = self.df["volume"].mean()
        if latest["volume"] > avg_vol:
            score += 10 if score > 0 else -10  # Accentue le sens dominant

        return score

    def decide(self) -> Tuple[str, int]:
        """
        Retourne une décision ('buy', 'sell', 'hold') et un score associé.
        - buy : score >= seuil
        - sell : score <= -seuil
        - hold : entre les deux
        """
        score = self.compute_score()
        if score >= self.score_threshold:
            logger.debug(f"Signal d'achat détecté | Score={score}")
            return "buy", score
        elif score <= -self.score_threshold:
            logger.debug(f"Signal de vente détecté | Score={score}")
            return "sell", score
        else:
            return "hold", score
