from app.ml.model import DelayPredictor

def predict_delay(distance: float, weather: float, traffic: float, congestion: float) -> dict:
    predictor = DelayPredictor.get()
    delay = predictor.predict(distance, weather, traffic, congestion)
    risk = predictor.risk_score(delay)
    return {
        "predicted_delay_hours": round(delay, 2),
        "risk_score": round(risk, 4)
    }
