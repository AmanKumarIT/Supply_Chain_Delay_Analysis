import pickle
import numpy as np
from app.core.config import settings

class DelayPredictor:
    _instance = None

    def __init__(self):
        with open(settings.model_path, "rb") as f:
            self.model = pickle.load(f)

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def predict(self, distance: float, weather: float, traffic: float, congestion: float) -> float:
        features = np.array([[distance, weather, traffic, congestion]])
        return float(self.model.predict(features)[0])

    def risk_score(self, delay: float, max_expected_delay: float = 40.0) -> float:
        """Normalise predicted delay to a 0–1 risk score."""
        return min(delay / max_expected_delay, 1.0)
